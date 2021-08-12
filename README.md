Automated Test Equipment
========================

Utilities to drive a Tenma 72-2540 bench supply over a serial port.

Examples :

select memory 5 : (note, the output is turned off by the psu when a memory is selected)

    ./psu.py -m=5

Overcurrent and overvoltage protection are enabled by default. Turn them off with the --overcurrent=0 or --overvoltage=0 options.

Set the supply to 16V, turn it on :

    ./psu.py v=16 on

You can save to the memory locations :

    ./psu.py m=3 v=12.0 i=2.0 save

Turn the unit on to 5V for 10 seconds

    ./psu.py v=5 on sleep=10 off

Turn the unit off for 2s, using the existing settings :

    ./psu.py off sleep=2 on

It has a very simple loop construct. You mark the start of the loop with 'loop' (defaults to the first command) and repeat on 'repeat'.

So, to set the supply to 5V and ramp down to 0V, do :

    ./psu.py v=5 on loop sleep=1 v-0.1 repeat

This will bail out when V reaches 0.0 by default, or you can set the minimum with eg. the --min-v=2.0 command.

The loop will also bail if it reaches the upper voltage limit set by --max-v=V

    ./psu.py --max-v=10 v=0 on loop sleep=1 v+0.5 repeat

You can continuously output the status using the 'monitor' command :

    ./psu.py monitor

All the commands print info starting with a ':', except the 'show' command, which prints time, voltage and current. This can be used to dump the data to a file, or plot it in real time.

    ./psu.py --overvoltage=0 --max-v=10 v=0 on loop sleep=0.1 show v+0.5 repeat | grep -v "^:"

There is an MQTT client available which sends JSON data to a named server / topic. This applies to the 'show' and 'monitor' commands.

    ./psu.py --mqtt server --topic ate/psu/0 monitor

The JSON data looks like this :

    {"V": 5.0, "I": 0.0}

FIN
