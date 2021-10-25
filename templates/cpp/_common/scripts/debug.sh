#!/usr/bin/env bash

sh scripts/build.sh debug
gdb build/bin/<PNAME>
