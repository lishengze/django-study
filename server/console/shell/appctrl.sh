#!/bin/bash
################################################################################
##  appctl.sh 用于控制本地服务启停清理等动作
##
##  Author: yan.hc
##  Modify: 20130718
##
MY_NAME=`basename $0`
MY_PATH=`dirname $0`
MY_PID=$$

###
DEPLOY_PATH=${HOME}/app
DEPLOY_PATH_RUN=${DEPLOY_PATH}/run
PATH_NAME_TMP=temp
PATH_NAME=console
WORK_PATH=${HOME}/${PATH_NAME}
WORK_PATH_TMP=${WORK_PATH}/${PATH_NAME_TMP}
JRE_BIN=/home/uapp/jre/bin
JAVA=java
VM_LANG=zh_CN.GBK
FLAG_COLOR=0

if [ $FLAG_COLOR -eq 1 ]
then
  CSTR_BLACK="\033[30m"
  CSTR_RED_L="\033[0;31m"
  CSTR_RED_H="\033[1;31m"
  CSTR_GRN_L="\033[0;32m"
  CSTR_GRN_H="\033[1;32m"
  CSTR_YLW_L="\033[0;33m"
  CSTR_YLW_H="\033[1;33m"
  CSTR_BLU_L="\033[0;34m"
  CSTR_BLU_H="\033[1;34m"
  CSTR_PUP_L="\033[0;35m"
  CSTR_PUP_H="\033[1;35m"
  CSTR_DGN_L="\033[0;36m"
  CSTR_DGN_H="\033[1;36m"
  CSTR_WRITE="\033[37m"
  CSTR_HIGHL="\033[1m"
  CSTR_END="\033[0m"
else
  CSTR_BLACK=""
  CSTR_RED_L=""
  CSTR_RED_H=""
  CSTR_GRN_L=""
  CSTR_GRN_H=""
  CSTR_YLW_L=""
  CSTR_YLW_H=""
  CSTR_BLU_L=""
  CSTR_BLU_H=""
  CSTR_PUP_L=""
  CSTR_PUP_H=""
  CSTR_DGN_L=""
  CSTR_DGN_H=""
  CSTR_WRITE=""
  CSTR_HIGHL=""
  CSTR_END=""
fi
###


Usage()
{
  echo "Usage for ${MY_NAME}:"
  echo "  ${MY_NAME} ACTION IPADDR CENTER APPNAME APPNO [ARGS]"
  echo "  OPTIONS means:"
  echo "    ACTION  --- [ start | stop | show | clean  ... ]"
  echo "    IPADDR  --- [172.1.128.151|...]"
  echo "    CENTER  --- [ PD | ZJ | BJ   ... (DATACENTER)]"
  echo "    APPNAME --- [ sysprobe | sysagent | sysfront  ... ]"
  echo "    APPNO   --- [ 1 | 2 | 3 | 4  ... (PATH_NO)]"
  echo "    ARGS    --- [ 1 | 2 | 3 | 4  ... (CMDL_NO)]"
  echo ""
  echo "  EX:"
  echo "  ${MY_NAME} start PD sysprobe 1 11"
  echo ""

  exit 1
}

Init()
{
  [ -r "${MY_PATH}/setEnv.sh" ] && . ${MY_PATH}/setEnv.sh
  [ -r "${MY_PATH}/ForceFileCheck.fun" ] && . ${MY_PATH}/ForceFileCheck.fun
  FILE_TEMP=${WORK_PATH_TMP}/${MY_NAME}.${MY_PID}    ###WORK_PATH_TMP
#  mkdir WORK_PATH_TMP
  touch ${FILE_TEMP}
  LANG_ORIG="${LANG}"
  DIR_ORIG=`pwd`
  USER=`whoami`

  if [ -d "${JRE_BIN}" ]
  then
    JAVA_BIN=${JRE_BIN}/${JAVA}
  else
    JAVA_BIN=/home/uapp/jre/bin/${JAVA}
  fi
}

PrintInfo()
{
  echo -e "`printf "%s::%s::%s::%s\n" "${CMD_NAME}" "${IPADDR}" "${APPTIP}" "$*"`"
}

