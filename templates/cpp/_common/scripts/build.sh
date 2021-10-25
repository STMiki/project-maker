#!/usr/bin/env bash
set -e

mkdir -p build
cd build
if [ "$1" == "debug" ]; then
    conan install .. --build=missing --profile debug
    cmake .. -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Debug
else
    conan install .. --build=missing
    cmake .. -G 'Unix Makefiles'
fi
cmake --build .
