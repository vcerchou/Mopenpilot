import sys
from common.params import Params
params = Params()

def mp_rewrite_lateral_tuning(ret):
  if int(params.get("LatcontrolMod")) == 1:
    ret.lateralTuning.init('lqr')
    ret.lateralTuning.lqr.scale = 1500.0
    ret.lateralTuning.lqr.ki = 0.05
    ret.lateralTuning.lqr.a = [0., 1., -0.22619643, 1.21822268]
    ret.lateralTuning.lqr.b = [-1.92006585e-04, 3.95603032e-05]
    ret.lateralTuning.lqr.c = [1., 0.]
    ret.lateralTuning.lqr.k = [-110.73572306, 451.22718255]
    ret.lateralTuning.lqr.l = [0.3233671, 0.3185757]
    ret.lateralTuning.lqr.dcGain = 0.002237852961363602
  elif int(params.get("LatcontrolMod")) == 2:
    ret.lateralTuning.init('indi')
    ret.lateralTuning.indi.innerLoopGainBP = [0.]
    ret.lateralTuning.indi.innerLoopGainV = [4.0]
    ret.lateralTuning.indi.outerLoopGainBP = [0.]
    ret.lateralTuning.indi.outerLoopGainV = [3.0]
    ret.lateralTuning.indi.timeConstantBP = [0.]
    ret.lateralTuning.indi.timeConstantV = [1.0]
    ret.lateralTuning.indi.actuatorEffectivenessBP = [0.]
    ret.lateralTuning.indi.actuatorEffectivenessV = [1.0]
    ret.steerActuatorDelay = 0.3
  return ret

if __name__ == "__main__":
  sys.tracebacklimit=0
  car_folder = sys.argv[1]
  try:
    brand_name = car_folder.split("/")[-1]
    model_names = __import__("selfdrive.car.%s.values" % brand_name, fromlist=["CAR"]).CAR
    for c in sorted(model_names.__dict__.keys()):
      if not c.startswith("__"):
        print("%s" % getattr(model_names, c))
  except (ImportError, IOError):
    pass
