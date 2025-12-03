# Guide d'installation Purevent2HA

## Prérequis

- Home Assistant ≥ 2024.1.0
- Module USB EnOcean (TCM310, RPI-HF, etc.)
- VMI Purevent configurée avec EnOcean
- Port série disponible (Linux/macOS/Windows)

## Installation rapide

### 1. Ajouter le repository

Settings → Developer tools → Terminal (ou SSH)

```bash
# Ajouter le repository
# Allez dans: Settings → Add-ons → Create addon repository
# Et entrez: https://github.com/ricolaflo88/Purevent2HA
```

Ou via YAML:

```bash
# SSH/Terminal
nano /etc/homeassistant/add-ons.json
```

Ajouter:
```json
{
  "repositories": [
    "https://github.com/ricolaflo88/Purevent2HA"
  ]
}
```

### 2. Installer l'addon

1. Settings → Add-ons
2. Chercher "Purevent2HA"
3. Cliquer "Install"
4. Attendre l'installation

### 3. Configurer l'addon

1. Dans la page de l'addon, cliquer "Configuration"
2. Remplir les paramètres:
   - **Port**: Déterminer le port USB (voir ci-dessous)
   - **Baudrate**: 57600 (défaut)
   - **Timeout**: 30s (défaut)
   - **Log Level**: info (défaut)
3. Cliquer "Save"

### 4. Démarrer l'addon

1. Cliquer "Start"
2. Vérifier dans les logs que tout fonctionne
3. Attendre ~30s

### 5. Configurer dans Home Assistant

1. Settings → Devices & Services → Integrations
2. Chercher "Purevent2HA"
3. Si détecté automatiquement, cliquer "Configure"
4. Sinon, créer manuellement avec "Create Integration"

## Déterminer le port USB

### Linux

```bash
# Liste tous les ports série
ls -la /dev/tty*

# Identifier le module EnOcean
dmesg | grep -i usb | tail -20

# Vérifier les permissions
sudo chmod 666 /dev/ttyUSB0  # adapter le numéro
```

Ports courants:
- `/dev/ttyUSB0` - Premier module USB
- `/dev/ttyUSB1` - Deuxième module USB
- `/dev/ttyACM0` - Arduino/STM32
- `/dev/ttyAMA0` - UART Raspberry Pi
- `/dev/ttyS0` - Port série intégré

### macOS

```bash
# Liste les ports
ls -la /dev/tty.usb*

# Identifier le module
ioreg -p IOUSB | grep -A 5 "EnOcean"
```

Ports courants:
- `/dev/tty.usbserial-*` - Module USB EnOcean

### Windows

Via Device Manager:
1. Ouvrir Device Manager (devmgmt.msc)
2. Chercher "COM" sous "Ports"
3. Note le numéro (ex: COM5)
4. Dans l'addon, entrer: `COM5`

## Vérifier la configuration

### Via SSH

```bash
# Se connecter à HA
ssh root@homeassistant.local

# Accéder aux logs de l'addon
docker logs addon_purevent2ha

# Vérifier la connexion
curl http://localhost:5000/health
```

### Via Home Assistant

Settings → Developer tools → Logs → Filtrer "purevent2ha"

## Dépannage

### Module non détecté

```bash
# Vérifier les permissions
sudo chmod 666 /dev/ttyUSB0

# Vérifier la connexion USB
lsusb | grep -i enocean

# Tester le port
ls -la /dev/ttyUSB0
```

### Pas de données reçues

1. Vérifier le baudrate (57600 par défaut)
2. Vérifier la distance du VMI (portée EnOcean ~30m)
3. Vérifier que le VMI envoie bien ses données

```bash
# Checker les logs
docker logs addon_purevent2ha | grep -i "packet\|device"
```

### Erreur de liaison série

```bash
# Vérifier le baudrate
stty -F /dev/ttyUSB0 57600

# Tester avec screen
screen /dev/ttyUSB0 57600

# Quitter: Ctrl+A puis Ctrl+\
```

## Configuration avancée

### Changer le baudrate

Si le VMI utilise un baudrate différent:

1. Dans l'addon, changer "baudrate"
2. Redémarrer l'addon

### Augmenter le timeout

Si les connexions sont instables:

```yaml
# Dans l'addon config
timeout: 60  # Augmenter à 60s
max_retry: 5  # Plus de tentatives
```

### Debug mode

Pour plus de logs:

```yaml
# Dans l'addon config
log_level: debug
```

## Créer les automations

### Exemple 1: Alerte CO2 élevé

Dans Settings → Automations:

```yaml
alias: "VMI - Alerte CO2"
description: ""
trigger:
  - platform: numeric_state
    entity_id: sensor.purevent_co2
    above: 1200
action:
  - service: notify.notify
    data:
      message: "CO2 élevé: {{ states('sensor.purevent_co2') }} ppm"
mode: single
```

### Exemple 2: Chauffage automatique

```yaml
alias: "VMI - Chauffage si froid"
trigger:
  - platform: numeric_state
    entity_id: sensor.purevent_temperature
    below: 18
action:
  - service: switch.turn_on
    entity_id: switch.purevent_heating
condition: []
mode: single
```

Voir [EXAMPLES.md](EXAMPLES.md) pour plus d'exemples.

## Utiliser le dashboard

Un dashboard pré-configuré est disponible:

```yaml
# Ajouter à votre Lovelace YAML
views:
  - title: "Purevent"
    cards:
      - type: custom:button-card
        entity: switch.purevent_power
        name: "VMI Purevent"
        tap_action:
          action: toggle
      
      - type: gauge
        entity: sensor.purevent_humidity
        name: "Humidité"
      
      - type: gauge
        entity: sensor.purevent_co2
        name: "CO2"
```

## Support

### Logs complets

```bash
# 100 dernières lignes
docker logs addon_purevent2ha | tail -100

# Avec timestamps
docker logs addon_purevent2ha -t | tail -50

# Suivi en temps réel
docker logs -f addon_purevent2ha
```

### Vérifier l'API

```bash
# Status
curl http://localhost:5000/health

# Appareils
curl http://localhost:5000/api/devices

# Historique
curl "http://localhost:5000/api/history?limit=10"
```

### Redémarrer l'addon

```bash
# Via Home Assistant
# Settings → Add-ons → Purevent2HA → Restart

# Ou via CLI
docker restart addon_purevent2ha
```

## Prochaines étapes

1. Configurer les automations (voir EXAMPLES.md)
2. Créer un dashboard personnalisé
3. Ajouter des scripts/automatisations
4. Intégrer avec d'autres systèmes

## Besoin d'aide?

- 📖 [Documentation complète](DOCS.md)
- 🧑‍💻 [Guide de développement](DEVELOPMENT.md)
- 📋 [Exemples](EXAMPLES.md)
- 🐛 [Signaler un bug](https://github.com/ricolaflo88/Purevent2HA/issues)
- 💬 [Discussions](https://github.com/ricolaflo88/Purevent2HA/discussions)

## Informations de version

- Version: 1.0.0
- Home Assistant: ≥ 2024.1.0
- Python: 3.11
- Architecture: Multi-arch (amd64, arm64, armv7, armhf)
