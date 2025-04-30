#include "rocket.hpp"

namespace iron_dome_game
{
    Rocket::Rocket(Velocity velocity)
    {
        trajectory.initialState.pos.x = GRID_COLUMNS - 190;
        trajectory.initialState.pos.y = 5;
        trajectory.initialState.velocity.x = velocity.x;
        trajectory.initialState.velocity.y = velocity.y;

        width   = 3;
        height  = 3;
    }

    //============================================================================//

    void Rocket::drawOnGrid(Grid &grid)
    {
        auto col = pos().x;
        auto row = pos().y;

        auto distance = 2;

        grid.drawPixel(row, col,   '/');
        grid.drawPixel(row+1, col+1, '/');
        grid.drawPixel(row+2, col+2, '/');

        grid.drawPixel(row, col+distance,   '/');
        grid.drawPixel(row+1, col+distance+1, '/');
        grid.drawPixel(row+2, col+distance+2, '/');
    }

}