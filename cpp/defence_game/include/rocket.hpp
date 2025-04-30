#pragma once

#include "entity.hpp"

namespace iron_dome_game
{
struct Rocket : public Entity
{
    Rocket(Velocity velocity);
    ~Rocket() = default;

    void drawOnGrid(Grid &grid) override;

    EntityType type() override { return EntityType::ROCKET; }

    bool isStatic() { return false; }
};

}