#include "plate.hpp"

namespace iron_dome_game
{
Plate::Plate(Velocity velocity)
{
    trajectory.initialState.pos.x = GRID_COLUMNS - 10;
    trajectory.initialState.pos.y = 5;
    trajectory.initialState.velocity.x = velocity.x;
    trajectory.initialState.velocity.y = velocity.y;

    width   = 3;
    height  = 3;
}

//============================================================================//

void Plate::drawOnGrid(Grid &grid)
{
    auto col = pos().x;
    auto row = pos().y;

    grid.drawPixel(row, col,   '\\');
    grid.drawPixel(row, col+1, '_');
    grid.drawPixel(row, col+2, '/');

    grid.drawPixel(row+1, col  , '|');
    grid.drawPixel(row+1, col+1, ' ');
    grid.drawPixel(row+1, col+2, '|');

    grid.drawPixel(row+2, col  , '/');
    grid.drawPixel(row+2, col+1, '^');
    grid.drawPixel(row+2, col+2, '\\');
}

}