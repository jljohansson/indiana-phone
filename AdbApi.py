#
# Joakim L. Johansson / mikaoj@gmail.com
#
from flask import Blueprint, abort, request, json
import os
import yaml
from adb import adb_commands
from adb import sign_m2crypto
from adb import usb_exceptions

import logging
logging.basicConfig(level=logging.INFO)

adb_api = Blueprint('adb_api', __name__)

def run_shell_commands(shell_commands):
  try:
    signer = sign_m2crypto.M2CryptoSigner(os.path.expanduser('~/.android/adbkey'))
    device = adb_commands.AdbCommands()
    device.ConnectDevice(rsa_keys=[signer])
    for command in shell_commands:
      logging.info('shell=%s' % command['shell'])
      logging.info('description=%s' % command['description'])
      device.Shell(command['shell'])
  except Exception as ex:
    abort(500, str(ex))


@adb_api.route('/api', methods = ['GET'])
def api():
   return '''
GET /adb/api
POST /adb/shell
POST /adb/action/set-pcscf/profile
   '''

@adb_api.route('/action/<string:action>/<string:profile>', methods = ['POST'])
def action(action, profile):
  logging.info('action=%s profile=%s' % (action, profile))
  with open(profile + ".yaml", "r") as stream:
    try:
      data = yaml.load(stream)
      logging.info('loaded profile from %s' % (stream.name))
      action = data[action]
      sequence = action['sequence']
      data['sequence'] = run_shell_commands(sequence)
      return json.dumps(data)
    except Exception as ex:
      abort(500, str(ex))

@adb_api.route('/shell', methods = ['POST'])
def shell():
   data = request.get_json(force=True)
   data['sequence'] = run_shell_commands(data["sequence"])
   return json.dumps(data)

@adb_api.route('/dumpsys', defaults={'thing': ""}, methods = ['GET'])
@adb_api.route('/dumpsys/<string:thing>',          methods = ['GET'])
def dumpsys(thing):
   return "Thing is [" + thing + "]"
