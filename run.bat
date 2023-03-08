:: this script launches all three servers
echo off
START /B "" python3 process.py 10.250.28.57 a > nul
START /B "" python3 process.py 10.250.28.57 b > nul
START /B "" python3 process.py 10.250.28.57 c > nul
timeout /t 75
taskkill /im "python3.9.exe" /f > nul