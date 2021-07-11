#!/usr/bin/env python3

import tenma

def main():
    """Main module function, used for testing simple functional test"""
    device = tenma.Tenma722540('/dev/psu')
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
        for mv in range(0, 16000, 100):
            volts = mv / 1000.0
            device.set_voltage(volts)
            #sleep(1)
            it = device.get_actual_current()
            vt = device.get_actual_voltage()
            print(vt, it)
    except KeyboardInterrupt:
        pass

    print("Done")
    device.set_output(False)
    device.set_voltage(0.0)
    device.set_overcurrent_protection(False)
    device.set_overvoltage_protection(False)
    device.recall_memory(1)

main()

# FIN
