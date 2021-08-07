#!/usr/bin/env python3

import sys
import json
import time
import argparse
import datetime

# Add the submodule to PATH
sys.path.append('PyExpLabSys')
sys.path.append('PyExpLabSys/PyExpLabSys/drivers')

import tenma

#
#

class Tenma722540(tenma.TenmaBase):
    pass

#
#

def monitor(mqtt, topic):

    server = None

    if mqtt and topic:
        from iot import broker3 as broker
        server = broker.Broker("tenma-psu", server=mqtt)

    while True:
        try:
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            tt = datetime.datetime.now()
            print(tt, vt, it)
 
            if server:
                msg = { 'V' : vt, 'I' : it }
                server.send(topic, json.dumps(msg))
        except ValueError:
            pass

        time.sleep(0.01)

#
#

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('--path', dest='path', default='/dev/psu', help='device path')
    p.add_argument('commands', nargs='+')
    p.add_argument('--max-v', dest='max_v', type=float, default=16.8)
    p.add_argument('--max-i', dest='max_i', type=float, default=2.0)
    p.add_argument('--overcurrent', dest='overcurrent', type=int, default=0)
    p.add_argument('--overvoltage', dest='overvoltage', type=int, default=0)
    p.add_argument('--on', dest='on', action='store_true', default=False)
    p.add_argument('--mqtt', dest='mqtt', help='mqqt server')
    p.add_argument('--topic', dest='topic', help='mqtt topic')

    args = p.parse_args()
    #print(args)

    device = Tenma722540(args.path)

    print('set overcurrent', args.overcurrent)
    device.set_overcurrent_protection(args.overcurrent)
    print('set overvoltage', args.overvoltage)
    device.set_overvoltage_protection(args.overvoltage)

    def set_voltage(vv):
        assert (vv >= 0.0), vv
        print(f'set v={vv}')
        global v
        assert(vv <= args.max_v), (vv, args.max_v)
        v = vv
        device.set_voltage(v)

    i = device.get_actual_current()
    v = device.get_actual_voltage()

    if args.on:
        print(f'switch on. v={v} i={i}')
        device.set_output(True)        

    repeat = False

    while True:

        for command in args.commands:
            if command == 'on':
                print(f'switch on. v={v} i={i}')
                device.set_output(True)
            elif command == 'off':
                print('switch off')
                device.set_output(False)
            elif command.startswith('sleep='):
                parts = command.split('=')
                period = float(parts[1])
                print('sleeping', period)
                time.sleep(period)
            elif command == 'repeat':
                print('repeat')
                repeat = True
            elif command.startswith('v+'):
                parts = command.split('+')
                set_voltage(v + float(parts[1]))
            elif command.startswith('v-'):
                parts = command.split('-')
                set_voltage(v - float(parts[1]))
            elif command.startswith('v='):
                parts = command.split('=')
                set_voltage(float(parts[1]))
            elif command == 'monitor':
                monitor(args.mqtt, args.topic)
            else:
                raise Exception(f'Unknown command {command}')

        if not repeat:
            break

# FIN