PrintInfoX()
{
  echo -e "`printf "%-22s %s\n" ${APPTIP} "$*"`"
}

StartApp()
{
  StartEnv

  if [ -d "${APPDIR}/bin" ]    ###
  then
    cd ${APPDIR}/bin

    case ${APPNAME} in
    JProbe | jprobe)
      export LANG=${VM_LANG}    #VM_LANG=zh_CN.GBK
      nohup ${JAVA_BIN} -jar ./JProbe ${APPARGS} >../log/out 2>../log/err.out &    ###JRE_BIN=/home/uapp/jre/bin
      export LANG=${LANG_ORIG}
      ;;
    *)
      nohup ./${APPNAME} ${APPARGS} >../log/out 2>&1 &
      ;;
    esac

    if [ $? -eq 0 ]
    then
      ShowApp
    else
      PrintInfo "${CSTR_RED_H}App Not run${CSTR_END}"
    fi

    cd ${DIR_ORIG}
  else
    PrintInfo "${CSTR_YLW_H}Path Not found${CSTR_END}"
  fi
}

ShowVersionApp()
{
  StartEnv

  if [ -d "${APPDIR}/bin" ]    ###
  then
    cd ${APPDIR}/bin

    case ${APPNAME} in
    JProbe | jprobe)
      export LANG=${VM_LANG}    #VM_LANG=zh_CN.GBK
      ver_info=`${JAVA_BIN} -jar ./JProbe -v` ###JRE_BIN=/home/uapp/jre/bin
      export LANG=${LANG_ORIG}
      ;;
    *)
      ver_info=`./${APPNAME} -v`
      ;;
    esac

    if [ $? -eq 0 ]
    then
      PrintInfo "${CSTR_GRN_H}${ver_info}${CSTR_END}"
    else
      PrintInfo "${CSTR_RED_H}Failed${CSTR_END}"
    fi

    cd ${DIR_ORIG}
  else
    PrintInfo "${CSTR_YLW_H}Path Not found${CSTR_END}"
  fi
}

StopApp()
{
  SeekApp
  PIDs=`cat ${FILE_TEMP} 2>/dev/null | awk '{ if ($2 >1) {printf("%d ", $2)}}'`
  if [ "${PIDs}" != "" ]
  then
    kill -9 ${PIDs} >/dev/null 2>&1
    PrintInfo "${CSTR_GRN_H}App stopped${CSTR_END}"
  else
    PrintInfo "${CSTR_YLW_H}App Not run${CSTR_END}"
  fi
}

ShowApp()
{
  if [ -d "${APPDIR}/bin" ]    ###
  then
    SeekApp
    INFO=`cat ${FILE_TEMP} 2>/dev/null | awk -v APP=${APPNAME} -v ARG="${APPARG}" '{
      if ($2 >1)
      {
        printf("%5d %6s ", $2,$5);
        for(i = 8; i<=NF; i++)
        {
          printf("%s ", $i);
        }
        printf("\n");
      }
    }'`
  
    if [ "${INFO}" != "" ]
    then
      PrintInfo "${INFO}"
    else
      PrintInfo "${CSTR_YLW_H}App Not run${CSTR_END}"
    fi
  else
    PrintInfo "${CSTR_YLW_H}Path Not found${CSTR_END}"  
  fi
}

ShowxApp()
{
  if [ -d "${APPDIR}/bin" ]    ###
  then
    SeekApp
    PIDs=`cat ${FILE_TEMP} 2>/dev/null | awk '{ if ($2 >1) {printf("%d ", $2)}}'`
    if [ "${PIDs}" != "" ]
    then
      PrintInfoX "${CSTR_GRN_H}running${CSTR_END}"
    else
      PrintInfoX "${CSTR_RED_H}offline${CSTR_END}"
    fi
  else
    PrintInfoX "${CSTR_YLW_H}undeployed${CSTR_END}"  
  fi
}

SeekApp()
{
  ps -f -U ${USER}|grep -v "${MY_NAME}"| grep -v sshd|grep -v '\-bash' |grep -v "ps -f" | grep -v "grep" | grep -v "awk" | grep -w "./${APPNAME}`[ "${APPARG}" != "" ] && printf ' '${APPARG}`" >${FILE_TEMP} 2>/dev/null
}

