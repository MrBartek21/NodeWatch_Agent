import os
import time
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import docker
import psutil
import socket
import requests
from flask import Flask, request, jsonify

load_dotenv()

CENTRAL_URL = os.getenv("CENTRAL_URL")
API_KEY = os.getenv("API_KEY")
AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME")
NODE_TYPE = os.getenv("AGENT_TYPE", "Docker Host")
INTERVAL = int(os.getenv("UPDATE_INTERVAL", 10))
HOST_TYPE = os.getenv("HOST_TYPE")

client = docker.from_env()
app = Flask(__name__)



# --- Funkcje pomocnicze ---
def get_host_status():
    # CPU, RAM, dysk, uptime
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    uptime = int(time.time() - psutil.boot_time())

    # IP hosta (pierwszy interfejs nie loopback)
    ip = None
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip.startswith("127."):
            # w sieci lokalnej
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
    except:
        ip = "n/a"

    # wersja Dockera
    try:
        docker_version = subprocess.check_output(["docker", "--version"], text=True).strip()
    except:
        docker_version = "n/a"

    # temperatura CPU
    temp = None
    if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
        try:
            temp = int(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
        except:
            temp = None
    else:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    temp = entries[0].current
                    break

    return {
        "cpu_percent": cpu,
        "memory_percent": mem,
        "disk_percent": disk,
        "uptime": uptime,
        "ip": ip,
        "docker_version": docker_version,
        "cpu_temp": temp
    }

def get_all_containers():
    containers = []
    for c in client.containers.list(all=True):
        info = c.attrs
        network = info['NetworkSettings']['Networks']
        ip_addresses = [v['IPAddress'] for v in network.values()] if network else []

        # obsługa portów
        ports_list = []
        ports_dict = info['NetworkSettings'].get('Ports') or {}
        for container_port, host_bindings in ports_dict.items():
            if host_bindings:  # lista mappingów hosta
                for mapping in host_bindings:
                    host_port = mapping.get('HostPort')
                    container_port_num = container_port.split("/")[0]  # np. '80/tcp' -> 80
                    ports_list.append(f"{host_port}->{container_port_num}")
            else:
                # expose, ale brak host mapping
                ports_list.append(container_port)

        # obsługa voluminów
        volumes_list = [m['Source'] for m in info.get('Mounts', [])]

        # obsługa czasu utworzenia
        created_time = info.get('Created')
        try:
            created_time = datetime.fromisoformat(created_time.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        except:
            created_time = created_time

        containers.append({
            "name": c.name,
            "status": c.status,
            "health": info['State'].get('Health', {}).get('Status', 'none'),
            "created": created_time,
            "ip_addresses": ip_addresses,
            "ports": ports_list,
            "volumes": volumes_list
        })
    return containers

def get_network_hostname():
    """Zwraca nazwę hosta w sieci lokalnej lub IP, jeśli nazwa niedostępna"""
    try:
        # Spróbuj pobrać nazwę hosta sieciowego
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()  # pełna nazwa DNS
        if fqdn and fqdn != "localhost":
            return fqdn

        # Spróbuj uzyskać IP z interfejsu
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "n/a"

# --- Wysyłanie statusu do centralnego serwera ---
def send_update():
    data = {
        "hostname": get_network_hostname(),  # hostname w sieci lokalnej
        "agent_hostname": AGENT_HOSTNAME,    # stała nazwa agenta
        "host_type": HOST_TYPE,    # game server/dev server/services
        "type": NODE_TYPE,
        "host_status": get_host_status(),
        "containers": get_all_containers()
    }
    try:
        res = requests.post(CENTRAL_URL, json=data, headers={"X-API-KEY": API_KEY}, timeout=5)
        if res.status_code != 200:
            print("Central update error:", res.text)
    except Exception as e:
        print("Send error:", e)



def start_container(name):
    try:
        c = client.containers.get(name)
        c.start()
        return True
    except Exception as e:
        print("Start error:", e)
        return False

def stop_container(name):
    try:
        c = client.containers.get(name)
        c.stop()
        return True
    except Exception as e:
        print("Stop error:", e)
        return False

def restart_container(name):
    try:
        c = client.containers.get(name)
        c.restart()
        return True
    except Exception as e:
        print("Restart error:", e)
        return False

def execute_docker_compose(compose_content):
    try:
        temp_file = "/tmp/docker-compose-temp.yml"
        with open(temp_file, "w") as f:
            f.write(compose_content)
        subprocess.run(["docker-compose", "-f", temp_file, "up", "-d"], check=True)
        os.remove(temp_file)
        return True
    except Exception as e:
        print("Compose error:", e)
        return False


# --- API dla frontendu ---
@app.route("/api/container_action", methods=["POST"])
def api_container_action():
    data = request.json
    hostname = data.get("hostname")
    container_name = data.get("container_name")
    action = data.get("action")
    if not container_name or not action:
        return jsonify({"error": "Brak nazwy kontenera lub akcji"}), 400

    result = False
    if action == "start":
        result = start_container(container_name)
    elif action == "stop":
        result = stop_container(container_name)
    elif action == "restart":
        result = restart_container(container_name)
    else:
        return jsonify({"error": "Nieznana akcja"}), 400

    if result:
        return jsonify({"message": f"Kontener {container_name} został {action}ed"})
    else:
        return jsonify({"error": f"Błąd podczas {action} kontenera {container_name}"}), 500

@app.route("/api/compose_execute", methods=["POST"])
def api_compose_execute():
    data = request.json
    hostname = data.get("hostname")
    compose = data.get("compose")
    if not compose:
        return jsonify({"error": "Brak treści docker-compose"}), 400

    result = execute_docker_compose(compose)
    if result:
        return jsonify({"message": "Docker Compose wykonany pomyślnie"})
    else:
        return jsonify({"error": "Błąd podczas wykonywania Docker Compose"}), 500
    

# --- Uruchamianie agenta ---
if __name__ == "__main__":
    from threading import Thread
    # Wątek do wysyłania statusu
    def status_loop():
        while True:
            send_update()
            time.sleep(INTERVAL)
    Thread(target=status_loop, daemon=True).start()
    # Start Flask
    app.run(host="0.0.0.0", port=5000)