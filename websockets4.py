import socketio
import eventlet
from flask import Flask, render_template

from pydbus import SystemBus
from gi.repository import GLib
from threading import Thread
import json

sio = socketio.Server()
print(sio)
app = Flask(__name__)

class DbusMonitor(Thread):
  def run(self):
    bus = SystemBus()
    bus.subscribe(iface = 'org.ofono.Modem',               signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.VoiceCallManager',    signal_fired = self.cb_server_signal_emission)
    bus.subscribe(iface = 'org.ofono.VoiceCall',           signal_fired = self.cb_server_signal_emission)
    loop = GLib.MainLoop()
    loop.run()

  def __init__(self):
    super(DbusMonitor, self).__init__()

  def cb_server_signal_emission(*args):
    print(sio)
    print("Message: ", args)
    makedev = lambda path : path.split('/')[-1]
    if 'PropertyChanged' in args[4]:
      message = { 'source': args[3] , 'event': 'property_change', 'device': makedev(args[2]), 'property': args[5][0], 'property_value': args[5][1] }
    elif 'CallAdded' in args[4]:
      message = { 'source': args[3], 'event': 'call_added', 'device': makedev(args[2]), 'properties': args[5][1] }
    elif 'CallRemoved' in args[4]:
      message = { 'source': args[3], 'event': 'call_removed', 'device': makedev(args[2]) }
    socketio.emit('message23', 'test')


@app.route('/')
def index():
  text = '''
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
  return text

@sio.on('connect')
def connect(sid, environ):
    print('connect ', sid)

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

#@socketio.on('my event')
#def handle_my_custom_event(arg1):
#    emit('message', {'data': 42})

if __name__ == '__main__':
  thread = DbusMonitor()
  thread.start()
  app = socketio.Middleware(sio, app)
  eventlet.wsgi.server(eventlet.listen(('', 5001)), app)



