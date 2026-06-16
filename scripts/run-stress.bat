@echo off
setlocal
cd /d "%~dp0.."

if "%JMETER_HOME%"=="" (
  echo Задайте JMETER_HOME
  exit /b 1
)

netstat -an | findstr ":8083" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo [ОШИБКА] Порт 8083 не слушается. Сначала запустите scripts\tunnel.bat
  exit /b 1
)

if exist stress\stress.csv del /f stress\stress.csv
if exist stress_report rmdir /s /q stress_report

echo === Стресс-тест (config=2 по умолчанию — измените в stress\stress-test-plan.jmx) ===
"%JMETER_HOME%\bin\jmeter.bat" -n -t stress\stress-test-plan.jmx -l stress\stress.csv -j stress\jmeter.log
if errorlevel 1 exit /b 1

"%JMETER_HOME%\bin\jmeter.bat" -g stress\stress.csv -o stress_report

echo === График отклик vs нагрузка (все запросы) ===
python scripts\plot-stress.py stress\results.csv stress\stress-graph.png

echo Готово: stress\stress.csv, stress_report\index.html, stress\stress-graph.png
