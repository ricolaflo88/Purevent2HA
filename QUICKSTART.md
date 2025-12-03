"""Quick start guide for developers"""

# Purevent2HA - Guide de démarrage rapide pour développeurs

## Structure du repository

```
Purevent2HA/
├── purevent2ha/                           # Addon Home Assistant
│   ├── addon.yaml                         # Configuration addon
│   ├── Dockerfile                         # Image Docker
│   ├── README.md                          # Documentation addon
│   ├── DEVELOPMENT.md                     # Guide développement
│   ├── DOCS.md                            # Documentation technique
│   ├── rootfs/                            # Système fichiers addon
│   │   ├── app/                           # Code daemon
│   │   │   ├── purevent2ha_daemon.py     # Daemon principal
│   │   │   ├── enocean_comm.py            # Communication EnOcean
│   │   │   ├── api.py                     # API HTTP
│   │   │   └── utils.py                   # Utilitaires
│   │   ├── etc/purevent2ha/               # Configuration
│   │   └── usr/local/bin/
│   │       └── startup.sh                 # Script démarrage
│   ├── custom_components/purevent2ha/     # Intégration HA
│   │   ├── __init__.py                    # Main integration
│   │   ├── manifest.json                  # Manifest
│   │   ├── const.py                       # Constantes
│   │   ├── config_flow.py                 # Configuration UI
│   │   ├── coordinator.py                 # Data coordinator
│   │   ├── services.py                    # Services HA
│   │   ├── sensor.py                      # Platform sensor
│   │   ├── switch.py                      # Platform switch
│   │   ├── climate.py                     # Platform climate
│   │   ├── number.py                      # Platform number
│   │   ├── devices/                       # Configs appareils
│   │   ├── translations/                  # Traductions i18n
│   │   └── services.yaml                  # Définition services
│   └── tests/                             # Tests
├── .github/workflows/                     # CI/CD
├── README.md                              # Principal README
├── SETUP.md                               # Guide installation
├── EXAMPLES.md                            # Exemples utilisation
├── INDEX.md                               # Index documentation
├── CHANGELOG.md                           # Historique versions
├── LICENSE                                # Licence MIT
├── repository.json                        # Config repository
├── build.sh                               # Script build
├── deploy.sh                              # Script déploiement
├── verify.sh                              # Script vérification
└── run_tests.sh                           # Script tests
```

## Démarrage rapide

### 1. Configuration initiale

```bash
cd /workspaces/Purevent2HA

# Vérifier la structure
./verify.sh

# Vérifier les fichiers manquants
./deploy.sh
```

### 2. Développer localement

#### Option A: Build Docker local

```bash
# Build l'addon
cd purevent2ha
docker build -t purevent2ha .

# Tester le daemon
docker run -it -v $(pwd)/rootfs/app:/app purevent2ha python3 /app/purevent2ha_daemon.py
```

#### Option B: Tester en dev container

```bash
# Installer les dépendances
pip install -r purevent2ha/rootfs/requirements.txt

# Tester le daemon
python3 purevent2ha/rootfs/app/purevent2ha_daemon.py
```

### 3. Tester l'intégration HA

```bash
# Copier vers config HA de dev
cp -r purevent2ha/custom_components/purevent2ha ~/.config/homeassistant/custom_components/

# Redémarrer HA
# Settings → Developer tools → YAML → Automations → Restart
```

### 4. Exécuter les tests

```bash
./run_tests.sh

# Ou manuellement
pytest purevent2ha/tests/ -v
```

## Modification et déploiement

### Ajouter une nouvelle plateforme (ex: light)

1. Créer `purevent2ha/custom_components/purevent2ha/light.py`
2. Ajouter à `__init__.py`: `Platform.LIGHT` dans `PLATFORMS`
3. Ajouter au manifest.json
4. Tester

### Modifier le daemon

1. Éditer les fichiers dans `rootfs/app/`
2. Tester localement avec Docker
3. Rebuild et tester

### Ajouter une traduction

1. Éditer `custom_components/purevent2ha/translations/*.json`
2. Ajouter la clé dans les fichiers de traduction

### Créer une nouvelle version

1. Mettre à jour `addon.yaml`: version
2. Mettre à jour `CHANGELOG.md`
3. Commit et push

## Debugging

### Logs daemon

```bash
docker logs -f addon_purevent2ha
# Ou en dev:
tail -f /var/log/purevent2ha.log
```

### Test API directement

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/devices
curl -X POST http://localhost:5000/api/commands \
  -H "Content-Type: application/json" \
  -d '{"device_id":"vmi","command":"POWER"}'
```

### Python REPL

```python
from purevent2ha.rootfs.app.enocean_comm import EnOceanCommunicator

comm = EnOceanCommunicator(port='/dev/ttyUSB0')
comm.connect()
comm.start()

# Voir les messages reçus
for callback in comm.callbacks:
    print(callback)
```

## Fichiers à connaître

| Fichier | Rôle |
|---------|------|
| `addon.yaml` | Configuration de l'addon |
| `manifest.json` | Manifest de l'intégration HA |
| `purevent2ha_daemon.py` | Daemon principal (cœur) |
| `enocean_comm.py` | Communication EnOcean |
| `coordinator.py` | Mise à jour des données |
| `sensor.py` | Entités capteurs |
| `switch.py` | Entités switches |
| `climate.py` | Entité climate |

## Points d'extension

### Ajouter un appareil

1. Configuration device JSON: `devices/XXXX-XX-XX.json`
2. Parser dans `enocean_comm.py`: `_parse_packet()`
3. Mapping dans `coordinator.py`: `_process_devices()`
4. Entités correspondantes

### Ajouter une commande

1. Ajouter dans device JSON: `commands: []`
2. Implémenter dans `enocean_comm.py`: `send_command()`
3. Service correspondant

### Ajouter une entité

1. Créer la platform: `entity_type.py`
2. Ajouter à `PLATFORMS` dans `__init__.py`
3. Ajouter les entités dans le fichier

## Checklist avant release

- [ ] Tester localement avec Docker
- [ ] Vérifier les logs (pas d'erreur)
- [ ] Exécuter les tests: `./run_tests.sh`
- [ ] Vérifier la structure: `./verify.sh`
- [ ] Mettre à jour CHANGELOG.md
- [ ] Mettre à jour version dans addon.yaml
- [ ] Commit et push
- [ ] Créer une release GitHub
- [ ] Tester depuis le repository addon

## Ressources

- [Home Assistant Addon Development](https://developers.home-assistant.io/docs/add-ons/dev_environment/)
- [Home Assistant Integration Development](https://developers.home-assistant.io/docs/development_index)
- [EnOcean Protocol Specification](https://www.enocean.com/en/technology/specifications/)
- [python-enocean Documentation](https://python-enocean.readthedocs.io/)

---

**Version**: 1.0.0  
**Créé**: 2024-12-03
"""
