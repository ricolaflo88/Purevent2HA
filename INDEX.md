# Purevent2HA - Documentation et Ressources

## 📚 Documentation complète

- **[README.md](README.md)** - Vue d'ensemble et fonctionnalités
- **[SETUP.md](SETUP.md)** - Guide d'installation détaillé
- **[DOCS.md](purevent2ha/DOCS.md)** - Documentation technique
- **[DEVELOPMENT.md](purevent2ha/DEVELOPMENT.md)** - Guide de développement
- **[EXAMPLES.md](EXAMPLES.md)** - Exemples d'utilisation et automations
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions

## 🎯 Démarrage rapide

1. Ajouter le repository: `https://github.com/ricolaflo88/Purevent2HA`
2. Installer l'addon "Purevent2HA"
3. Configurer le port série (`/dev/ttyUSB0` par défaut)
4. Démarrer et consulter les logs

## 🔌 Appareils supportés

- **VMI Purevent** (D1079-01-00) - Appareil principal
- **Capteur CO2** (A5-09-04) - Mesure CO2
- **Capteur T°/Humidité** (A5-04-01) - Mesure température/humidité
- **Assistant Ventilairsec** (D1079-00-00) - Support optionnel

## 🎚️ Entités Home Assistant

### Capteurs
- Temperature, Humidity, CO2
- Status, Filter State, Airflow

### Contrôles
- Power, Heating, Cooling, Intake
- Fan Speed

### Climat
- Climate entity avec contrôle température

## 🛠️ Services disponibles

- `purevent2ha.send_command` - Envoyer des commandes personnalisées

## 📊 Architecture

```
Module EnOcean USB
    ↓
Daemon Python (port 5000)
    ↓
API HTTP
    ↓
Home Assistant Integration
    ↓
Sensor/Switch/Climate/Number Entities
    ↓
Automations & Dashboard
```

## 🚀 Installation (résumé)

### Via addon repository

1. Settings → Add-ons → Create addon repository
2. Ajouter: `https://github.com/ricolaflo88/Purevent2HA`
3. Installer "Purevent2HA"
4. Configurer le port série
5. Démarrer l'addon

### Ports série courants

- Linux: `/dev/ttyUSB0`, `/dev/ttyUSB1`, `/dev/ttyAMA0`
- macOS: `/dev/tty.usbserial-*`
- Windows: `COM1`, `COM3`, etc.

## 📋 Configuration

```yaml
# Dans l'addon configuration
port: /dev/ttyUSB0      # Port du module EnOcean
baudrate: 57600         # Vitesse liaison
timeout: 30             # Timeout en secondes
max_retry: 3            # Tentatives maximum
log_level: info         # Level de log
```

## 🔧 Dépannage courant

| Problème | Solution |
|----------|----------|
| Module non détecté | Vérifier le port avec `ls -la /dev/tty*` |
| Pas de données | Vérifier baudrate et distance VMI |
| Erreur liaison | Vérifier les permissions: `sudo chmod 666 /dev/ttyUSB0` |
| Logs vides | Augmenter log_level en debug |

## 📝 Automations rapides

**Activer chauffage si froid:**
```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.purevent_temperature
    below: 18
action:
  - service: switch.turn_on
    entity_id: switch.purevent_heating
```

**Alerte CO2 élevé:**
```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.purevent_co2
    above: 1200
action:
  - service: notify.notify
    data:
      message: "CO2 élevé!"
```

Voir [EXAMPLES.md](EXAMPLES.md) pour plus d'exemples.

## 🐛 Rapporter un bug

1. Vérifier les logs: `docker logs addon_purevent2ha`
2. Essayer de redémarrer l'addon
3. Consulter la documentation
4. Créer une issue sur GitHub avec les logs et la configuration

## 💡 Fonctionnalités

✅ Réception des capteurs EnOcean
✅ Commande du VMI Purevent
✅ Support complet Home Assistant
✅ Dashboard Lovelace intégré
✅ Historique des données
✅ Multi-langues (FR, EN)
✅ Architecture multi-platform

## 📈 Performance

- Latence: <100ms
- Mémoire: ~50MB
- CPU: <5% au repos
- Compatibilité: Multi-arch (x86_64, ARM64, ARMv7, etc.)

## 🔐 Sécurité

- API locale uniquement
- Validation des entrées
- Pas de données sensibles en logs
- Permissions minimales requises

## 📞 Support

- GitHub Issues: https://github.com/ricolaflo88/Purevent2HA/issues
- GitHub Discussions: https://github.com/ricolaflo88/Purevent2HA/discussions
- Documentation: Cette page

## 📜 Licence

AGPL v3 - Voir [LICENSE](LICENSE)

## 🙏 Remerciements

Basé sur:
- Plugin Jeedom OpenEnOcean
- Plugin Jeedom Ventilairsec
- Bibliothèque python-enocean

---

**Fait avec ❤️ pour la communauté Home Assistant**

Version: 1.0.0 | Mise à jour: 2024-12-03
