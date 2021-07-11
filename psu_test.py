#!/usr/bin/env python3

import sys
import json
import time

from iot import broker3 as broker

# Add the submodule to PATH
sys.path.append('PyExpLabSys')
sys.path.append('PyExpLabSys/PyExpLabSys/drivers')

import tenma

class Tenma722540(tenma.TenmaBase):
    pass

mqtt = broker.Broker("xively", server="mosquitto")

topic = 'home/psu'

#
#

def main():
    """Main module function, used for testing simple functional test"""
    device = Tenma722540('/dev/psu')
    print('ID:', device.get_identification())
    print('Status:', device.status())

    device.set_output(False)
    device.recall_memory(5)

    print('Overcurrent and overvoltage protection, watch the LEDS switch')
    device.set_overcurrent_protection(True)
    device.set_overvoltage_protection(True)

    device.set_voltage(0.0)
    device.set_current(0.4)
    device.set_output(True)

    try:
        for mv in range(0, 16500, 250):
            volts = mv / 1000.0
            device.set_voltage(volts)
            #time.sleep(1)
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            #print(vt, it)

            msg = { 'V' : vt, 'I' : it }
            mqtt.send(topic, json.dumps(msg))
    
    except KeyboardInterrupt:
        pass

    print("Done")
    device.set_output(False)
    device.set_voltage(0.0)
    device.set_overcurrent_protection(False)
    device.set_overvoltage_protection(False)
    device.recall_memory(1)

    it = device.get_actual_current()
    vt = device.get_actual_voltage()
    print(vt, it)

    msg = { 'V' : vt, 'I' : it }
    mqtt.send(topic, json.dumps(msg))

#
#

def monitor():
    device = Tenma722540('/dev/psu')

    while True:
        try:
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            #print(vt, it)
    
            msg = { 'V' : vt, 'I' : it }
            mqtt.send(topic, json.dumps(msg))
        except ValueError:
            pass

        time.sleep(1)

main()

# FIN
