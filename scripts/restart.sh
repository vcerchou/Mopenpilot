#!/data/data/com.termux/files/usr/bin/sh

cat > /dev/p.txt << EOF
python
selfdrive
_sensord
camerad
_ui
EOF

cmd=$1
bg_restart() {
  exclude='grep|ssh'
  #env|grep SSH_CLIENT=127.0.0.1>/dev/null && exclude="$exclude|athenad"
  ps -ef|grep -v grep|grep launch_chffrplus.sh|awk '{print $1}'|xargs kill -s SIGTERM  >/dev/null 2>&1

  cat /dev/p.txt|while read p;do
    ps -ef|grep -vwE "$exclude"|grep $p|awk '{print $1}'|xargs kill -s SIGINT >/dev/null 2>&1
  done
  cat /data/openpilot/selfdrive/manager/process_config.py |grep -vEw "$exclude"|grep Process|grep 'd"'|awk -F '"' '{print $2}'|sort|uniq|xargs kill -s SIGINT >/dev/null 2>&1

  sleep 0.2

  cat /dev/p.txt|while read p;do
    ps -ef|grep -vwE "$exclude"|grep $p|awk '{print $1}'|xargs kill -9 >/dev/null 2>&1
  done
  cat /data/openpilot/selfdrive/manager/process_config.py |grep -vwE "$exclude"|grep Process|grep 'd"'|awk -F '"' '{print $2}'|sort|uniq|xargs kill -9 >/dev/null 2>&1

  #校验是否kill干净
  #ps -ef|awk '{print $1}'|while read id;do ls -l /proc/$id/cwd 2>/dev/null|grep openpilot >/dev/null;[ $? -eq 0 ] && ps -ef|grep -v grep|grep -w $id; done

  lsof -n|grep /data/openpilot|grep -v $(basename $0)|grep -vwE "$exclude"|grep -v op.sh
  lsof -n|grep /data/openpilot|grep -v $(basename $0)|grep -vwE "$exclude"|grep -v op.sh|awk '{print $1,$2}'|grep /data/openpilot|awk '{print $1}'|sort|uniq|while read pid;do
    kill -9 $pid
  done

  rm -rf /runonce
  ip rule del prio 100 from all lookup main >/dev/null 2>&1
  ps -ef|grep -v grep|grep -E 'ssh|athenad'

  > /data/run.log
  if [ "$1" = "" ];then
    /data/data/com.termux/files/usr/bin/tmux new-session -s comma -d /comma.sh
  else
    export PYTHONUNBUFFERED=1
    stdbuf -o0 -e0 /comma.sh |tee -a /data/run.log 2>&1 &
  fi

}

if [ "$cmd" = "" ] ;then
  bg_restart >/dev/null 2>&1 &
  echo "tmux at"
else
  bg_restart $cmd
fi
