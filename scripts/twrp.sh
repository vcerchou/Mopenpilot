#/bin/sh

pid=$$
ps -ef|grep -v grep|grep -v $pid|grep "$(basename $0)" >/dev/null
[ $? -eq 0 ] && echo "already running" && exit 0

recovery_dev=$(readlink  /dev/block/platform/*/*/by-name/recovery)

TWRP_SHA256SUM=aedd7935a2afe5e62fa92f36859a3a2993685d487d258bb32ccf668b953c54c3
TWRP=/tmp/twrp.img
i=$(dd if=$recovery_dev count=59200|sha256sum|awk '{print $1}')
if [ "$TWRP_SHA256SUM" != "$i" ];then
  wget http://wiki.dpp.cool/otherFiles/software/twrp-3.3.1-0-leecolepro3.img -O $TWRP 2>/dev/null && \
    dd if=$TWRP of=$recovery_dev && reboot recovery
else
  reboot recovery
fi

