#!/usr/bin/env zsh

# Check for uncommitted changes
#if [ -n "$(git status --porcelain)" ]; then
#  echo "There are uncommitted changes in the Git repository. Aborting."
#  exit 1
#fi

# Make docs
pandoc README.md -o README.rst
# cp assets/* docs/assets/
sphinx-build -b html docs html
rm -r ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client/*
cp html/*.html ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client
cp -r html/_static ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client/_static
cp -r assets/ ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client/assets
touch ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client/.nojekyll

# Commit and push docs
pushd ~/Developer/jonnybergdahl/jonnybergdahl.github.io
git checkout main
git pull
git add growcube-client
if [ -n "$(git status --porcelain)" ]; then
  git commit -m "Update growcube-client docs"
  git push
else
   echo "Branch main is up to date,nothing to do."
fi
popd

# Make new version
rm -rf dist
python3 setup.py sdist bdist_wheel
twine upload dist/*

