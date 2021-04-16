@echo off

FOR %%i IN (S:\install\c3s\yaml_cache_files\*.yaml) DO (
    echo Checking %%i
    call python -c "import yaml, sys; yaml.safe_load(sys.stdin)" < "%%i"
)