# 🧠 NodeWatch Agent

[![Docker Pulls](https://img.shields.io/docker/pulls/mrbartek21/nodewatch_agent?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/mrbartek21/nodewatch_agent)  
[![Docker Image Size](https://img.shields.io/docker/image-size/mrbartek21/nodewatch_agent/amd64_v5?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/r/mrbartek21/nodewatch_agent)  
[![Docker Version](https://img.shields.io/badge/version-amd64__v5-blue?style=for-the-badge)](https://hub.docker.com/r/mrbartek21/nodewatch_agent)  
[![Build Status](https://img.shields.io/github/actions/workflow/status/mrbartek21/nodewatch_agent/docker-image-ci.yml?style=for-the-badge&logo=github)](https://github.com/mrbartek21/nodewatch_agent/actions)

---

**NodeWatch Agent** to lekki kontener zaprojektowany do komunikacji z centralnym systemem **NodeWatch**, umożliwiający monitorowanie, raportowanie oraz zdalne zarządzanie hostami (np. serwerami Docker) z poziomu panelu centralnego.

Agent automatycznie zbiera dane o stanie kontenerów, zasobach systemowych oraz konfiguracjach hosta, a następnie przesyła je do centralnego API w regularnych odstępach czasu.

---

## 🚀 Szybki start

**Przykładowy plik `docker-compose.yml`:**

```yaml
version: "3.9"
services:
  agent:
    image: mrbartek21/nodewatch_agent:amd64_v5
    container_name: agent
    restart: unless-stopped
    network_mode: "host"
    environment:
      CENTRAL_URL: "https://agent.pacynait.pl/api/update"
      API_KEY: "TwojSekretnyKlucz"
      AGENT_HOSTNAME: "srv03"
      AGENT_TYPE: "Docker Host"
      HOST_TYPE: "Dev"
      UPDATE_INTERVAL: "10"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./docker-compose:/app/docker-compose

```

**Uruchom agenta poleceniem:**

```bash
docker compose up -d
```

## ⚙️ Zmienne środowiskowe

| Nazwa | Opis | Wymagane | Przykład |
|:------|:------|:-----------:|:-----------|
| **CENTRAL_URL** | Adres API serwera centralnego, z którym agent się komunikuje | ✅ | `https://agent.pacynait.pl/api/update` |
| **API_KEY** | Klucz API do autoryzacji komunikacji z centralą | ✅ | `superSekretnyToken123` |
| **AGENT_HOSTNAME** | Unikalna nazwa hosta w systemie centralnym | ✅ | `srv03` |
| **AGENT_TYPE** | Typ agenta (np. *Docker Host*, *Sensor Node*) | ✅ | `Docker Host` |
| **HOST_TYPE** | Typ środowiska (np. produkcja, test, dev) | ✅ | `Dev` |
| **UPDATE_INTERVAL** | Częstotliwość aktualizacji danych (sekundy) | ❌ | `10` |

---

## 🐳 Wymagane uprawnienia

Aby agent mógł monitorować kontenery Dockera, musi mieć dostęp do socketu:

```yaml
- /var/run/docker.sock:/var/run/docker.sock
```

Dodatkowo katalog:

```yaml
- ./docker-compose:/app/docker-compose
```

może zawierać lokalne pliki konfiguracyjne lub dane wspierające działanie agenta.

## 📡 Jak to działa

- Agent nawiązuje połączenie z serwerem centralnym przy użyciu `CENTRAL_URL` i `API_KEY`.  
- Wysyła cyklicznie informacje o stanie kontenerów i systemu.  
- Odbiera ewentualne polecenia zarządzania lub aktualizacje konfiguracji.  
- Każdy host posiada własny unikalny identyfikator `AGENT_HOSTNAME`.  

---

## 🧰 Architektura i wymagania

- **Język:** Python / Node.js (w zależności od wersji backendu)  
- **Komunikacja:** HTTPS (REST API)  
- **Systemy:** Linux, Debian, Ubuntu, Raspberry Pi OS, Alpine  
- **Tryb pracy:** Headless (brak interfejsu graficznego)  

---

## 🔄 Aktualizacje i wersjonowanie

Wersje obrazu publikowane są w formacie:  

mrbartek21/nodewatch_agent:<arch>_v<wersja>


Przykłady:  
- `mrbartek21/nodewatch_agent:amd64_v5`  
- `mrbartek21/nodewatch_agent:arm64_v5`  

Aktualizację możesz wykonać jednym poleceniem:  
```bash
docker compose pull && docker compose up -d
```

## 🧩 Integracja z systemem NodeWatch

Agent jest częścią ekosystemu **NodeWatch**, który umożliwia:

- Zarządzanie wieloma hostami z jednego miejsca
- Monitorowanie statusów kontenerów i serwerów
- Automatyczne aktualizacje i restart usług
- Analizę logów i zdarzeń w czasie rzeczywistym

Więcej informacji: [https://agent.pacynait.pl](https://agent.pacynait.pl)

---

## 🧑‍💻 Przykładowe zastosowania

- Monitoring klastrów Docker
- Zdalne zarządzanie serwerami developerskimi
- Integracja z centralnym panelem administracyjnym
- Automatyzacja procesów DevOps

---

## 🧾 Licencja

Projekt **NodeWatch Agent** jest dostępny na zasadach licencji **MIT**.  
Możesz go dowolnie wykorzystywać, modyfikować i wdrażać w swoich systemach.