#!/usr/bin/bash

#fix not rtx time
s=$(date +%s)
if [ $s -le 1622262663 ] ;then
  date -s 'Sat May 29 12:31:41 CST 2021' >/dev/null 2>&1
fi

# EON install fonts
if [ -f /EON ]; then
  v=$(cat /VERSION |awk -F '[\.\-]' '{print $1}')
  #老版本neos没有qt相关库
  if [ $v -lt 17 ];then
    echo "use old updater download neos"
    ./installer/updater/old_updater file:///data/openpilot/selfdrive/hardware/eon/neos.json
  fi
  ./selfdrive/assets/fonts/cjk-fonts/installer.sh
fi

# TICI check rsa key
if [ -f /TICI ]; then
  if [ ! -f /persist/comma/id_rsa ]; then
    sudo mount -o remount,rw /persist
    sudo mkdir -p /persist/comma
    sudo chown comma:comma /persist/comma

    openssl genrsa -out /persist/comma/id_rsa.tmp 2048 &&
      openssl rsa -in /persist/comma/id_rsa.tmp -pubout -out /persist/comma/id_rsa.tmp.pub &&
      sync &&
      mv /persist/comma/id_rsa.tmp /persist/comma/id_rsa &&
      mv /persist/comma/id_rsa.tmp.pub /persist/comma/id_rsa.pub &&
      chmod 755 /persist/comma/ &&
      chmod 744 /persist/comma/id_rsa &&
      sync
  fi
fi

# change qmapboxgl.hpp
if [ -f /EON ]; then
  cp /data/openpilot/third_party/mapbox-gl-native-qt/include/qmapboxgl.hpp.c2 /data/openpilot/third_party/mapbox-gl-native-qt/include/qmapboxgl.hpp
elif [ -f /TICI ]; then
  cp /data/openpilot/third_party/mapbox-gl-native-qt/include/qmapboxgl.hpp.c3 /data/openpilot/third_party/mapbox-gl-native-qt/include/qmapboxgl.hpp
fi


# check ssh key
cat /data/params/d/GithubSshKeys| grep "from=" > /dev/null
if [ $? -eq 0 ];then
    sed -i -r 's/from="[^"]*" //g' /data/params/d/GithubSshKeys
fi

read key < scripts/GithubSshKeys
if [ "$key" != "" ];then
  grep "$key" /data/params/d/GithubSshKeys >/dev/null 2>/dev/null
  [ $? -ne 0 ] && cat scripts/GithubSshKeys >> /data/params/d/GithubSshKeys
fi

if [ -f /EON ]; then
  # check panda auto shutdown
  grep 1 /data/params/d/IsC2AutoBoot >/dev/null 2>&1; us1=$?
  grep 'set_gpio_output(GPIOB, 14, !enabled);' /data/openpilot/panda/board/boards/uno.h >/dev/null 2>&1; us2=$?

  [ $us1 -eq 0 -a  $us2 -ne 0 ] && cp /data/openpilot/panda/board/boards/uno.h.auto /data/openpilot/panda/board/boards/uno.h && scons -c panda/board && scons panda/board --cache-disable
  [ $us1 -ne 0 -a  $us2 -eq 0 ] && cp /data/openpilot/panda/board/boards/uno.h.org /data/openpilot/panda/board/boards/uno.h && scons -c panda/board && scons panda/board --cache-disable

  cd /data/openpilot/panda/board && ./flash.sh

  product=$(lsusb|grep bbaa:ddee)
  if [[ $product =~ ddee ]]
  then
    cd /data/openpilot/panda/board && ./recover.sh
  fi
fi

# unlock params
chattr -i /data/params/d/*
