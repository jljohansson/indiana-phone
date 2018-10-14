from pydbus import SystemBus
from gi.repository import GLib

import logging
logging.basicConfig(level=logging.DEBUG)


def handle_interface_added(_a, obj, iface, signal, params):
  logging.debug('handle_interface_added: %s' % str(params))
  if 'org.bluez.Device1' in params[1]:  # is this a Device1?
    device = params[1]['org.bluez.Device1']
    logging.debug('Name=%s' % device['Name'])
    logging.debug('Address=%s' % device['Address'])
    logging.debug('Connected=%s' % device['Connected'])
    logging.debug('Paired=%s' % device['Paired'])
    logging.debug('Blocked=%s' % device['Blocked'])
    logging.debug('ServicesResolved=%s' % device['ServicesResolved'])

def handle_interface_removed(_a, obj, iface, signal, params):
  logging.debug('handle_interface_removed')
  logging.debug('Device=%s' % params[0])

def cb(a, obj, iface, signal, params):
  logging.debug('signal=%s' % str(signal))
  logging.debug('obj=%s'    % str(obj))
  logging.debug('iface=%s'  % str(iface))
  logging.debug('params=%s' % str(params))

def get_devices():
  bus = SystemBus()
  bluez =  bus.get('org.bluez', '/')
  mobjs = bluez.GetManagedObjects()
  devices = { k: v['org.bluez.Device1'] for k,v in mobjs.items() if 'org.bluez.Device1' in v }
  return devices

def forget_device(dev):
  logging.debug('forget_device(%s)' % str(dev))
  bus = SystemBus()
  adapter = bus.get('org.bluez', '/org/bluez/hci0')
  adapter.RemoveDevice(dev)
  return True  

def setup_adapter():
  bus = SystemBus()
  adapter = bus.get('org.bluez', '/org/bluez/hci0')
  adapter.Discoverable = True
  if adapter.Discovering: adapter.StopDiscovery()

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

if __name__ == '__main__':

  setup_adapter()

  [forget_device(d) for d in get_devices()]

  bus = SystemBus()
 
  bus.subscribe(iface='org.freedesktop.DBus.ObjectManager', signal='InterfacesAdded', signal_fired=handle_interface_added)
  bus.subscribe(iface='org.freedesktop.DBus.ObjectManager', signal='InterfacesRemoved', signal_fired=handle_interface_removed)

  bus.subscribe(iface='org.freedesktop.DBus.Properties', signal='PropertiesChanged', signal_fired=cb)
  bus.subscribe(iface='org.freedesktop.DBus.ObjectManager', signal='PropertiesChanged', signal_fired=cb)
  bus.subscribe(iface='org.bluez.Adapter1', signal_fired=cb)
  bus.subscribe(iface='org.bluez.AgentManager1', signal_fired=cb)
  bus.subscribe(iface='org.bluez.Device1', signal_fired=cb)
  bus.subscribe(iface='org.bluez', signal_fired=cb)
  bus.subscribe(iface='org.bluez.Manager', signal_fired=cb)
  loop = GLib.MainLoop()
  loop.run()

