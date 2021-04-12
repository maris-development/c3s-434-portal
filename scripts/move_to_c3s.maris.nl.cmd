@ECHO off

CALL P:
CD P:\paul\Workspaces\c3s

IF /I NOT "%cd%" == "P:\paul\Workspaces\c3s" (
    ECHO Not in correct directory.
    EXIT
) ELSE (
    ECHO Copying files from public\ to S:\www\c3s.maris.nl\
)


@REM @ECHO on

for %%i in (*.*) do if not "%%i"==".gitignore" if not "%%i"==".git" del /q /s "%%i"

COPY public\* S:\www\c3s.maris.nl /Y /V 