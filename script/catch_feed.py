#!/usr/bin/python3

import serial
import datetime
from ha_mqtt import mqttPublisher

PORT = '/dev/ttyUSB0'
BAUD = 9600

""" 
Dictionary of OBIS codes to search for

  structure of entry:
    obis_code: (description, unit, mqtt_topic)

  where:
    obis_code .. 6 byte code of HAN entry (bytes)
    description .. verbal description of entry (string)
    unit .. unit of entry
    mqtt_topic .. mqtt topic to publish value (string)
"""
OBIS = {
    b'\x00\x00\x60\x0E\x00\xFF': ('Active tarif', '', 'tariff'),
    #b'\x01\x00\x01\x07\x00\xFF': ('Instantaneous active power', 'W', 'power'),
    b'\x01\x00\x01\x08\x00\xFF': ('Active energy import (total)', 'Wh', 'consumption/total'),
    b'\x01\x00\x01\x08\x01\xFF': ('Active energy import - Tariff 1', 'Wh', 'consumption/T1'),
    b'\x01\x00\x01\x08\x02\xFF': ('Active energy import - Tariff 2', 'Wh', 'consumption/T2'),
}

# if filename is set, all HAN messages are logged into it
#filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_log.csv")
filename = None


# file logging
def add_line(fname, line):

    if fname:
        with open(fname, 'a') as fd:
            fd.write(f"{line.strip()}\n")

# create string from bytes message
def bytes_to_string(data):
    s = ""
    for d in data:
        s += ("" if s=="" else " ") + "{:02X}".format(d)
    return s

# decode value
# data .. received HAN message
# pos .. position of OBIS in data
def decode(data, pos):
    if (pos < 4) and (data[pos-4] != 2) and (data[pos-3] != 2):
        return None

    if data[pos + 7] == 6: # 32 bit unsigned
        val = 0
        beg = pos + 8
        for d in data[beg : beg+4]:
            val <<= 8
            val |= d
        return val

    if data[pos + 7] == 9: # string
        dlen = data[pos + 8]
        val = ''
        beg = pos + 9
        for d in data[beg : beg + dlen]:
            val += chr(d)
        return val


# continual reading of serial port
with serial.Serial(PORT, BAUD, timeout=0.2) as port:

    mqtt_client = mqttPublisher()

    while True:
        data = port.readall()
        if data != b'':
            strdata = bytes_to_string(data)
            now = datetime.datetime.now()
            tstamp = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            #print("{} ({}) {}".format(tstamp, len(data), strdata))
            print("{} {} bytes".format(tstamp, len(data)))
            csvline = "{};{}".format(tstamp, strdata)
            add_line(filename, csvline)
            connected = False
            for ob in OBIS:
                fnd = data.find(ob)
                if fnd != -1:
                    dec = decode(data, fnd)
                    if dec:
                        if not connected:
                            mqtt_client.connect()
                            connected = True
                        desc = OBIS[ob]
                        print(f'{desc[0]}: {dec} {desc[1]}')
                        mqtt_client.publish_obis(desc[2], dec)
            if connected:
                    mqtt_client.disconnect()

