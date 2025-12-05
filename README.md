# amm_read

Using HAN interface to read AMM tariff device.


## Setup

Raspberry PI with RS485 -> USB converter at the tariff device (HAN reading).
Home Assistant with MQTT server running. Can be RPi too.


### Install and run service

1) Copy script folder to you RPi home directory.
2) Login to RPi and goto script folder.
3) Create secrets.py file containing your HA MQTT credentials.

Example secrets.py
```python
MQTT_IP = '192.168.42.123'
MQTT_USER = 'tariff_device_mqtt_user_name'
MQTT_PWD = 'tariff_device_mqtt_password'
```
MQTT IP and credentials came from Home Assistant user setting. You can create extra MQTT user for your tariff device in HA.

4) Test your MQTT connection by running ha_mqtt.py

```bash
python ha_mqtt.py
```

If you see ```home/energy/tariff=T0``` in your MQTT explorer in HA now, MQTT publishing is working.

5) Test HAN interface reading by running catch_feed.py

```
python catch_feed.py
```

If your HAN connection works, you will see packet receive log every half minute. The shorter is relebox message, longer is tariff readout.

6) Run it as service defined in catch_feed.service file.

```
sudo cp catch_feed.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/catch_feed.service
sudo systemctl daemon-reload
sudo systemctl enable catch_feed.service
sudo systemctl start catch_feed.service
```

This will copy .service file to its place, ensure it has right privileges. Than reload daemons, enable after reboot and start it imediatelly.


### Connect HA entities to MQTT

Make sure you have ```mqtt.yaml``` file created and ```mqtt: !include mqtt.yaml``` line in ```configuration.yaml``` file in your Home Assistant settings.
Insert following in ```mqtt.yaml``` file:

```yaml
sensor:

  # tariff devide (energy)
  - name: "Energy Tariff"
    unique_id: "energy_tariff"
    state_topic: "home/energy/tariff"

  - name: "Energy Total Consumption"
    unique_id: "energy_total"
    state_topic: "home/energy/consumption/total"
    unit_of_measurement: "Wh"
    device_class: energy
    state_class: total_increasing

  - name: "Energy Consumption T1"
    unique_id: "energy_t1"
    state_topic: "home/energy/consumption/T1"
    unit_of_measurement: "Wh"
    device_class: energy
    state_class: total_increasing

  - name: "Energy Consumption T2"
    unique_id: "energy_t2"
    state_topic: "home/energy/consumption/T2"
    unit_of_measurement: "Wh"
    device_class: energy
    state_class: total_increasing
```

This will connect sensor.energy_tarif, sensor.energy_total, sensor.energy_t1 and sensor.energy_t2 entities to its MQTT topics.
You can use those entities in your HA energy dashboard.
