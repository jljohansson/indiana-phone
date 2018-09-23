from flask import Flask, json
from flask_socketio import SocketIO, emit
from pydbus import SystemBus
from gi.repository import GLib
from threading import Thread
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

async_mode = "threading"  # None | "threading" | "eventlet" | "gevent"
socketio = SocketIO(app, async_mode=async_mode)

#Message:  (':1.654', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', False))

class DbusMonitor(Thread):

  def run(self):
    bus = SystemBus()
    bus.subscribe(iface = 'org.ofono.Modem',               signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.VoiceCallManager',    signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.VoiceCall',           signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.CallVolume',          signal_fired = self.cb_server_signal_emission)
    loop = GLib.MainLoop()
    loop.run()

  def __init__(self):
    super(DbusMonitor, self).__init__()

  def cb_server_signal_emission(*args):
    print("Message: ", args)
    iface = args[3]
    event = args[4]
    print(iface)
    makedev = lambda path : path.split('/')[-1]
    if 'PropertyChanged' in event:
      message = { 'source': iface, 'event': 'property_change', 'device': makedev(args[2]), 'property': args[5][0], 'property_value': args[5][1] }
    elif 'CallAdded' in event:
      message = { 'source': iface, 'event': 'call_added', 'device': makedev(args[2]), 'properties': args[5][1] }
    elif 'CallRemoved' in event:
      message = { 'source': iface, 'event': 'call_removed', 'device': makedev(args[2]) }
    socketio.emit('message', json.dumps(message))


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

@socketio.on('connect', namespace='/')
def test_connect():
    print('connect')
    emit('my response', {'data': 'Connected'})

if __name__ == '__main__':
  thread = DbusMonitor()
  thread.start()
  socketio.run(app, host='0.0.0.0', port=5001)
