cmake_minimum_required(VERSION 3.15)
project(asun-py CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---- Find Python ----
# For wheel builds we only need the extension-module development artifacts,
# not the embedding libraries. This is much more reliable in cibuildwheel's
# isolated environments.
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)

# ---- pybind11 ----
# Prefer system pybind11; fall back to vendored headers.
find_package(pybind11 CONFIG QUIET)
if(pybind11_FOUND)
    pybind11_add_module(asun MODULE src/asun_py.cpp)
else()
    # Use vendored headers (no pybind11 CMake infra needed — headers only)
    set(VENDOR_PBINC "${CMAKE_CURRENT_SOURCE_DIR}/vendor")
    if(NOT EXISTS "${VENDOR_PBINC}/pybind11/pybind11.h")
        message(FATAL_ERROR
            "pybind11 headers not found in vendor/pybind11/. "
            "Run: pip install pybind11  or  make  (which auto-vendors them).")
    endif()
    # Fall back to a plain shared library target
    add_library(asun MODULE src/asun_py.cpp)
    set_target_properties(asun PROPERTIES PREFIX "" SUFFIX "${Python3_EXT_SUFFIX}")
    target_include_directories(asun PRIVATE ${VENDOR_PBINC} ${Python3_INCLUDE_DIRS})
    if(TARGET Python3::Module)
        target_link_libraries(asun PRIVATE Python3::Module)
    endif()
endif()

if(DEFINED ASUN_EXTENSION_SUFFIX AND NOT "${ASUN_EXTENSION_SUFFIX}" STREQUAL "")
    set_target_properties(asun PROPERTIES PREFIX "" SUFFIX "${ASUN_EXTENSION_SUFFIX}")
endif()

target_compile_options(asun PRIVATE -O2 -Wall -Wextra)

install(TARGETS asun DESTINATION .)
