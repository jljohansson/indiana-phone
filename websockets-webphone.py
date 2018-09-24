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

bus = SystemBus()
ofono = bus.get('org.ofono', '/')


#Message:  (':1.654', '/hfp/org/bluez/hci0/dev_94_65_2D_84_61_99', 'org.ofono.Modem', 'PropertyChanged', ('Powered', False))
class DbusMonitor(Thread):

  def run(self):
    bus = SystemBus()
    bus.subscribe(iface = 'org.freedesktop.DBus.ObjectManager', signal_fired = self.cb_bluez_signal)
    bus.subscribe(iface = 'org.ofono.Modem',               signal_fired = self.cb_ofono_signal)
    bus.subscribe(iface = 'org.ofono.NetworkRegistration', signal_fired = self.cb_ofono_signal)
    bus.subscribe(iface = 'org.ofono.VoiceCallManager',    signal_fired = self.cb_ofono_signal)
    bus.subscribe(iface = 'org.ofono.VoiceCall',           signal_fired = self.cb_ofono_signal)
    loop = GLib.MainLoop()
    loop.run()

  def __init__(self):
    super(DbusMonitor, self).__init__()

  def cb_bluez_signal(*args):
    print("BLUEZ: ", args)
    iface = args[3]
    event = args[4]
    if 'InterfacesAdded' in event:
      props = args[5][1]['org.bluez.Device1']
      socketio.emit('device_added', {'device': args[5][0], 'name': props['Name'], 'name': props['Name'], 'connected': props['Connected'],'trusted': props['Trusted'],'address': props['Address'] })
    elif 'InterfacesRemoved' in event:
      socketio.emit('device_removed', {'device': args[5][0]})

  def cb_ofono_signal(*args):
    print("OFONO: ", args)
    iface = args[3]
    event = args[4]
    print(iface)
    makedev = lambda path : path.split('/')[-1]
    if 'PropertyChanged' in event and 'Strength' in args[5][0]:
      socketio.emit('strength', args[5][1])
    elif 'PropertyChanged' in event and 'Powered' in args[5][0]:
      socketio.emit('powered', args[5][1])
    elif 'PropertyChanged' in event and 'Online' in args[5][0]:
      socketio.emit('online', args[5][1])
    elif 'PropertyChanged' in event:
      pass
    elif 'CallAdded' in event:
      message = { 'source': iface, 'event': 'call_added', 'device': makedev(args[2]), 'properties': args[5][1] }
    elif 'CallRemoved' in event:
      message = { 'source': iface, 'event': 'call_removed', 'device': makedev(args[2]) }
    elif 'DisconnectReason' in event:
      message = { 'source': iface, 'event': 'call_disconnect', 'device': makedev(args[2]), 'disconnector': args[5][0] }


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
    socket.on('device_added', function(device) { console.log('device_added: ' + JSON.stringify(device)) });
    socket.on('device_removed', function(device) { console.log('device_removed: ' + JSON.stringify(device)) });
    socket.on('strength', function(strength) { document.getElementById("strength").value = strength; });    
    socket.on('powered', function(powered) { document.getElementById("powered").value = powered; });    
    socket.on('online', function(online) { document.getElementById("online").value = online; });    
	</script>
  <script>
function makeTheCall(device, number)
{
    var url = 'http://192.168.0.201:5001/' + device + '/dial/' + number;
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "POST", url, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

  </script>
  </head>
  <body>
    <label for="strength">Strength:</label><input id="strength" type="text" value="N/A"><br>
    <label for="powered">Powered:</label><input id="powered" type="text" value="N/A"><br>
    <label for="online">Online:</label><input id="online" type="text" value="N/A"><br>
    <div>
      <label for="list">Phone number:</label>
      <select id="list" onchange="document.getElementById('displayValue').value=this.options[this.selectedIndex].text; document.getElementById('idValue').value=this.options[this.selectedIndex].value;">
        <option></option>
        <option value="+61459868975">+61459868975</option>
      </select>
      <input name="displayValue" placeholder="add/select a value" id="displayValue" onfocus="this.select()" type="text">
      <input name="idValue" id="idValue" type="hidden">
     </div>
     <button onclick="makeTheCall('dev_94_65_2D_84_61_99', '+61459868975')">Call</button>
     <br>
     <label for="status">Status:</label><input id="status" type="text" value="N/A"><br>
    <textarea id="logbox" width="100" rows="10"></textarea>
    <br>
    <button onclick="document.getElementById('logbox').value='';">Clear</button>
  </body>
</html>
''' 

@app.route('/devices', methods = ['GET'])
def get_devices():
  try:
    devices = ofono.GetModems()
  except Exception as ex:
    print(ex)
    abort(500)
  cropdevice = lambda d : d.replace('/hfp/org/bluez/hci0/', '')  # yay, Lambda!
  return  jsonify({'devices': [{'device': cropdevice(dev), 'properties':props} for dev, props in devices]})


@app.route('/<string:device>/dial/<string:number>', methods = ['POST'])
def dial_number(device, number):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    path = vcm.Dial(number, "default")
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return make_response(jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]}), 201)


@app.route('/<string:device>/calls', methods = ['GET'])
def get_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]})


@app.route('/<string:device>/hangup', methods = ['POST'])
def hangup_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    vcm.HangupAll()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': []})


@app.route('/<string:device>/answer', methods = ['GET', 'POST'])
def answer_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    vcm.ReleaseAndSwap()
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]})



@socketio.on('connect', namespace='/')
def test_connect():
    print('connect')
    emit('my response', {'data': 'Connected'})

if __name__ == '__main__':
  thread = DbusMonitor()
  thread.daemon = True
  thread.start()
  socketio.run(app, host='0.0.0.0', port=5001)
