#!/usr/bin/env python3

import sys
import os
import json
import time
import argparse
import datetime

# Add the submodule to PATH
here = os.path.dirname(__file__)
sys.path.append(here + '/PyExpLabSys')
sys.path.append(here + '/PyExpLabSys/PyExpLabSys/drivers')

import tenma

#
#

class Tenma722540(tenma.TenmaBase):
    pass

#
#

def show(server, topic, i, v):
    tt = datetime.datetime.now()
    print(tt, v, i)

    if server and topic:
        msg = { 'V' : v, 'I' : i }
        server.send(topic, json.dumps(msg))
#
#

def monitor(server, topic):

    while True:
        try:
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            show(server, topic, it, vt)
        except ValueError:
            pass

#
#

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument('--path', dest='path', default='/dev/psu', help='device path')
    p.add_argument('commands', nargs='+')
    p.add_argument('--max-v', dest='max_v', type=float, default=16.8)
    p.add_argument('--max-i', dest='max_i', type=float, default=2.0)
    p.add_argument('--min-v', dest='min_v', type=float, default=0.0)
    p.add_argument('--overcurrent', dest='overcurrent', type=int, default=1)
    p.add_argument('--overvoltage', dest='overvoltage', type=int, default=1)
    p.add_argument('--on', dest='on', action='store_true', default=False)
    p.add_argument('--mqtt', dest='mqtt', help='mqqt server')
    p.add_argument('--topic', dest='topic', help='mqtt topic')
    p.add_argument('--memory', dest='memory', type=int, default=5)

    args = p.parse_args()
    #print(args)

    device = Tenma722540(args.path)

    memory = args.memory

    server = None
    if args.mqtt and args.topic:
        from iot import broker3 as broker
        server = broker.Broker("tenma-psu", server=args.mqtt)

    print(':set overcurrent', args.overcurrent)
    device.set_overcurrent_protection(args.overcurrent)
    print(':set overvoltage', args.overvoltage)
    device.set_overvoltage_protection(args.overvoltage)

    def set_voltage(vv):
        assert(vv >= args.min_v), (vv, args.min_v)
        global v
        assert(vv <= args.max_v), (vv, args.max_v)
        v = vv
        print(f':set v={v}')
        device.set_voltage(v)

    i = args.max_i
    print(f':set current={i}')
    device.set_current(i)

    i = device.get_actual_current()
    v = device.get_actual_voltage()

    if args.on:
        print(f':switch on. v={v} i={i}')
        device.set_output(True)  

    repeat = False

    idx = 0
    loop = 0

    try:
        while idx < len(args.commands):

            sys.stdout.flush()

            command = args.commands[idx]
            idx += 1

            if command == 'on':
                print(f':switch on. v={v} i={i}')
                device.set_output(True)
            elif command == 'off':
                print(':switch off')
                device.set_output(False)
            elif command.startswith('sleep='):
                parts = command.split('=')
                period = float(parts[1])
                print(':sleeping', period)
                time.sleep(period)
            elif command == 'repeat':
                print(':repeat')
                idx = loop
            elif command == 'loop':
                print(':loop')
                loop = idx
            elif command.startswith('v+'):
                parts = command.split('+')
                set_voltage(v + float(parts[1]))
            elif command.startswith('v-'):
                parts = command.split('-')
                set_voltage(v - float(parts[1]))
            elif command.startswith('v='):
                parts = command.split('=')
                set_voltage(float(parts[1]))
            elif command.startswith('i='):
                parts = command.split('=')
                device.set_current(float(parts[1]))
            elif command.startswith('m='):
                parts = command.split('=')
                memory = int(parts[1])
                print(f':set memory={memory}')
                device.recall_memory(memory)
            elif command == 'monitor':
                monitor(server, args.topic)
            elif command == 'show':
                it = device.get_actual_current()
                vt = device.get_actual_voltage()
                show(server, args.topic, it, vt)
            elif command == 'save':
                print(':save memory', memory)
                device.save_memory(memory)
            else:
                raise Exception(f'Unknown command {command}')
    except AssertionError as ex:
        print(':AssertionError', ex)

# FIN
