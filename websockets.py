#from gevent import monkey
#monkey.patch_all()

from flask import Flask, render_template, json
from flask_socketio import SocketIO, emit

from pydbus import SystemBus
from gi.repository import GLib
import threading
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')
#socketio = SocketIO(app)

#Message:  (':1.654', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', False))
#Data:  Powered

bus = SystemBus()

def cb_server_signal_emission(*args):

    print("Message: ", args)
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
        message = { 'source': 'network', 'event': 'property_change', 'device': makedev(args[1]), 'property': args[4][0], 'property_value': args[4][1] }
      else:
        message = {'unknown_signal': args }

    socketio.emit('message', json.dumps(message))


def dbus_monitor():
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
        socket.emit('connected', {data: 'Client connected!'});
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
def handle_my_custom_event(arg1):
    emit('message', {'data': 42})

if __name__ == '__main__':
  t = threading.Thread(target=dbus_monitor)
  t.daemon = True
  t.start()
  socketio.run(app, host='0.0.0.0', port=5001)



