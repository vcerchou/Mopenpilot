#!/usr/bin/bash

lang=$(cat /data/property/persist.sys.locale)

url="http://mypilot.com.cn:8088/installers/upgrade"
if [ "$lang" == "zh-TW" ];then
  url="https://twmp.myclouds.ai/installers/upgrade"
fi

cd /tmp
curl --connect-timeout 120 -A "NEOSInstaller-0.2" -o upgrade $url
chmod +x upgrade
./upgrade
if [ "$lang" == "zh-TW" ];then
  echo -n 0 > /data/params/d/IsAllowSuperAuth
fi
reboot