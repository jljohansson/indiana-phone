#
# Joakim L. Johansson / mikaoj@gmail.com
#
from flask import Blueprint, abort, request, json
import os
from pydbus import SystemBus

import logging
logging.basicConfig(level=logging.DEBUG)

bluez_api = Blueprint('bluez_api', __name__)

@bluez_api.route('/adapters', methods = ['GET'])
def adapters():
  return json.dumps(all_adapters(), sort_keys=True, indent=4)

@bluez_api.route('/devices', methods = ['GET'])
def devices():
  #data = request.get_json(force=True)
  #data['commands'] = run_commands(data["commands"])
  #return json.dumps(data)
  return json.dumps(list(all_devices()), sort_keys=True, indent=4)


@bluez_api.route('/device/<path:path>', methods = ['GET'])
def device(path):
  print("path %s" % (path))
  #return json.dumps()
  return path

#@bluez_api.route('/dumpsys', defaults={'thing': ""}, methods = ['GET'])
#@bluez_api.route('/dumpsys/<string:thing>',          methods = ['GET'])
#def dumpsys(thing):
#   return "Thing is [" + thing + "]"

def all_adapters():
  bus = SystemBus()
  bluez = bus.get("org.bluez", "/")
  adapters = { k: v['org.bluez.Adapter1'] for k, v in bluez.GetManagedObjects().items() if 'org.bluez.Adapter1' in v}
  logging.info('all_adapters() -> %s' % list(adapters.keys()))
  return adapters

def all_devices():
  bus = SystemBus()
  bluez = bus.get("org.bluez", "/")
  devices = { k: v['org.bluez.Device1'] for k, v in bluez.GetManagedObjects().items() if 'org.bluez.Device1' in v}
  logging.info('all_devices() -> %s' % list(devices.keys()))
  return devices