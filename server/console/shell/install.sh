#!/bin/bash

WORK_DIR='console'
WORK_BIN='bin'
WORK_CFG='config'
WORK_SCR='scripts'
WORK_TEMP='temp'
WORK_MODULES='modules'
WORK_PACKAGE='packages'
WORK_LOG='log'
WORK_SHELL='shell'

WORK_BASE=${HOME}
WORK_PATH=${WORK_BASE}/${WORK_DIR}
WORK_PATH_BIN=${WORK_PATH}/${WORK_BIN}
WORK_PATH_CFG=${WORK_PATH}/${WORK_CFG}
WORK_PATH_SCR=${WORK_PATH}/${WORK_SCR}
WORK_PATH_TEMP=${WORK_PATH}/${WORK_TEMP}
WORK_PATH_MODULES=${WORK_PATH}/${WORK_MODULES}
WORK_PATH_PACKAGE=${WORK_PATH}/${WORK_PACKAGE}
WORK_PATH_SHELL=${WORK_PATH}/${WORK_SHELL}
WORK_PATH_LOG=${WORK_PATH}/${WORK_LOG}

DEPLOY_DIR='app'
DEPLOY_RUN='run'
DEPLOY_LATEST='latest'
DEPLOY_RELEASE='release'
DEPLOY_UPDATE='update'

DEPLOY_PATH=${WORK_BASE}/${DEPLOY_DIR}
DEPLOY_PATH_LATEST=${DEPLOY_PATH}/${DEPLOY_LATEST}
DEPLOY_PATH_RELEASE=${DEPLOY_PATH}/${DEPLOY_RELEASE}
DEPLOY_PATH_UPDATE=${DEPLOY_PATH}/${DEPLOY_UPDATE}
DEPLOY_PATH_RUN=${DEPLOY_PATH}/${DEPLOY_RUN}

WORK_MODE_CONSOLE="console"
WORK_MODE_RELAY="relay"
WORK_MODE_TARGET="target"

PERSONAL_RPMDB=${HOME}/rpm/var/lib/rpm
PERSONAL_PREFIX=${HOME}/usr
PERSONAL_PATH_BIN=${PERSONAL_PREFIX}/bin
PERSONAL_PROFILE=${HOME}/.bash_profile

PKGNAME_PYTHON=python2.7-2.7.12-el5_5.x86_64.rpm
PKGNAME_PYTHON_MODULES=python_modules.tz
PKGFILE_PYTHON=${WORK_PATH_PACKAGE}/${PKGNAME_PYTHON}
PKGFILE_PYTHON_MODULES=${WORK_PATH_PACKAGE}/${PKGNAME_PYTHON_MODULES}

PYTHON_VERSION_NEEDED=2.6

MODULE_ECDSA='ecdsa-0.13'
MODULE_PYCRYPTO='pycrypto-2.7a1'
MODULE_PARAMIKO='paramiko-1.12.1'

makeBasePath()
{
  mkdir -p ${WORK_PATH_TEMP}  ${WORK_PATH_LOG}
}

makeDeployPath()
{
  mkdir -p ${DEPLOY_PATH_LATEST} ${DEPLOY_PATH_RELEASE}
}

makeAppPath()
{
  mkdir -p ${DEPLOY_PATH_UPDATE} ${DEPLOY_PATH_RUN}
}

chmodExec()
{
  chmod 750 ${WORK_PATH_SCR}/*.py ${WORK_PATH_SHELL}/*.sh
}

init()
{
  chmodExec
  makeBasePath
  [ "${WORK_MODE}" = "${WORK_MODE_CONSOLE}" ] && makeDeployPath
  makeAppPath
}

getPythonVer()
{
  VER_PYTHON=`python -V 2>&1 | awk '{ print $2 }'`
  if [ $? -ne 0 ]
  then
    VER_PYTHON="0.0"
  fi
}

checkPythonVer()
{
  getPythonVer
  if [ "${VER_PYTHON}" \< "${PYTHON_VERSION_NEEDED}" ]
  then
    installPython
  fi
}

installPythonPkg()
{
  mkdir -p ${PERSONAL_RPMDB}
  rpm --rebuilddb --dbpath ${PERSONAL_RPMDB}
  rpm -ivh --nodeps ${PKGFILE_PYTHON} --dbpath ${PERSONAL_RPMDB} --prefix ${PERSONAL_PREFIX} >/dev/null 2>&1
}

registerPythonEnv()
{
  result=`echo "$PATH" | grep ":${PERSONAL_PATH_BIN}:"`
  if [ "$result" = "" -a -d ${PERSONAL_PATH_BIN} ]
  then
    echo "register Python Env"
    printf 'export PATH=.:%s:${PATH}\n' "${PERSONAL_PATH_BIN}" >>${PERSONAL_PROFILE}
    . ${PERSONAL_PROFILE}
  fi
}

installPython()
{
  echo 'installing python'
  installPythonPkg
  registerPythonEnv
}

installModule()
{
  for module in $*
  do
    echo "installing module [${module}]"  
    cd ${module} >/dev/null 2>&1 && chmod 750 setup.py && python setup.py install >/dev/null 2>&1 && cd - >/dev/null 2>&1
  done
}

installModules()
{
  echo 'installing modules'
  cd ${WORK_PATH_PACKAGE}
  mkdir -p ${WORK_PATH_MODULES}
  tar zxf ${PKGFILE_PYTHON_MODULES} -C ${WORK_PATH_MODULES} >/dev/null 2>&1
  cd ${WORK_PATH_MODULES}

  [ "${WORK_MODE}" != "${WORK_MODE_TARGET}" ] && installModule ${MODULE_ECDSA} ${MODULE_PYCRYPTO} ${MODULE_PARAMIKO}
  #installModule others
}

getOption()
{
  case $1 in
  target|Target|T|TGT|tgt)
    WORK_MODE=${WORK_MODE_TARGET}
    ;;
  relay|Relay|R|RL|rl)
    WORK_MODE=${WORK_MODE_RELAY}
    ;;
  *)
    WORK_MODE=${WORK_MODE_CONSOLE}
  esac
}


## main
getOption $*
init
checkPythonVer
installModules
