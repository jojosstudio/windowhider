@echo off
echo [INFO] Kompiliere hider.dll ...

set SDK=C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0
set LIB_SDK=C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0

cl /LD /O2 /nologo ^
   /I"%SDK%\um" ^
   /I"%SDK%\shared" ^
   /I"%SDK%\ucrt" ^
   hider.c /Fe:hider.dll ^
   /link ^
   /LIBPATH:"%LIB_SDK%\um\x64" ^
   /LIBPATH:"%LIB_SDK%\ucrt\x64" ^
   user32.lib

if %errorlevel% == 0 (
    echo [OK] hider.dll erfolgreich erstellt!
) else (
    echo [FEHLER] Kompilierung fehlgeschlagen.
)
pause
