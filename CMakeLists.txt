cmake_minimum_required(VERSION 3.13)

# Set the project name
project(picoSerialControlledKeyboard)

# Default Pico drive letter (adjust if needed)
set(PICO_DRIVE "D:" CACHE STRING "Drive letter where Pico is mounted")

# Deploy target: Copy only necessary files to Pico
add_custom_target(deploy
    COMMAND ${CMAKE_COMMAND} -E echo "Deploying to ${PICO_DRIVE}"
    COMMAND powershell -Command "Copy-Item code.py ${PICO_DRIVE}"
    COMMAND powershell -Command "Copy-Item macros.json ${PICO_DRIVE}"
    COMMAND powershell -Command "if (Test-Path lib/adafruit_hid) { Copy-Item -Recurse lib/adafruit_hid '${PICO_DRIVE}/lib/' }"
    COMMAND powershell -Command "if (Test-Path lib/adafruit_bus_device) { Copy-Item -Recurse lib/adafruit_bus_device '${PICO_DRIVE}/lib/' }"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ deployed (code, macros, and minimal libs)"
    COMMENT "Deploying CircuitPython files to Pico"
)

# Install dependencies target: Download and extract only required libraries
add_custom_target(install-deps
    COMMAND ${CMAKE_COMMAND} -E echo "Setting up lib directory..."
    COMMAND ${CMAKE_COMMAND} -E make_directory lib
    COMMAND ${CMAKE_COMMAND} -E echo "Download bundle from: https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases"
    COMMAND ${CMAKE_COMMAND} -E echo "Then extract: adafruit_hid/ and adafruit_bus_device/ to lib/"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ ready to install (follow instructions above)"
    COMMENT "Setting up minimal library structure"
)

# Clean target: Remove generated files
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E echo "Cleaning project files..."
    COMMAND powershell -Command "Remove-Item -Recurse lib\\*, *.pyc, __pycache__ -Force -ErrorAction SilentlyContinue"
    COMMAND ${CMAKE_COMMAND} -E echo "✓ cleaned"
    COMMENT "Cleaning project files"
)