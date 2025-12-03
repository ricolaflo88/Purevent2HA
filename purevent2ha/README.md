"""Purevent2HA - Addon for Home Assistant"""

# Purevent2HA

Une intégration complète pour la VMI Purevent via le protocole EnOcean dans Home Assistant.

## Fonctionnalités

- ✅ Réception des données des capteurs:
  - Température et humidité (A5-04-01)
  - CO2 (A5-09-04)
  - État du VMI (D1079-01-00)
- ✅ Commande du VMI Purevent:
  - Marche/Arrêt
  - Chauffage
  - Refroidissement
  - Vitesse du ventilateur
- ✅ Support de l'assistant Ventilairsec (D1079-00-00)
- ✅ Historique complet des données
- ✅ Dashboard intégré
- ✅ Services Home Assistant
- ✅ Multi-langues (FR, EN)

## Installation

### Via le repository d'addons

1. Ajouter ce repository à Home Assistant: https://github.com/ricolaflo88/Purevent2HA
2. Installer "Purevent2HA" depuis la boutique d'addons
3. Configurer le port série et démarrer l'addon

### Configuration

Dans la configuration de l'addon:

```yaml
port: /dev/ttyUSB0  # Port du module EnOcean
baudrate: 57600
timeout: 30
max_retry: 3
log_level: info
```

## Entités créées

### Capteurs
- `sensor.purevent_temperature` - Température (°C)
- `sensor.purevent_humidity` - Humidité (%)
- `sensor.purevent_co2` - Concentration CO2 (ppm)
- `sensor.purevent_status` - État du VMI
- `sensor.purevent_filter_state` - État du filtre
- `sensor.purevent_airflow` - Débit d'air (m³/h)

### Contrôles
- `switch.purevent_power` - Alimentation On/Off
- `switch.purevent_heating` - Chauffage On/Off
- `switch.purevent_cooling` - Refroidissement On/Off
- `switch.purevent_intake` - Insufflation d'air On/Off
- `number.purevent_fan_speed` - Vitesse ventilateur (0-100%)

### Climat
- `climate.purevent_vmi` - Contrôle climat du VMI

## Services

### `purevent2ha.send_command`

Envoyer une commande personnalisée:

```yaml
service: purevent2ha.send_command
data:
  device_id: "purevent_vmi"
  command: "POWER"
  parameters: true
```

## Dépannage

### Le module n'est pas détecté

1. Vérifier le port série: `ls -la /dev/tty*`
2. Vérifier les permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Vérifier la connexion USB du module EnOcean

### Pas de données reçues

1. Vérifier la configuration du baudrate (57600 par défaut)
2. Vérifier les logs: `docker logs addon_purevent2ha`
3. Vérifier les ID des appareils EnOcean

### Erreurs de liaison série

- Baudrate incorrect
- Câblage USB défectueux
- Ports USB surchargés

## Support

Pour toute question ou problème, consultez:
- GitHub: https://github.com/ricolaflo88/Purevent2HA
- Documentation: https://github.com/ricolaflo88/Purevent2HA/wiki

## Licence

AGPL v3
