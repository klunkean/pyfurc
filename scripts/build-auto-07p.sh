#!/usr/bin/bash -x
cd auto-07p
git clean -dxf
./configure --enable-plaut=no --enable-plaut04=no
make -j3
# chmod 774 cmds/@*