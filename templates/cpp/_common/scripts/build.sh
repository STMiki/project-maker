#!/usr/bin/env bash
set -e

mkdir -p build
cd build
conan install .. --build=missing
cmake .. -G 'Unix Makefiles'
cmake --build .
