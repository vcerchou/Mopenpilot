# -*- coding:utf-8 -*-

import time
import json
import jwt
import requests
import _thread

from common.params import Params
from common.basedir import PERSIST
from selfdrive.swaglog import cloudlog
import cereal.messaging as messaging
from common.realtime import Ratekeeper
from common.conversions import Conversions as CV
from selfdrive.hardware.eon.hardware import getprop


class TrafficAssist:

  def __init__(self):
    self.params = Params()
    self.dongle_id = self.params.get("DongleId", encoding='utf8')
    self.is_traffic_assist = self.params.get_bool("IsTrafficAssist")

    self.pm = messaging.PubMaster(['trafficAssist'])
    self.sm = messaging.SubMaster(['carState', 'controlsState', 'gpsLocationExternal'])

    self.public_key = ""
    self.private_key = ""

    self.map_network = False
    self.enabled = False

    self.v_ego = 0
    self.latitude = 0
    self.longitude = 0

    self.state = 0  # 0-not speed limit 1-have speed limit no control 2-have speed limit to control
    self.speed_limit = 0
    self.road_name = ''

  def get_locale(self):
    return getprop("persist.sys.locale")

  def api_get(self, endpoint, method='GET', timeout=None, access_token=None, **params):
    resp = None
    try:
      # backend = "http://49.158.167.27:8881/mpmap/"
      backend = "https://twmp.myclouds.ai/mpmap/"

      headers = {}
      if access_token is not None:
        headers['Authorization'] = "JWT "+access_token

      headers['User-Agent'] = "MyPilot-Map"
      resp = requests.request(method, backend+endpoint, timeout=timeout, headers=headers, params=params)
    except Exception:
      self.map_network = False
      cloudlog.exception("traffic_assist api_get error")

    return resp

  def get_road_name(self):
    road_name = ""
    try:
      path = ""
      for i in range(3):
        path += "%s,%s" % (self.latitude, self.longitude)
        if i < 2:
          path += "_"
        time.sleep(1)

      token = jwt.encode({'identity': self.dongle_id}, self.private_key, algorithm='RS256')
      resp = self.api_get("roads/roadName", method='POST', timeout=15, path=path, language=self.get_locale(), public_key=self.public_key, token=token)

      if resp.status_code == 200:
        self.map_network = True
        res = json.loads(resp.text)
        if res is not None and len(res) > 0:
          road_name = res['roadName']
    except Exception:
      self.state = 0
      self.speed_limit = 0
      cloudlog.exception("road_name request error")
      time.sleep(10)
    self.road_name = road_name

  def speed_limits(self):
    try:
      is_speed_limit = False
      coordinate = "%s,%s" % (self.latitude, self.longitude)
      token = jwt.encode({'identity': self.dongle_id}, self.private_key, algorithm='RS256')
      resp = self.api_get("roads/speedLimits", method='POST', timeout=15, coordinate=coordinate, public_key=self.public_key, token=token)
      if resp.status_code == 200:
        self.map_network = True
        res = json.loads(resp.text)
        if res is not None and len(res) > 0:
          res = json.loads(resp.text)
          status = res['status']
          if status == 1:
            if "speedLimits" in res:
              self.speed_limit = int(res['speedLimits'])
              # 车速大于65km/h时, 如果限速与车速差大于20则不控制限速
              if self.v_ego >= 65 and abs(self.speed_limit - self.v_ego) >= 20:
                is_speed_limit = False
              else:
                is_speed_limit = True

      if not is_speed_limit:
        self.speed_limit = 0
    except Exception:
      self.state = 0
      self.speed_limit = 0
      cloudlog.exception("speed_limits request error")
      time.sleep(10)

  def road_name_thread(self):
    while True:
      try:
        if self.state > 0:
          self.get_road_name()
          time.sleep(10)
      except Exception:
        cloudlog.exception("traffic road_name_thread error")
      time.sleep(1)

  def speed_limits_thread(self):
    while True:
      try:
        if self.is_traffic_assist and self.enabled \
                and self.v_ego > 1 and self.latitude!=0 and self.longitude!=0 and self.accuracy < 10:
          self.speed_limits()
      except Exception:
        cloudlog.exception("traffic assist speed_limits_thread error")

      time.sleep(2)

  def start(self):
    rk = Ratekeeper(20, print_delay_threshold=None)

    with open(PERSIST+"/comma/id_rsa.pub") as f1, open(PERSIST+"/comma/id_rsa") as f2:
      self.public_key = f1.read()
      self.private_key = f2.read()

    # _thread.start_new_thread(self.road_name_thread, ())
    _thread.start_new_thread(self.speed_limits_thread, ())
    while True:
      try:
        if rk.frame % 60 == 0:
          self.is_traffic_assist = self.params.get_bool("IsTrafficAssist")

        self.sm.update(0)

        self.v_ego = self.sm['carState'].vEgo * CV.MS_TO_KPH + 2
        self.latitude = round(self.sm['gpsLocationExternal'].latitude, 8)
        self.longitude = round(self.sm['gpsLocationExternal'].longitude, 8)
        self.accuracy = self.sm['gpsLocationExternal'].accuracy

        self.enabled = self.sm['controlsState'].enabled

        if self.enabled and self.map_network and self.is_traffic_assist:
          if self.speed_limit > 0:
            if self.v_ego >= self.speed_limit:
              self.state = 2
            else:
              self.state = 1
          else:
            self.state = 0
        else:
          self.state = 0
          self.speed_limit = 0

        if not self.map_network or not self.is_traffic_assist:
          self.road_name = ""
          self.map_network = False

        dat = messaging.new_message('trafficAssist')
        dat.trafficAssist.state = self.state
        dat.trafficAssist.speedLimit = self.speed_limit
        dat.trafficAssist.notifyMsg = "注意：已進入限速監控區域，限速%skm/h" % self.speed_limit
        # 注意：已進入限速監控區域，限速%skm/h
        # 注意：已进入限速监控区域,限速%skm/h

        dat.trafficAssist.mapNetwork = self.map_network
        dat.trafficAssist.roadName = self.road_name

        self.pm.send("trafficAssist", dat)

      except Exception:
        cloudlog.exception("traffic assist error")

      rk.keep_time()


def main(sm=None, pm=None):
  TrafficAssist().start()


if __name__ == "__main__":
  main()
