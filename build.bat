@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo Compiling AI Games Store...
python -m PyInstaller --noconsole --onefile --name "AI_Games_Store" --icon "assets/ui/icon.ico" --add-data "assets;assets" --collect-all customtkinter main.py

echo Build Complete!
pause
