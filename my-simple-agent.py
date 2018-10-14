from optparse import OptionParser
import sys

from pydbus import SystemBus
from gi.repository import GLib

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"


bus = None
device_obj = None
dev_path = None

### bluezutils
SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

def get_managed_objects():
  bus = SystemBus()
  obj = bus.get("org.bluez", "/")
  manager = obj["org.freedesktop.DBus.ObjectManager"]
  return manager.GetManagedObjects()

def find_adapter(pattern=None):
  return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_in_objects(objects, pattern=None):
  bus = SystemBus()
  for path, ifaces in objects.iteritems():
    adapter = ifaces.get(ADAPTER_INTERFACE)
    if adapter is None:
      continue
    if not pattern or pattern == adapter["Address"] or path.endswith(pattern):
      obj = bus.get(SERVICE_NAME, path)
      return obj[ADAPTER_INTERFACE]
  raise Exception("Bluetooth adapter not found")

def find_device(device_address, adapter_pattern=None):
  return find_device_in_objects(get_managed_objects(), device_address, adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
  bus = SystemBus()
  path_prefix = ""
  if adapter_pattern:
    adapter = find_adapter_in_objects(objects, adapter_pattern)
    path_prefix = adapter.object_path
  for path, ifaces in objects.iteritems():
    device = ifaces.get(DEVICE_INTERFACE)
    if device is None:
      continue
    if (device["Address"] == device_address and
            path.startswith(path_prefix)):
      obj = bus.get(SERVICE_NAME, path)
      return obj[DEVICE_INTERFACE]

  raise Exception("Bluetooth device not found")

###simple-agent

def ask(prompt):
  try:
    return raw_input(prompt)
  except:
    return input(prompt)

def set_trusted(path):
  dev = bus.get("org.bluez", path)
  dev.Trusted = True
  print("EJOJMJN: Trusted is True")

def dev_connect(path):
  dev = bus.get("org.bluez", path)
  print("EJOJMJN: Connecting path %s" % (s))
  dev.Connect()


class Rejected(Exception):
  _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(object):
  dbus = \
    """
    <node>
      <interface name='org.bluez.Agent1'>
        <method name='Release'>
          <arg type='' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='AuthorizeService'>
          <arg type='os' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='RequestPinCode'>
          <arg type='o' name='a' direction='in'/>
          <arg type='s' name='response' direction='out'/>
        </method>
        <method name='RequestPasskey'>
          <arg type='o' name='a' direction='in'/>
          <arg type='u' name='response' direction='out'/>
        </method>
        <method name='DisplayPasskey'>
          <arg type='ouq' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='DisplayPinCode'>
          <arg type='os' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='RequestConfirmation'>
          <arg type='ou' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='RequestAuthorization'>
          <arg type='o' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
        <method name='Cancel'>
          <arg type='' name='a' direction='in'/>
          <arg type='' name='response' direction='out'/>
        </method>
      </interface>
    </node>
    """


  def __init__(self):
    self.exit_on_release = True

  def Release(self):
    print("Release")
    if self.exit_on_release:
      mainloop.quit()

  def AuthorizeService(self, device, uuid):
    print("AuthorizeService (%s, %s)" % (device, uuid))
    authorize = ask("Authorize connection (yes/no): ")
    if (authorize == "yes"):
      return
    raise Rejected("Connection rejected by user")

  def RequestPinCode(self, device):
    print("RequestPinCode (%s)" % (device))
    set_trusted(device)
    return ask("Enter PIN Code: ")

  def RequestPasskey(self, device):
    print("RequestPasskey (%s)" % (device))
    set_trusted(device)
    passkey = ask("Enter passkey: ")
    return dbus.UInt32(passkey)

  def DisplayPasskey(self, device, passkey, entered):
    print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

  def DisplayPinCode(self, device, pincode):
    print("DisplayPinCode (%s, %s)" % (device, pincode))

  def RequestConfirmation(self, device, passkey):
    print("RequestConfirmation (%s, %06d)" % (device, passkey))
    confirm = ask("Confirm passkey (yes/no): ")
    if (confirm == "yes"):
      set_trusted(device)
      return
    raise Rejected("Passkey doesn't match")

  def RequestAuthorization(self, device):
    print("RequestAuthorization (%s)" % (device))
    auth = ask("Authorize? (yes/no): ")
    if (auth == "yes"):
      return
    raise Rejected("Pairing rejected")

  def Cancel(self):
    print("Cancel")

  def set_exit_on_release(self, exit_on_release):
    self.exit_on_release = exit_on_release



def pair_reply():
  print("Device paired")
  set_trusted(dev_path)
  dev_connect(dev_path)
  mainloop.quit()

def pair_error(error):
  err_name = error.get_dbus_name()
  if err_name == "org.freedesktop.DBus.Error.NoReply" and device_obj:
    print("Timed out. Cancelling pairing")
    device_obj.CancelPairing()
  else:
    print("Creating device failed: %s" % (error))
  mainloop.quit()


if __name__ == '__main__':

  bus = SystemBus()

  capability = "KeyboardDisplay"

  parser = OptionParser()
  parser.add_option("-i", "--adapter", action="store", type="string", dest="adapter_pattern", default=None)
  parser.add_option("-c", "--capability", action="store", type="string", dest="capability")
  parser.add_option("-t", "--timeout", action="store", type="int", dest="timeout", default=60000)
  (options, args) = parser.parse_args()
  if options.capability:
    capability  = options.capability

  path = "/test/agent"
#  agent = Agent(bus, path)
  agent = Agent()
  bus.publish("org.bluez.Agent1", Agent())
  
  mainloop = GLib.MainLoop()

  obj = bus.get(BUS_NAME, "/org/bluez")
  manager = obj['org.bluez.AgentManager1']
  manager.RegisterAgent(path, capability)

  print("Agent registered")

  # Fix-up old style invocation (BlueZ 4)
  if len(args) > 0 and args[0].startswith("hci"):
    options.adapter_pattern = args[0]
    del args[:1]

  if len(args) > 0:
    print("here1")
    device = find_device(args[0], options.adapter_pattern)
    dev_path = device.object_path
    agent.set_exit_on_release(False)
    device.Pair(reply_handler=pair_reply, error_handler=pair_error, timeout=60000)
    device_obj = device
  else:
    manager.RequestDefaultAgent(path)

#  bus.publish("org.bluez.Agent1", (path, agent))
  mainloop.run()

  #adapter.UnregisterAgent(path)
  #print("Agent unregistered")
