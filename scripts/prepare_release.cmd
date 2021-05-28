@echo off
cd S:\install\c3s\

call yarn build

call yarn move

call git add -A

call git commit

call git push 

call git push github

cd S:\www\c3s.maris.nl

call git add -A 

call git commit

call git push 

call git push github