#!/bin/bash

WORKSPACE=`pwd`
PYTHONEXE=python3
HT=LINUX-x86_64
BUILDPATH="$WORKSPACE/build/$HT"

echo -e '\033[0;34mRemove existing build\033[0m'
if [ -d "$BUILDPATH" ] ; then rm -rf "$BUILDPATH" ; fi

echo -e '\033[0;34mCreate build path\033[0m'
mkdir -p "$BUILDPATH"

WORKPATH="$BUILDPATH/work"
DISTPATH="$BUILDPATH/dist"
SPECPATH="$WORKSPACE/res/build.spec"
VENVPATH="$BUILDPATH/venv"
echo -e '\033[0;34mCreate virtual environment\033[0m'
$PYTHONEXE -m venv "$VENVPATH"
echo -e '\033[0;34mActivate virtual environment\033[0m'
source "$VENVPATH/bin/activate"
echo -e '\033[0;34mUpgrade pip\033[0m'
$PYTHONEXE -m pip install --upgrade pip
echo -e '\033[0;34mInstall requirements\033[0m'
$PYTHONEXE -m pip install -r requirements.txt
echo -e '\033[0;34mConvert UI file to PY\033[0m'
pyuic5 --from-imports -o src/gui/interface_ui.py res/ui/interface.ui
echo -e '\033[0;34mConvert QRC file to PY\033[0m'
pyrcc5 -o src/gui/resources_rc.py res/resources.qrc
echo -e '\033[0;34mCreate executable\033[0m'
pyinstaller --workpath "$WORKPATH" --distpath "$DISTPATH" "$SPECPATH"
echo -e '\033[0;34mDeactivate virtual environment\033[0m'
deactivate
