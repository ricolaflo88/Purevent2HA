# Purevent2HA - Documentation

## Vue d'ensemble

Purevent2HA est une intégration Home Assistant complète pour la VMI Purevent via le protocole EnOcean.

### Fonctionnalités

- **Réception de données** : Capteurs CO2, Température/Humidité, capteur assistant Ventilairsec
- **Commandes** : Envoi de commandes à la VMI Purevent
- **Surveillance** : État du VMI, erreurs, filtres
- **Dashboard** : Interface Lovelace pour visualisation et contrôle
- **Historique** : Stockage des données pour analyse

### Appareils supportés

- **VMI Purevent** (D1079-01-00) : Appareil principal
- **Capteur CO2** (A5-09-04) : Mesure CO2
- **Capteur Température/Humidité** (A5-04-01) : Mesure T/H
- **Assistant Ventilairsec** (D1079-00-00) : Assistance

## Configuration

### Port série

Spécifier le port de connexion du module EnOcean:
- Linux: `/dev/ttyUSB0`, `/dev/ttyACM0`
- Format: String

### Paramètres avancés

- **Baudrate**: Vitesse de liaison (défaut: 57600)
- **Timeout**: Délai d'attente (défaut: 30s)
- **Max Retry**: Tentatives (défaut: 3)
- **Log Level**: Niveau de journalisation

## Entités créées

### Sensors
- `sensor.purevent_temperature`
- `sensor.purevent_humidity`
- `sensor.purevent_co2`
- `sensor.purevent_status`

### Switches
- `switch.purevent_power`
- `switch.purevent_heating`

### Climate
- `climate.purevent_vmi`

### Numbers
- `number.purevent_fan_speed`

## Services

### `purevent2ha.send_command`
Envoyer une commande au VMI.

Paramètres:
- `device_id`: ID du périphérique
- `command`: Commande à envoyer
- `parameters`: Paramètres additionnels

## Troubleshooting

### Le module EnOcean n'est pas détecté
- Vérifier le port série correct
- Vérifier les permissions (sudo)
- Vérifier la connexion USB

### Pas de données reçues
- Vérifier la configuration des appareils EnOcean
- Vérifier les ID des périphériques
- Consulter les logs: `docker logs addon_purevent2ha`

### Erreur de liaison série
- Vérifier le baudrate (57600 par défaut)
- Vérifier le câblage
