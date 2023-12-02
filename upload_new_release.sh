#!/usr/bin/env zsh

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  echo "There are uncommitted changes in the Git repository. Aborting."
  exit 1
fi

# Make docs
sphinx-build -b html . build
rm -r ~/Developer/jonnybergdahl/jonnybergdahl.github.io/growcube-client/*
cp docs/build/*.html ~/Developer/jonnybergdahl/jonnybergdahl.github.io/jbwopr
cp -r docs/build/_static ~/Developer/jonnybergdahl/jonnybergdahl.github.io/jbwopr/_static

exit 1

# Commit and push docs
cd ~/Developer/jonnybergdahl/jonnybergdahl.github.io
git checkout main
git add jbwopr
if [ -n "$(git status --porcelain)" ]; then
  git commit -m "Update JBWOPR docs"
  git push
else
   echo "Branch main is up to date,nothing to do."
fi

# Make new version
rm -rf dist
python3 setup.py sdist bdist_wheel
twine upload dist/*.html dist/*.js dist/*.css dist/*.png dist/*.svg dist/*.ico dist/*.txt dist/*.xml dist/*.json dist/*.ttf dist/*.woff dist/*.woff2 dist/*.eot dist/*.otf dist/*.map dist/*.gz dist/*.zip

