from common.params import Params
from selfdrive.car.toyota.values import CAR as toyote_values

params = Params()

CAR_FP_CORRESPONDENCE = {
  toyote_values.RAV4_TW_SNG_TSS2: toyote_values.COROLLA_TSS2
}

def get_camera_offset():
  camera_offset = params.get("CameraOffset", encoding='utf8')
  if camera_offset is not None:
    camera_offset = int(camera_offset) * -0.01
  else:
    camera_offset = -0.06
  return camera_offset




