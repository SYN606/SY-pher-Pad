#!/bin/bash
set -e

rm -rf dist build SY-pherPad.AppDir *.AppImage appimagetool-x86_64.AppImage

if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

echo "Compiling binary with PyInstaller..."
uv run pyinstaller --noconfirm --onedir --windowed --add-data "gui:gui" --add-data "editor:editor" --add-data "crypt_core:crypt_core" --add-data "icons:icons" --icon="icons/app_icon.ico" --name="SY-pherPad" main.py

echo "Assembling AppDir structural layers..."
mkdir -p SY-pherPad.AppDir/usr/bin
cp -r dist/SY-pherPad/* SY-pherPad.AppDir/usr/bin/
cp sy-pherpad.desktop SY-pherPad.AppDir/
cp AppRun SY-pherPad.AppDir/
chmod +x SY-pherPad.AppDir/AppRun

cp icons/app_icon.ico SY-pherPad.AppDir/sy-pherpad.ico
cp icons/app_icon.ico SY-pherPad.AppDir/sy-pherpad.png

echo "Packaging into standalone AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage SY-pherPad.AppDir

echo "Success! SY-pherPad-x86_64.AppImage has been generated."
