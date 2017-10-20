@ECHO off

REM *********************************************************
REM *                                                       *
REM * Change these path variables to get app to run locally *
REM *                                                       *
REM *********************************************************
@SET "appRoot=%CD%"
@SET "pythonPath=%PYTHONPATH%
@SET "appPath=%appRoot%\bin\app.py"

REM *********************************************************
REM *                                                       *
REM * If you have python installed on your environment      *
REM * variables path, you can use this instead of the       *
REM * portable python. This is nice because it will not     *
REM * open a cmd window before launching the app.           *
REM *                                                       *
REM *********************************************************
REM @SET "pythonSystemPath"=python

ECHO App Root:    %appRoot%
ECHO App Path:    %appPath%
ECHO Python Root: %pythonPath%
ECHO.

%pythonPath% %appPath%