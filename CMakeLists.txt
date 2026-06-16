cmake_minimum_required(VERSION 3.13)

# Set the project name
project(picoSerialControlledKeyboard)

# Adafruit bundle used by install-deps
set(CIRCUITPY_BUNDLE_VERSION "20260310" CACHE STRING "Adafruit CircuitPython bundle release date")
set(CIRCUITPY_BUNDLE_URL "https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/${CIRCUITPY_BUNDLE_VERSION}/adafruit-circuitpython-bundle-10.x-mpy-${CIRCUITPY_BUNDLE_VERSION}.zip" CACHE STRING "Adafruit CircuitPython bundle URL")

# Default Pico drive letter (adjust if needed)
set(PICO_DRIVE "D:" CACHE STRING "Drive letter where Pico is mounted")

# Deploy target: Copy only necessary files to Pico
add_custom_target(deploy
    COMMAND ${CMAKE_COMMAND} -E echo "Deploying to ${PICO_DRIVE}"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; if (-not (Test-Path '${PICO_DRIVE}')) { throw 'Pico drive not found at ${PICO_DRIVE}. Check PICO_DRIVE and that the board is mounted.' }; New-Item -ItemType Directory -Path '${PICO_DRIVE}/lib' -Force | Out-Null"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item boot.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item code.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item macros.json ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item config.json ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item config_manager.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item logger.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item macros.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item command_handler.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; Copy-Item hardware.py ${PICO_DRIVE} -Force"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; if (Test-Path lib/adafruit_hid) { if (Test-Path '${PICO_DRIVE}/lib/adafruit_hid') { Remove-Item -Recurse -Force '${PICO_DRIVE}/lib/adafruit_hid' }; Copy-Item -Recurse lib/adafruit_hid '${PICO_DRIVE}/lib/' -Force }"
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; if (Test-Path lib/adafruit_bus_device) { if (Test-Path '${PICO_DRIVE}/lib/adafruit_bus_device') { Remove-Item -Recurse -Force '${PICO_DRIVE}/lib/adafruit_bus_device' }; Copy-Item -Recurse lib/adafruit_bus_device '${PICO_DRIVE}/lib/' -Force }"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ deployed (code, macros, and minimal libs)"
    COMMENT "Deploying CircuitPython files to Pico"
)

# Install dependencies target: Download and extract only required libraries
add_custom_target(install-deps
    COMMAND ${CMAKE_COMMAND} -E echo "Setting up lib directory..."
    COMMAND ${CMAKE_COMMAND} -E make_directory lib
    COMMAND powershell -NoProfile -ExecutionPolicy Bypass -Command "$$ErrorActionPreference = 'Stop'; $$zipPath = Join-Path $$PWD 'lib/adafruit-bundle.zip'; $$extractDir = Join-Path $$PWD 'lib/.bundle_extract'; Write-Host 'Downloading bundle:' '${CIRCUITPY_BUNDLE_URL}'; Invoke-WebRequest -Uri '${CIRCUITPY_BUNDLE_URL}' -OutFile $$zipPath; if (Test-Path $$extractDir) { Remove-Item -Recurse -Force $$extractDir }; Expand-Archive -Path $$zipPath -DestinationPath $$extractDir -Force; $$hid = Get-ChildItem -Path $$extractDir -Recurse -Directory | Where-Object { $$_.Name -eq 'adafruit_hid' } | Select-Object -First 1; $$bus = Get-ChildItem -Path $$extractDir -Recurse -Directory | Where-Object { $$_.Name -eq 'adafruit_bus_device' } | Select-Object -First 1; if (-not $$hid) { throw 'adafruit_hid not found in extracted bundle' }; if (-not $$bus) { throw 'adafruit_bus_device not found in extracted bundle' }; Copy-Item -Path $$hid.FullName -Destination (Join-Path $$PWD 'lib') -Recurse -Force; Copy-Item -Path $$bus.FullName -Destination (Join-Path $$PWD 'lib') -Recurse -Force; Remove-Item -Force $$zipPath -ErrorAction SilentlyContinue; Remove-Item -Recurse -Force $$extractDir -ErrorAction SilentlyContinue; Write-Host 'Installed: lib/adafruit_hid and lib/adafruit_bus_device'"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ dependencies installed"
    COMMENT "Setting up minimal library structure"
)

# Clean target: Remove generated files
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E echo "Cleaning project files..."
    COMMAND powershell -Command "Remove-Item -Recurse lib\\*, *.pyc, __pycache__ -Force -ErrorAction SilentlyContinue"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ cleaned"
    COMMENT "Cleaning project files"
)