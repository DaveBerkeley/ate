#!/usr/bin/env python3

import sys
import os
import json
import time
import argparse
import datetime

import socket
import serial

# Add the submodule to PATH
here = os.path.dirname(__file__)
sys.path.append(here + '/hm305_ctrl')

sys.path.append(here + '/PyExpLabSys')
sys.path.append(here + '/PyExpLabSys/PyExpLabSys/drivers')

from tenma import TenmaBase

# https://github.com/JackDoan/hm305_ctrl 
from hm305 import HM305

#
#

class Socket(TenmaBase):

    def __init__(self, server, port, sleep_after_command=0.1):
        self.sleep_after_command = sleep_after_command
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((server, port))

    def com(self, command, decode_reply=True):
        #print(':: tx', command)
 
        self.s.send(command.encode('utf-8'))
        time.sleep(self.sleep_after_command)
        if command.endswith('?'):
            reply = self.s.recv(1000)
            #print(':: rx', reply)
            if decode_reply:
                reply = reply.decode('utf-8')  # pylint: disable=redefined-variable-type
            return reply

#
#

def SocketDevice(path):
    print(':', path)
    server, port = path.split(':')
    return Socket(server, int(port))

class SerialDevice(TenmaBase):
    """Driver for the Tenma 72-2540 power supply"""

#
#

class SerialDevice:
    """Driver for the Hanmatek HM305T power supply"""

    def __init__(self, path):
        f = serial.Serial(path, baudrate=9600, timeout=0.1)
        self.dev = HM305(f)
        self.dev.initialize()

    def set_output(self, on):
        if on:
            self.dev.on()
        else:
            self.dev.off()
    def set_voltage(self, v):
        self.dev.voltage.instrument_setpoint = v
    def set_current(self, i):
        self.dev.current.instrument_setpoint = i
    def get_actual_current(self):
        return self.dev.current.value
    def get_actual_voltage(self):
        return self.dev.voltage.value

    def set_overcurrent_protection(self, x):
        pass
    def set_overvoltage_protection(self, x):
        pass
    def recall_memory(self, m):
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
    p.add_argument('--path', dest='path', default='/dev/ttypsu2', help='/dev/ttyXXX or server:port')
    p.add_argument('commands', nargs='+', help='on off v=x i=x v+x v-x sleep=s m=x save loop repeat show monitor')
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

    if args.path.startswith('/'):
        # serial port
        device = SerialDevice(args.path)
    else:
        device = SocketDevice(args.path)

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
