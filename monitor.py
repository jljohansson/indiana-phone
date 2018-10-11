from pydbus import SystemBus
from gi.repository import GLib
import paho.mqtt.publish as publish
import json

def mqtt(topic, payload, hostname="127.0.0.1", retain=False):
   publish.single(topic, payload, hostname=hostname)

def prop(signal, params):
  return json.dumps({signal: {params[0]: params[1]}})

def cadd(signal, params):
  return json.dumps({signal: {"path": params[0], "props": params[1]}})

def crem(signal, params):
  return json.dumps({signal: {"path": params[0]}})

def dev(obj, iface):
  return obj.split('/')[-1] + '/' + iface.split('.')[-1]

def vcdev(obj, iface):
  return obj.split('/')[-2] + '/' + iface.split('.')[-1]


if __name__ == '__main__':

  bus = SystemBus()
  if_list = [
             ('org.ofono.Modem',               'PropertyChanged', lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), prop(signal, params))),
             ('org.ofono.VoiceCall',           'PropertyChanged', lambda _a, obj, iface, signal, params: mqtt(vcdev(obj, iface), prop(signal, params))),
             ('org.ofono.CallVolume',          'PropertyChanged', lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), prop(signal, params))),
             ('org.ofono.VoiceCallManager',    'PropertyChanged', lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), prop(signal, params))),
             ('org.ofono.VoiceCallManager',    'CallAdded',       lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), cadd(signal, params))),
             ('org.ofono.VoiceCallManager',    'CallRemoved',     lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), crem(signal, params))),
             ('org.ofono.NetworkRegistration', 'PropertyChanged', lambda _a, obj, iface, signal, params: mqtt(dev(obj, iface), prop(signal, params))),
            ]
  [bus.subscribe(iface=iface, signal=signal, signal_fired=cb) for iface, signal, cb in if_list]

  mqtt("monitor", payload="started", retain=True)

  loop = GLib.MainLoop()
  loop.run()
