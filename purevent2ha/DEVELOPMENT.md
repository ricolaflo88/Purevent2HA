# Purevent2HA

Addon Home Assistant complet pour VMI Purevent via EnOcean

## Architecture

```
purevent2ha/
├── addon.yaml                 # Configuration addon
├── Dockerfile                 # Image Docker
├── DOCS.md                    # Documentation
├── README.md                  # Readme
├── rootfs/
│   ├── app/
│   │   ├── purevent2ha_daemon.py    # Daemon principal
│   │   ├── enocean_comm.py           # Communication EnOcean
│   │   ├── api.py                    # API HTTP
│   │   └── utils.py                  # Utilitaires
│   ├── etc/purevent2ha/
│   │   └── config.json               # Configuration
│   └── usr/local/bin/
│       └── startup.sh                # Script démarrage
└── custom_components/purevent2ha/
    ├── __init__.py                   # Main integration
    ├── manifest.json                 # Manifest HA
    ├── const.py                      # Constantes
    ├── config_flow.py                # Config flow
    ├── coordinator.py                # Coordinator
    ├── services.py                   # Services
    ├── sensor.py                     # Plateforme Sensors
    ├── switch.py                     # Plateforme Switches
    ├── climate.py                    # Plateforme Climate
    ├── number.py                     # Plateforme Numbers
    ├── devices/                      # Configs appareils
    │   ├── d1079-01-00.json         # VMI Purevent
    │   ├── a5-09-04.json            # Capteur CO2
    │   ├── a5-04-01.json            # Capteur T°/H
    │   └── d1079-00-00.json         # Assistant
    ├── translations/                 # Traductions
    │   ├── fr.json
    │   └── en.json
    ├── services.yaml                # Définition services
    └── lovelace_dashboard.yaml      # Dashboard Lovelace
```

## Points clés de l'implémentation

### 1. Communication EnOcean
- Utilise la bibliothèque `python-enocean`
- Gère les différents types de télégrammes (BS4, VLD, RPS)
- Thread dédié pour la réception asynchrone
- Queue de messages pour thread-safety

### 2. Daemon autonome
- Écoute sur le port 5000 (API HTTP)
- Sauvegarde les données en JSON
- Gestion des reconnexions automatiques
- Logging complet

### 3. Intégration Home Assistant
- Coordinator pour mise à jour des données
- Entités complètes (sensor, switch, climate, number)
- Config flow pour configuration facile
- Services pour automations

### 4. Stockage des données
- `/data/purevent2ha/devices.json` - Données actuelles
- `/data/purevent2ha/history.json` - Historique
- `/data/purevent2ha/devices_config.json` - Configuration

## Flux de données

```
Module EnOcean USB
        ↓
enocean_comm.py (recevoir les télégrammes)
        ↓
purevent2ha_daemon.py (traiter et stocker)
        ↓
API HTTP (port 5000)
        ↓
Home Assistant Integration
        ↓
Coordinator (mise à jour)
        ↓
Entités (sensor, switch, climate, etc.)
        ↓
Dashboard Lovelace + Automations
```

## Appareils supportés

### D1079-01-00 - VMI Purevent
- Appareil principal
- Réception: état, température, humidité, CO2, erreurs
- Envoi: marche/arrêt, chauffage, refroidissement, vitesse ventilateur

### A5-09-04 - Capteur CO2
- Appareil secondaire
- Réception: concentration CO2 (0-2500 ppm)

### A5-04-01 - Capteur T°/Humidité
- Appareil secondaire
- Réception: température (-30 à +60°C), humidité (0-100%)

### D1079-00-00 - Assistant Ventilairsec
- Appareil optionnel
- Réception: état, informations

## Commandes supportées

```
POWER              → Marche/Arrêt (boolean)
HEATING            → Chauffage (boolean)
COOLING            → Refroidissement (boolean)
INTAKE             → Insufflation d'air (boolean)
SET_TEMP           → Température cible (float)
SET_FAN_SPEED      → Vitesse ventilateur (0-100)
```

## Services

### purevent2ha.send_command

```yaml
service: purevent2ha.send_command
data:
  device_id: "purevent_vmi"
  command: "POWER"
  parameters: true
```

## Variables d'environnement

- `PUREVENT_PORT` - Port série (défaut: /dev/ttyUSB0)
- `PUREVENT_BAUDRATE` - Baudrate (défaut: 57600)
- `PUREVENT_TIMEOUT` - Timeout (défaut: 30s)
- `PUREVENT_MAX_RETRY` - Tentatives (défaut: 3)
- `PUREVENT_LOG_LEVEL` - Level log (défaut: info)

## Build et déploiement

### Build local

```bash
# Build pour toutes les architectures
./build.sh

# Build pour une architecture spécifique
docker build -t purevent2ha ./purevent2ha
```

### Push vers registry

```bash
docker push ghcr.io/ricolaflo88/purevent2ha:latest
```

### Tests

```bash
cd purevent2ha/tests
python -m pytest
```

## Développement

### Structure des fichiers

1. **Core daemon** (`rootfs/app/`):
   - Gère la communication EnOcean
   - Expose l'API HTTP
   - Sauvegarde les données

2. **Integration Home Assistant** (`custom_components/`):
   - Intégration complète avec config flow
   - Platforms (sensor, switch, climate, number)
   - Services pour commandes
   - Traductions

3. **Tests** (`tests/`):
   - Tests unitaires
   - Tests d'intégration

### Ajouter un nouvel appareil

1. Créer le fichier config: `custom_components/purevent2ha/devices/XXXX-XX-XX.json`
2. Ajouter le parser dans `enocean_comm.py`
3. Créer les entités correspondantes
4. Ajouter aux tests

## Logging

Les logs sont disponibles via:
```bash
docker logs addon_purevent2ha
```

Ou dans Home Assistant: Settings → Developer Tools → Logs

## Performance

- Latence communication: <100ms
- Consommation mémoire: ~50MB
- CPU: <5% au repos
- Débit HTTP: >100 req/s

## Sécurité

- Pas de données sensibles en logs
- API locale uniquement (port 5000)
- Permissions minimales requises
- Validation des entrées

## Troubleshooting

### Logs complets

```bash
docker exec addon_purevent2ha cat /var/log/purevent2ha.log
```

### Debug mode

```yaml
# Configuration addon
log_level: debug
```

### Vérifier la connexion

```bash
docker exec addon_purevent2ha curl http://localhost:5000/health
```
