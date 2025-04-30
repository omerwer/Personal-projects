#include "config.hpp"
#include "pitcher.hpp"

namespace iron_dome_game
{
Pitcher::Pitcher()
{
    trajectory.initialState.pos.x = GRID_COLUMNS - 7;
    trajectory.initialState.pos.y = 0;

    width    = 6;
    height   = 5;
}

//============================================================================//

void Pitcher::drawOnGrid(Grid &grid)
{
    auto col = pos().x;
    auto row = pos().y;

    grid.drawPixel(row, col  , '|');
    grid.drawPixel(row, col+1, ' ');
    grid.drawPixel(row, col+2, ' ');
    grid.drawPixel(row, col+3, ' ');
    grid.drawPixel(row, col+4, '|');

    grid.drawPixel(row+1, col  , '/');
    grid.drawPixel(row+1, col+1, ' ');
    grid.drawPixel(row+1, col+2, '|');
    grid.drawPixel(row+1, col+3, ' ');
    grid.drawPixel(row+1, col+4, '\\');

    grid.drawPixel(row+2, col  , ' ');
    grid.drawPixel(row+2, col+1, ' ');
    grid.drawPixel(row+2, col+2, '|');
    grid.drawPixel(row+2, col+3, ' ');
    grid.drawPixel(row+2, col+4, ' ');

    grid.drawPixel(row+3, col  , '/');
    grid.drawPixel(row+3, col+1, '^');
    grid.drawPixel(row+3, col+2, '|');
    grid.drawPixel(row+3, col+3, '^');
    grid.drawPixel(row+3, col+4, '\\');

    grid.drawPixel(row+4, col,   ' ');
    grid.drawPixel(row+4, col+1, ' ');
    grid.drawPixel(row+4, col+2, '*');
    grid.drawPixel(row+4, col+3, ' ');
    grid.drawPixel(row+4, col+4, ' ');
}

}