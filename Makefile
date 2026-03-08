.PHONY: deploy install-deps clean

# adjust the drive letter if your Pico mounts differently
PICO_DRIVE ?= D:

deploy:
	@echo Deploying to $(PICO_DRIVE)
	@powershell -Command "Copy-Item code.py $(PICO_DRIVE)\"
	@powershell -Command "Copy-Item -Recurse lib $(PICO_DRIVE)\"
	@echo ✓ deployed

install-deps:
	@echo Downloading Adafruit CircuitPython bundle...
	@powershell -Command "Invoke-WebRequest -Uri https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20260307/adafruit-circuitpython-bundle-py-20260307.zip -OutFile bundle.zip; Expand-Archive bundle.zip -Force; Copy-Item adafruit-circuitpython-bundle-py-20260307\lib\* lib\ -Recurse; Remove-Item bundle.zip; Remove-Item -Recurse adafruit-circuitpython-bundle-py-20260307"
	@echo ✓ dependencies installed

clean:
	@echo Cleaning project files...
	@powershell -Command "Remove-Item -Recurse lib\*, *.pyc, __pycache__ -Force -ErrorAction SilentlyContinue"
	@echo ✓ cleaned
