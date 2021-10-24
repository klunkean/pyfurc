#!/usr/bin/bash -x
cd src/pyfurc/auto-07p
./configure --enable-plaut=no --enable-plaut04=no
make -j3
