#from gevent import monkey
#monkey.patch_all()

from flask import Flask, render_template, json
from flask_socketio import SocketIO, emit
import json

import sys
import tdbus
import gevent
if not hasattr(tdbus, 'GEventDBusConnection'):
    print('gevent is not available on this system')
    sys.exit(1)


from tdbus import GEventDBusConnection, DBUS_BUS_SYSTEM, signal_handler, DBusHandler, method

async_mode = "threading"  # None | "threading" | "eventlet" | "gevent"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

#Message:  (':1.654', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', False))
#Data:  Powered

class GEventHandler(DBusHandler):

  @signal_handler()
  def PropertyChanged(self, message):
         print('signal received: %s, args = %s' % (message.get_member(), repr(message.get_args())))
         socketio.emit('message', json.dumps(message))

  @method(interface="org.ofono.NetworkRegistration")
  def PropertyChangedMethod(self, message):
      print('signal received: %s, args = %s' % (message.get_member(), repr(message.get_args())))


print("hhere!")
conn = GEventDBusConnection(DBUS_BUS_SYSTEM)
print("hhere2!")
handler = GEventHandler()
print("hhere3!")

conn.add_handler(handler)
conn.subscribe_to_signals()
print("hhere4!")
from gevent.hub import get_hub
try:
    get_hub().switch()
except KeyboardInterrupt:
    pass


def cb_server_signal_emission(*args):

    print("Message3: ", args)
    makedev = lambda path : path.split('/')[-1]
    iface = args[2]

    if 'org.ofono.Modem' in iface:
      if 'PropertyChanged' in args[3]:
        message = { 'source': 'modem', 'event': 'property_change', 'device': makedev(args[1]), 'property': args[4][0], 'property_value': args[4][1] }
      else:
        message = {'unknown_signal': args }

    elif 'org.ofono.NetworkRegistration' in iface:
      if 'PropertyChanged' in args[3]:
        message = { 'source': 'network', 'event': 'property_change', 'device': makedev(args[1]), 'property': args[4][0], 'property_value': args[4][1] }
      else:
        message = {'unknown_signal': args }

    elif 'ofono.VoiceCallManager' in iface:
      if 'CallAdded' in args[3]:
        message = { 'source': 'callmgr', 'event': 'call_added', 'device': makedev(args[1]), 'properties': args[4][1] }
      elif 'CallRemoved' in args[3]:
        message = { 'source': 'callmgr', 'event': 'call_removed', 'device': makedev(args[1]) } 
      else:
        message = {'unknown_signal': args }

    elif 'ofono.VoiceCall' in iface:
      if 'PropertyChanged' in args[3]:
        message = { 'source': 'call', 'event': 'property_change', 'device': makedev(args[1]), 'property': args[4][0], 'property_value': args[4][1] }
      else:
        message = {'unknown_signal': args }

    socketio.emit('message', json.dumps(message))


def dbus_monitor():
  bus = SystemBus()
  bus.subscribe(iface = 'org.ofono.Modem',
                signal_fired = cb_server_signal_emission)
  bus.subscribe(iface = 'org.ofono.NetworkRegistration',
                signal_fired = cb_server_signal_emission)
  print(bus)
  bus.subscribe(iface = 'org.ofono.VoiceCallManager',
                signal_fired = cb_server_signal_emission)
  print(bus)
  bus.subscribe(iface = 'org.ofono.VoiceCall',
                signal_fired = cb_server_signal_emission)    
  loop = GLib.MainLoop()
  loop.run()

@app.route('/')
def index():
  return '''
<html>
<head>
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
<script type="text/javascript" charset="utf-8">
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        console.log('connect');
        socket.emit('my event', {data: 'Client connected!'});
    });
    socket.on('message', function(message) {
       console.log('The server has a message for you: ' + message);
       var t = document.getElementById("logbox");
       t.value = t.value + 'MESSAGE: ' + message + '\\n';
    });
</script>
</head>
<body>
<textarea id="logbox" width="100" rows="10"></textarea>
<br>
<button onclick="document.getElementById('logbox').value='';">Clear</button>
</body>
</html>
''' 



@socketio.on('my event')
def handle_connect(message):
  emit('message', {'data': 'Connected'})

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

if __name__ == '__main__':
  socketio.run(app, debug=True, host='0.0.0.0', port=5001)



