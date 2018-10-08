#
# Joakim L. Johansson / mikaoj@gmail.com
#
from flask import Blueprint
from flask import Flask, jsonify, abort, json, request, make_response
from pydbus import SystemBus

ofono_api = Blueprint('ofono_api', __name__)

bus = SystemBus()
ofono = bus.get('org.ofono', '/')

@ofono_api.route('/devices', methods = ['GET'])
def get_devices():
  try:
    devices = ofono.GetModems()
  except Exception as ex:
    print(ex)
    abort(500)
  cropdevice = lambda d : d.replace('/hfp/org/bluez/hci0/', '')  # yay, Lambda!
  return  jsonify({'devices': [{'device': cropdevice(dev), 'properties':props} for dev, props in devices]})


@ofono_api.route('/<string:device>/dial/<string:number>', methods = ['POST'])
def dial_number(device, number):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    path = vcm.Dial(number, "default")
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return make_response(jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]}), 201)


@ofono_api.route('/<string:device>/calls', methods = ['GET'])
def get_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]})


@ofono_api.route('/<string:device>/hangup', methods = ['POST'])
def hangup_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    vcm.HangupAll()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': []})


@ofono_api.route('/<string:device>/answer', methods = ['GET', 'POST'])
def answer_call(device):
  try:
    vcm = bus.get('org.ofono', '/hfp/org/bluez/hci0/' + device)
    vcm.ReleaseAndSwap()
    calls = vcm.GetCalls()
  except Exception as ex:
    print(ex)
    abort(500)
  return jsonify({'device': device, 'calls': [{'path': path, 'properties': props} for path, props in calls]})

