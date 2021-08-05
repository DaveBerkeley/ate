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

def discharge():
    print('ID:', device.get_identification())
    print('Status:', device.status())

    device.set_output(False)
    device.recall_memory(5)

    device.set_overcurrent_protection(True)
    device.set_overvoltage_protection(True)

    device.set_voltage(0.0)
    device.set_current(2.0)
    time.sleep(3)
    device.set_output(True)

    time.sleep(3)

    try:
        for mv in range(15000, 0, -10):
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
    while True:
        try:
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            print(vt, it)
 
            msg = { 'V' : vt, 'I' : it }
            mqtt.send(topic, json.dumps(msg))
        except ValueError:
            pass

        time.sleep(.1)

#
#

def alert():
    device.set_output(False)
    device.recall_memory(5)

    print('Overcurrent and overvoltage protection, watch the LEDS switch')
    device.set_overcurrent_protection(True)
    device.set_overvoltage_protection(True)

    v = 16.0
    device.set_voltage(v)
    device.set_current(2.0)
    device.set_output(True)

    time.sleep(3)

    it = device.get_actual_current()
    vt = device.get_actual_voltage()
    print(vt, it)

    msg = { 'V' : vt, 'I' : it }
    mqtt.send(topic, json.dumps(msg))

    while True:
        device.set_voltage(v)
        v -= 0.01
        time.sleep(0.1)

        if v < 5:
            break
        
        it = device.get_actual_current()
        vt = device.get_actual_voltage()
        print(vt, it)

        msg = { 'V' : vt, 'I' : it }
        mqtt.send(topic, json.dumps(msg))


#
#

if __name__ == "__main__":
    device = Tenma722540('/dev/psu')

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'on':
            device.set_voltage(16.8)
            device.set_current(2.0)
            device.set_output(True)
        elif cmd == 'off':
            device.set_output(False)
    else:
        #main()
        monitor()
        #discharge()
        #alert()

# FIN
