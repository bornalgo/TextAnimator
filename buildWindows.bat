@echo off

set "WORKSPACE=%~dp0"
set "PYTHONEXE=python"
set "HT=Win64"
set "BUILDPATH=%WORKSPACE%build\%HT%"

echo [34mRemove existing build[0m
if exist "%BUILDPATH%" rd /s /q "%BUILDPATH%"

echo [34mCreate build path[0m
mkdir "%BUILDPATH%"

set "WORKPATH=%BUILDPATH%\work"
set "DISTPATH=%BUILDPATH%\dist"
set "SPECPATH=%WORKSPACE%\res\build.spec"
set "VENVPATH=%BUILDPATH%\venv"
echo [34mCreate virtual environment[0m
%PYTHONEXE% -m venv "%VENVPATH%"
echo [34mActivate virtual environment[0m
"%VENVPATH%\Scripts\activate.bat" & ^
echo [34mUpgrade pip[0m & ^
%PYTHONEXE% -m pip install --upgrade pip & ^
echo [34mInstall requirements[0m & ^
%PYTHONEXE% -m pip install -r requirements.txt & ^
echo [34mConvert UI file to PY[0m & ^
pyuic5 --from-imports -o src/gui/interface_ui.py res/ui/interface.ui & ^
echo [34mConvert QRC file to PY[0m & ^
pyrcc5 -o src/gui/resources_rc.py res/resources.qrc & ^
echo [34mCreate executable[0m & ^
pyinstaller.exe --workpath "%WORKPATH%" --distpath "%DISTPATH%" "%SPECPATH%" & ^
echo [34mDeactivate virtual environment[0m & ^
deactivate
