python3 -m nuitka \
  --standalone \
  --macos-create-app-bundle \
  --macos-disable-console \
  --macos-app-icon=resources/app_icon.icns \
  --include-package=wx \
  --output-dir=dist/mac \
  src/growcube_adopt.py
python3 -m nuitka \
  --standalone \
  --macos-create-app-bundle \
  --macos-disable-console \
  --macos-app-icon=resources/app_icon.icns \
  --include-package=wx \
  --output-dir=dist/mac \
  src/growcube_app.py
