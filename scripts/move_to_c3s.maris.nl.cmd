@ECHO off

CALL S:
CD S:\install\c3s

IF /I NOT "%cd%" == "S:\install\c3s" (
    ECHO Not in correct directory. %cd%
    EXIT
) ELSE (
    ECHO Removing files from S:\www\c3s.maris.nl\
)


@REM @ECHO on
@REM Remove directories
 FOR /D %%d IN (S:\www\c3s.maris.nl\*) DO (
    @REM  echo "%%d"
    rmdir /Q /S "%%d"
 )

@REM Remove files
FOR %%i IN (S:\www\c3s.maris.nl\*) DO (
    if not "%%i"=="S:\www\c3s.maris.nl\.gitignore" (
        if not "%%i"=="S:\www\c3s.maris.nl\.git" (
            @REM echo "%%i"
            del /q /s "%%i"
        )
    )
)

ECHO Copying files from public\ to S:\www\c3s.maris.nl\

XCOPY public\* S:\www\c3s.maris.nl /S /Y /V 