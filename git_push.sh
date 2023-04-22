echo Enter the commit summary:
read commit_summary

git add .
git commit -m commit_summary
#git remote add origin git@github.com:D6AD3C/blender_python_suite.git
git push -u origin main
#git remote add $repo_id https://github.com/D6AD3C/blender_python_suite2.git

