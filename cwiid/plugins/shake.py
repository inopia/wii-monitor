import wmplugin
import cwiid
import math
from time import time

acc_zero = None
acc_one = None
acc = [0,0,0]

old_time=0

NEW_AMOUNT = 0.1
OLD_AMOUNT = 1 - NEW_AMOUNT

Roll_Scale = 1
Pitch_Scale = 1
X_Scale = 1
Y_Scale = 1

def wmplugin_info():
  return ["Shake"], [], []

def wmplugin_init(id, wiimote):
  global acc_zero, acc_one

  wmplugin.set_rpt_mode(id, cwiid.RPT_ACC)
  acc_zero, acc_one = wiimote.get_acc_cal(cwiid.EXT_NONE)
  return

def wmplugin_exec(mesg):
  global acc_zero, acc_one, acc, old_time

  shaken = False

  for m in mesg:
    if m[0] == cwiid.MESG_ACC:
      acc = [NEW_AMOUNT*(new-zero)/(one-zero) + OLD_AMOUNT*old
             for old,new,zero,one in zip(acc,m[1],acc_zero,acc_one)]
      a = math.sqrt(sum(map(lambda x: x**2, acc)))

#      roll = math.atan(acc[cwiid.X]/acc[cwiid.Z])
#      if acc[cwiid.Z] <= 0:
#        if acc[cwiid.X] > 0: roll += math.pi
#        else: roll -= math.pi

#      pitch = math.atan(acc[cwiid.Y]/acc[cwiid.Z]*math.cos(roll))
      if a < 0.2:
        shaken = True

#      if (a > 3.75) and ((old_time + 1.5) < time()):
#        old_time = time()
#        shaken=True

#      print a, old_time, time(), "\r",
  return [shaken], []