CleanApp()
{
  cd ${APPDIR}
  rm -rf ./bin/*core* ./log/* ./flow/* ./dump/*
  cd ${DIR_ORIG}
  [ "${CMD_NAME}" = "clean" ] && PrintInfo "${CSTR_GRN_H}Done${CSTR_END}"
}

RMCoreApp()
{
  cd ${APPDIR}
  rm -rf ./bin/*core*
  cd ${DIR_ORIG}
  [ "${CMD_NAME}" = "rmcore" ] && PrintInfo "${CSTR_GRN_H}Done${CSTR_END}"
}

StartEnv()
{
  #放开文件和core文件大小限制
  ulimit -c unlimited
  ulimit unlimited
  umask 027

  case ${APPNAME} in
  snmpmanager|manager)
    echo "shanghai" | sudo -S sh -c "chown root:root ${APPDIR}/bin/${APPNAME}; \
      chmod 777 ${APPDIR}/bin/${APPNAME}; chmod u+s ${APPDIR}/bin/${APPNAME}" >/dev/null 2>&1
    ;;
  esac
}

StartCmd()
{
  CMD_NAME="start"

  SeekApp
  PIDs=`cat ${FILE_TEMP} 2>/dev/null | awk '{ if ($2 >1) {printf("%d ", $2)}}'`
  if [ "${PIDs}" != "" ]
  then
    PrintInfo "${CSTR_YLW_H}Already running${CSTR_END}"
    return 1
  fi

  StartApp
}

ShowVersionCmd()
{
  CMD_NAME="version"
  ShowVersionApp
}

AliveCmd()
{
  CMD_NAME="alive"

  SeekApp
  PIDs=`cat ${FILE_TEMP} 2>/dev/null | awk '{ if ($2 >1) {printf("%d ", $2)}}'`
  if [ "${PIDs}" != "" ]
  then
    return 0
  fi

  StartApp
}

DeadCmd()
{
  CMD_NAME="dead"

  SeekApp
  PIDs=`cat ${FILE_TEMP} 2>/dev/null | awk '{ if ($2 >1) {printf("%d ", $2)}}'`
  if [ "${PIDs}" = "" ]
  then
    return 0
  fi

  StopApp
  CleanApp
}

StopCmd()
{
  CMD_NAME="stop"
  StopApp
}

ShowCmd()
{
  CMD_NAME="show"
  ShowApp
}

ShowxCmd()
{
  CMD_NAME="showx"
  ShowxApp
}

CleanCmd()
{
  CMD_NAME="clean"
  CleanApp
}

RemoveCoreCmd()
{
  CMD_NAME="rmcore"
  RMCoreApp	
}
StopClnCmd()
{
  CMD_NAME="stopcln"
  StopApp
  CleanApp
}

## Main function

Init

if [ $# -lt 5 ]
then
  Usage
fi

CMD_NAME=$1
IPADDR=$2
CENTER=$3
APPNAME=$4
APPNO=$5
APPDIR=${DEPLOY_PATH_RUN}/$4$5
APPTIP="${CENTER}.${APPNAME}.${APPNO}"
shift 5

APPARG=$1
APPARGS=$*

case ${CMD_NAME} in
alive|live|Alive|Live)
  AliveCmd
  ;;
dead|die|notalive|nonalive)
  DeadCmd
  ;;
start|Start|Run|run|startService|StartService)
  StartCmd
  ;;
stop|Stop|kill|Kill|stopService|StopService)
  StopCmd
  ;;
show|Show)
  ShowCmd
  ;;
showVer|ShowVersion|version|Version|'ver'|Ver)
  ShowVersionCmd
  ;;
showx|ShowX|showc|ShowC)
  ShowxCmd
  ;;
clean|Clean|cln)
  CleanCmd
  ;;
rmcore|RMCore|delcore|DelCore)
  RemoveCoreCmd
  ;;
stopcln|StopCln|stopc|StopC|stopclean|StopClean)
  StopClnCmd
  ;;
*)
  Usage
  ;;
esac

rm -f ${FILE_TEMP}
exit 0
