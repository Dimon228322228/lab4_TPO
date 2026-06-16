@echo off
REM SSH-туннель к stload (запускать в отдельном окне и не закрывать).
REM Замените USER на свой логин helios (sXXXXXX).
set HELIOS_USER=s336698

echo Проброс localhost:8083 -> stload.se.ifmo.ru:8080
echo После подключения JMeter обращается к http://localhost:8083
ssh -N -L 8083:stload.se.ifmo.ru:8080 -p 2222 %HELIOS_USER%@helios.cs.ifmo.ru
