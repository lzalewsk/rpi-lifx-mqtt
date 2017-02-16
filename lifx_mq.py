#!/usr/bin/env python

from lifxlan import *
import paho.mqtt.client as mqtt
import json
import time

#class LifxBulbs():
#class Sonos():

COLORS = {
    "red": RED,
    "orange": ORANGE,
    "yellow": YELLOW,
    "green": GREEN,
    "cyan": CYAN,
    "blue": BLUE,
    "purple": PURPLE,
    "pink": PINK,
    "white": WHITE,
    "cold_white": COLD_WHITE,
    "warm_white": WARM_WHITE,
    "gold": GOLD
}

DEVICE_LABEL = {
    'd0:73:d5:21:8c:b6' : 'L1',
    'd0:73:d5:21:56:5a' : 'L2'
}

LIFX_BULBS = {}

def lifx_power_on(mOpt):
    color = None
    if mOpt['options'].has_key('collor'):
        if mOpt['options']['collor'].lower() in COLORS:
            color = COLORS[mOpt['options']['collor'].lower()]
    else:
        color = COLORS['white']

    if mOpt['device'] == 'ALL':
        lifxlan = LifxLAN()
	lifxlan.set_color_all_lights(color, rapid=True)
        lifxlan.set_power_all_lights("on", rapid=True)
    else:
	if LIFX_BULBS.has_key(mOpt['device']):
	    light = Light( LIFX_BULBS[mOpt['device']]['mac'], LIFX_BULBS[mOpt['device']]['ip'])
	    light.set_color(color)
	    #Power On
	    light.set_power(1)

def lifx_power_off(mOpt):
    if mOpt['device'] == 'ALL':
        lifxlan = LifxLAN()
        lifxlan.set_power_all_lights("off", rapid=True)
    else:
	if LIFX_BULBS.has_key(mOpt['device']):
	    light = Light( LIFX_BULBS[mOpt['device']]['mac'], LIFX_BULBS[mOpt['device']]['ip'])
	    light.set_power(0)

def lifx_set_brightness(mOpt):
    if mOpt['device'] != 'ALL':
        if LIFX_BULBS.has_key(mOpt['device']):
            light = Light( LIFX_BULBS[mOpt['device']]['mac'], LIFX_BULBS[mOpt['device']]['ip'])
            light.set_brightness(mOpt['options']['brightness'])

def lifx_alarm():
    lifxlan = LifxLAN()
    lifxlan.set_color_all_lights(WARM_WHITE, rapid=True)
    lifxlan.set_waveform_all_lights(1,RED,1000,10,-20000,3)

# Rainbow
def lifx_rainbow():
    lifx = LifxLAN()

    original_colors = lifx.get_color_all_lights()
    original_powers = lifx.get_power_all_lights()

    print("Turning on all lights...")
    lifx.set_power_all_lights(True)
    sleep(1)

    print("Flashy fast rainbow")
    rainbow(lifx, 0.1)

    print("Smooth slow rainbow")
    rainbow(lifx, 1, smooth=True)

    print("Restoring original color to all lights...")
    for light, color in original_colors:
        light.set_color(color)

    sleep(1)

    print("Restoring original power to all lights...")
    for light, power in original_powers:
        light.set_power(power)


def rainbow(lan, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs*1000 if smooth else 0
    rapid = True if duration_secs < 1 else False
    for color in colors:
        lan.set_color_all_lights(color, transition_time_ms, rapid)
        sleep(duration_secs)



#######################################

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("showroom/controll")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    #Message definition
    #system,dev,command,optins
    #{'device': 'name or MAC', 'command': 'POWER_ON', 'system': 'LIFX', 'options': {'saturation': 100, 'collor': 'RED'}}
    #{"device": "L1", "command": "power_off", "system": "LIFX", "options": {"collor": "RED", "time": 399}}
    #jsb = json.dumps(msg) from src perspective
    #to m = json.loads(str)
    m = json.loads(msg.payload)
    if m['system'] == 'LIFX':
        if m.has_key('command'):
	    if m['command'] == 'rainbow':
	        lifx_rainbow()
	    if m['command'] == 'alarm':
	        lifx_alarm() 
	    if m['command'] == 'power_on':
	        lifx_power_on(m)
	    if m['command'] == 'power_off':
	        lifx_power_off(m)
        if m['options'].has_key('brightness'):
	    lifx_set_brightness(m)
    else:
	print 'JO Yhy'

def main():
    global LIFX_BULBS

    lifxlan = LifxLAN()
    devices = lifxlan.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
	dev = {}
	dev['ip'] = d.get_ip_addr()
	mac = d.get_mac_addr()
	dev['mac'] = mac
	LIFX_BULBS[DEVICE_LABEL[mac]] = dev
    print LIFX_BULBS

    client = mqtt.Client()
    client.username_pw_set('<user>', '<pass>')
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("<mqtt.server>", <port>, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == "__main__":
    try:
	main()

    #Ctrl C
    except KeyboardInterrupt:
        print "Cancelled"

    #Error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    #if it finishes or Ctrl C, shut it down
    finally:
        print "Finnaly...Exit"

    print "Done"

