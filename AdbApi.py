#
# Joakim L. Johansson / mikaoj@gmail.com
#
from flask import Blueprint, abort
import os
from adb import adb_commands
from adb import sign_m2crypto
from adb import usb_exceptions

adb_api = Blueprint('adb_api', __name__)

@adb_api.route('/pcscf/<string:addr>', methods = ['POST'])
def set_pcscf(addr):
  try:
    signer = sign_m2crypto.M2CryptoSigner(os.path.expanduser('~/.android/adbkey'))
    device = adb_commands.AdbCommands()
    device.ConnectDevice(rsa_keys=[signer])
    device.Shell('am force-stop com.samsung.advp.imssettings')
    device.Shell('am start -n com.samsung.advp.imssettings/com.samsung.advp.imssettings.MainActivity')
    device.Shell('input tap 1165 1480') # Close buggy popup
    device.Shell('input tap 765 920')   # Open IMS Profile submenu
    device.Shell('input tap 765 400')   # Select TEL VOLTE profile
    device.Shell('input swipe 770 2500 770 1350 2000')   # Scroll down
    device.Shell('input tap 765 2160')  # Open P-CSCF settings
    device.Shell('input tap 180 725')   # Select All 1
    device.Shell('input tap 180 800')   # Select All 2
    device.Shell('input tap 193 600')   # Select All 3
    device.Shell('input text ' + addr) # Type new IP
    device.Shell('input tap 1200 955')  # Select OK
    device.Shell('input tap 765 2410')  # Open P-CSCF Preference
    device.Shell('input tap 1200 1265') # Select Manaual
    device.Shell('input tap 1160 210') # Save Button
    return "yay"
  except Exception as ex:
    print(ex)
    abort(500)
