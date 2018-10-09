#
# Joakim L. Johansson / mikaoj@gmail.com
#
from flask import Blueprint, abort, request, json
import os
from adb import adb_commands
from adb import sign_m2crypto
from adb import usb_exceptions

import logging
logging.basicConfig(level=logging.DEBUG)

adb_api = Blueprint('adb_api', __name__)

def run_commands(commands):
   return [run_command(command) for command in commands]

def run_command(command):
  logging.debug('command=%s' % command)
  try:
    signer = sign_m2crypto.M2CryptoSigner(os.path.expanduser('~/.android/adbkey'))
    device = adb_commands.AdbCommands()
    device.ConnectDevice(rsa_keys=[signer])
    output = device.Shell(command["command"])
    logging.debug('output=%s' % output)
    command["output"] = output
    return command
  except Exception as ex:
    abort(500, str(ex))

@adb_api.route('/shell', methods = ['POST'])
def shell():
   data = request.get_json(force=True)
   data['commands'] = run_commands(data["commands"])
   return json.dumps(data)

@adb_api.route('/dumpsys', defaults={'thing': ""}, methods = ['GET'])
@adb_api.route('/dumpsys/<string:thing>',          methods = ['GET'])
def dumpsys(thing):
   return "Thing is [" + thing + "]"
