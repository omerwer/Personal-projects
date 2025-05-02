#!/bin/bash

read rows cols <<< $(stty size)
cat <<EOF > ./include/config.hpp
#pragma once
#define GRID_ROWS    (${rows})
#define GRID_COLUMNS (${cols})
#define GRAVITY         (-10)
#define RENDER_FRAME_MS (50)
EOF

g++ src/*.cpp -I$(pwd)/include -lpthread -o start_playing
