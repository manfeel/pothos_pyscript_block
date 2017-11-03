########################################################################
# Project setup
########################################################################
cmake_minimum_required(VERSION 2.8.9)
project(dynacode)
enable_language(CXX)

find_package(Pothos CONFIG REQUIRED)
include(PothosPythonUtil)

########################################################################
## Build and install
########################################################################
POTHOS_PYTHON_UTIL(
    TARGET dynacode
    SOURCES
        __init__.py
        dynacode.py
    FACTORIES
        "/blocks/dynacode:dynacode"
    DESTINATION dynacode
    ENABLE_DOCS
)