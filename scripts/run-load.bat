@echo off
setlocal
cd /d "%~dp0.."

if "%JMETER_HOME%"=="" (
  echo Задайте JMETER_HOME, например:
  echo   set JMETER_HOME=C:\apache-jmeter-5.6.3
  exit /b 1
)

netstat -an | findstr ":8083" | findstr "LISTENING" >nul
if errorlevel 1 (
  echo [ОШИБКА] Порт 8083 не слушается. Сначала запустите scripts\tunnel.bat
  exit /b 1
)

if exist load\load.csv del /f load\load.csv
if exist load_report rmdir /s /q load_report

echo === Нагрузочный тест: 3 конфигурации ===
"%JMETER_HOME%\bin\jmeter.bat" -n -t load\load-test-plan.jmx -l load\load.csv -j load\jmeter.log
if errorlevel 1 exit /b 1

echo === HTML-отчёт ===
"%JMETER_HOME%\bin\jmeter.bat" -g load\load.csv -o load_report

echo Готово: load\load.csv, load_report\index.html
