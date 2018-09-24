from pydbus import SystemBus
from gi.repository import GLib
from threading import Thread
import json

class DbusMonitor(Thread):

  def run(self):
    bus = SystemBus()
    bus.subscribe(iface = 'org.freedesktop.DBus.ObjectManager', signal_fired = self.cb_signal)
    bus.subscribe(iface = 'org.ofono.Modem',               signal_fired = self.cb_signal)
    bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal_fired = self.cb_signal)
    bus.subscribe(iface = 'org.ofono.VoiceCallManager',    signal_fired = self.cb_signal)
    bus.subscribe(iface = 'org.ofono.VoiceCall',           signal_fired = self.cb_signal)
    loop = GLib.MainLoop()
    loop.run()

  def __init__(self):
    super(DbusMonitor, self).__init__()

  def cb_signal(*args):
    print("SIGNAL: ", args[2:])

if __name__ == '__main__':
  thread = DbusMonitor()
  thread.daemon = False
  thread.start()
