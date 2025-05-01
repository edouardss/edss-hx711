cmake_minimum_required(VERSION 3.10)
project(hx711_loadcell)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ESP-IDF specific settings
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_VERSION 1)
set(CMAKE_C_COMPILER xtensa-esp32-elf-gcc)
set(CMAKE_CXX_COMPILER xtensa-esp32-elf-g++)
set(CMAKE_ASM_COMPILER xtensa-esp32-elf-gcc)

# Find required packages
find_package(viam-sdk REQUIRED)
find_package(esp-idf REQUIRED)

# Add source files
add_library(hx711_loadcell SHARED
    src/hx711_loadcell/hx711_loadcell.cpp
)

# Include directories
target_include_directories(hx711_loadcell PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${ESP_IDF_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(hx711_loadcell PRIVATE
    viam-sdk::viam-sdk
    ${ESP_IDF_LIBS}
)

# ESP-IDF specific flags
target_compile_options(hx711_loadcell PRIVATE
    -mlongcalls
    -ffunction-sections
    -fdata-sections
    -fstrict-volatile-bitfields
    -Wall
    -Werror=all
    -Wno-error=unused-function
    -Wno-error=unused-but-set-variable
    -Wno-error=unused-variable
    -Wno-error=deprecated-declarations
    -Wextra
    -Wno-unused-parameter
    -Wno-sign-compare
    -ggdb
)

# Install rules
install(TARGETS hx711_loadcell
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
) 