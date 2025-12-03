# Purevent2HA - Configuration Example

## Basic Setup

```yaml
# In addon configuration:
port: /dev/ttyUSB0
baudrate: 57600
timeout: 30
max_retry: 3
log_level: info
name: "Purevent2HA"
```

## Home Assistant Automations

### Example 1: Auto-enable heating when cold

```yaml
automation:
  - id: "purevent_heating_cold"
    alias: "VMI - Chauffage si froid"
    description: "Activer le chauffage si T < 18°C"
    
    trigger:
      - platform: numeric_state
        entity_id: sensor.purevent_temperature
        below: 18
    
    action:
      - service: switch.turn_on
        entity_id: switch.purevent_heating
      - service: notify.notify
        data:
          message: "Chauffage activé automatiquement"
```

### Example 2: Disable VMI on absence

```yaml
automation:
  - id: "purevent_absence"
    alias: "VMI - Arrêt absence"
    description: "Arrêter VMI si pas de présence"
    
    trigger:
      - platform: state
        entity_id: binary_sensor.presence
        to: "off"
    
    condition:
      - condition: state
        entity_id: switch.purevent_power
        state: "on"
    
    action:
      - service: switch.turn_off
        entity_id: switch.purevent_power
      - service: notify.notify
        data:
          message: "VMI arrêtée (absence)"
```

### Example 3: Reduce fan speed when away

```yaml
automation:
  - id: "purevent_away_mode"
    alias: "VMI - Mode absence"
    description: "Réduire vitesse ventilateur en absence"
    
    trigger:
      - platform: state
        entity_id: input_boolean.away_mode
        to: "on"
    
    action:
      - service: number.set_value
        entity_id: number.purevent_fan_speed
        data:
          value: 20  # 20% speed
```

### Example 4: Alert on high CO2

```yaml
automation:
  - id: "purevent_high_co2"
    alias: "VMI - Alerte CO2 élevé"
    description: "Alerte quand CO2 > 1200 ppm"
    
    trigger:
      - platform: numeric_state
        entity_id: sensor.purevent_co2
        above: 1200
    
    action:
      - service: notify.notify
        data:
          title: "Alerte qualité d'air"
          message: "CO2 élevé: {{ states('sensor.purevent_co2') }} ppm"
```

## Template Sensors

Add these to your `configuration.yaml` or create `sensors.yaml`:

```yaml
template:
  - sensor:
      - name: "VMI Status"
        unique_id: purevent_status_template
        state: >
          {% if is_state('switch.purevent_power', 'on') %}
            {% if is_state('switch.purevent_heating', 'on') %}
              Chauffage
            {% elif is_state('switch.purevent_cooling', 'on') %}
              Refroidissement
            {% else %}
              En marche
            {% endif %}
          {% else %}
            Arrêtée
          {% endif %}
      
      - name: "VMI Air Quality"
        unique_id: purevent_air_quality
        state: >
          {% set co2 = states('sensor.purevent_co2') | int(0) %}
          {% if co2 < 800 %}
            Excellent
          {% elif co2 < 1000 %}
            Bon
          {% elif co2 < 1200 %}
            Acceptable
          {% else %}
            Mauvais
          {% endif %}
        icon: mdi:air-filter
```

## Input Helpers

Create these helpers for manual control:

```yaml
input_boolean:
  away_mode:
    name: "Mode absence"
    icon: mdi:door

  heating_enabled:
    name: "Chauffage autorisé"
    icon: mdi:fire

input_number:
  target_temp:
    name: "Température cible"
    min: 15
    max: 25
    unit_of_measurement: "°C"
    step: 0.5
```

## Groups

```yaml
group:
  purevent_sensors:
    name: "Capteurs VMI"
    entities:
      - sensor.purevent_temperature
      - sensor.purevent_humidity
      - sensor.purevent_co2

  purevent_controls:
    name: "Contrôles VMI"
    entities:
      - switch.purevent_power
      - switch.purevent_heating
      - switch.purevent_cooling
      - number.purevent_fan_speed
```

## Scene Examples

```yaml
scene:
  - id: "purevent_comfort"
    name: "Mode Confort"
    entities:
      switch.purevent_power: on
      switch.purevent_heating: on
      number.purevent_fan_speed: 75

  - id: "purevent_eco"
    name: "Mode Économique"
    entities:
      switch.purevent_power: on
      switch.purevent_heating: off
      number.purevent_fan_speed: 30

  - id: "purevent_off"
    name: "Arrêt complet"
    entities:
      switch.purevent_power: off
```

## Dashboard Card Example

For custom dashboard with `custom:button-card`:

```yaml
type: custom:button-card
entity: switch.purevent_power
name: "VMI Purevent"
state:
  - operator: template
    value: "{{ is_state('switch.purevent_power', 'on') }}"
    styles:
      card:
        - background-color: "rgba(76, 175, 80, 0.3)"
tap_action:
  action: toggle
```

## Service Call Examples

Via Developer Tools > Services:

```yaml
# Power on
service: switch.turn_on
target:
  entity_id: switch.purevent_power

# Enable heating
service: switch.turn_on
target:
  entity_id: switch.purevent_heating

# Set fan speed to 50%
service: number.set_value
target:
  entity_id: number.purevent_fan_speed
data:
  value: 50

# Set temperature to 22°C
service: climate.set_temperature
target:
  entity_id: climate.purevent_vmi
data:
  temperature: 22
  hvac_mode: heat

# Custom command
service: purevent2ha.send_command
data:
  device_id: purevent_vmi
  command: POWER
  parameters: true
```
