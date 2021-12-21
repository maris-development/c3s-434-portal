@ECHO off

CALL S:
CD S:\install\c3s

XCOPY public\* S:\www\c3s.maris.nl\public /S /Y /V 