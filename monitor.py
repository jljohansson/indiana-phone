from pydbus import SystemBus
from gi.repository import GLib
import json

import paho.mqtt.publish as publish

#Message:  (':1.654', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', False))
#Data:  Powered

def cb_PropertyChanged(*args):
   print("Message: ", args)
   #Message:  (':1.2', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', True))
   #Message:  (':1.2', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.NetworkRegistration', 'PropertyChanged', ('Status', 'registered'))
   dev   = args[1].split('/')[-1]
   iface = args[2].split('.')[-1]
   payload = json.dumps({'PropertyChanged': {args[4][0]: args[4][1]}})
   publish.single(dev, payload, hostname="127.0.0.1")

def cb_VoiceCallManager(*args):
   print("Message: ", args)
   dev   = args[1].split('/')[-1]
   signal = args[3]
   payload = json.dumps({signal: {args[4][0]: args[4][1]}})
   publish.single(dev, payload, hostname="127.0.0.1")

# Interfaces:
#  'org.ofono.Modem'
#  'org.ofono.NetworkRegistration'
#  'org.ofono.VoiceCallManager'
#  'org.ofono.VoiceCallManager'

if __name__ == '__main__':
  bus = SystemBus()
  bus.subscribe(iface = 'org.ofono.Modem',               signal='PropertyChanged', signal_fired = cb_PropertyChanged)
  bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal='PropertyChanged', signal_fired = cb_PropertyChanged)
  bus.subscribe(iface = 'org.ofono.CallVolume',          signal='PropertyChanged', signal_fired = cb_PropertyChanged)
  bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal='PropertyChanged', signal_fired = cb_PropertyChanged)
  
  bus.subscribe(iface = 'org.ofono.VoiceCallManager',   signal=None,  signal_fired = cb_VoiceCallManager)
#  bus.subscribe(iface = 'org.ofono.VoiceCall',          signal=None,  signal_fired = cb_VoiceCall)
  
  loop = GLib.MainLoop()
  publish.single("ofono", payload="running", hostname="127.0.0.1", retain=True)
  publish.single("ofono/2", payload="running2", hostname="127.0.0.1", retain=True)
  publish.single("ofono/3", payload="running3", hostname="127.0.0.1", retain=True)
  loop.run()
