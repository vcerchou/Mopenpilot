import cereal.messaging as messaging
from common.numpy_fast import interp

# 根据当前速度判断使用 [市区/低速模式] 还是 [高速模式]
# 45km/h ≈ 12.5 m/s
CITY_SPEED = 12.5
TF_DEFAULT = 1.45

class FollowingDistance():
  def __init__(self):
    self.desired_TF = TF_DEFAULT
    self.is_city_mode = False
    self.tr_btn_val = 4
    self.sm = messaging.SubMaster(['trButton'])

  def update_TF(self, carstate, tf_default=TF_DEFAULT):

    # update ui button value
    self.sm.update(0)
    if self.sm.updated['trButton']:
      self.tr_btn_val = self.sm['trButton'].val

    if self.tr_btn_val == 1:
      self.desired_TF = 1.0

    elif self.tr_btn_val == 2:
      if carstate.vEgo <= CITY_SPEED:
        self.desired_TF = 1.2
      else:
        self.desired_TF = 1.3

    elif self.tr_btn_val == 3:
      if carstate.vEgo <= CITY_SPEED:
        self.desired_TF = TF_DEFAULT
      else:
        self.desired_TF = 1.8

    else:
      self.desired_TF = max(tf_default, TF_DEFAULT)

    return self.desired_TF
