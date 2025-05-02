#include "config.hpp"
#include "cannon.hpp"

namespace iron_dome_game
{
    Cannon::Cannon(){
        trajectory.initialState.pos.x = 3;
        trajectory.initialState.pos.y = 0;

        width    = 6;
        height   = 3;
    }

    void Cannon::drawOnGrid(Grid &grid)
    {
        // It's a two barrel cannon but it only shots one rocket for simplicity
        auto col = pos().x;
        auto row = pos().y;

        auto distance = 6;

        for (int i = 0; i < 4; ++i){
            grid.drawPixel(row+i, col+i, '/'); // Left cannon side
            grid.drawPixel(row+i, col+distance+i, '/'); // Right cannon side
            grid.drawPixel(row+1, col+2+i, '_'); // Cannon's bottom
            if (i == 3)
                grid.drawPixel(row+1, col+6, '_');
        }

        // Cannon's barrels outline
        for (int j = 1; j < 6; j=j+2){
            grid.drawPixel(row+2, col+j+1, '/');
            grid.drawPixel(row+3, col+j+2, '/');
        }

        // Cannon's barrels top
        grid.drawPixel(row+4, col+4, '_');
        grid.drawPixel(row+4, col+5, '_');
        grid.drawPixel(row+4, col+8, '_');
        grid.drawPixel(row+4, col+9, '_');
    }
}