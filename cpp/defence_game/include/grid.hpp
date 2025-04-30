#pragma once

#include <functional>
#include <list>
#include <vector>
#include <memory>
#include <mutex>

#include "config.hpp"
#include "trajectory.hpp"

namespace iron_dome_game
{

struct Entity;

// Two points, representing a rectangle around an entity
struct BoundingBox
{
    Pos p1;
    Pos p2;
};

class Grid
{
public:
    Grid() = default;
    ~Grid() = default;

    void draw();
    void refresh();

    uint16_t rows() { return GRID_ROWS; }
    uint16_t columns() { return GRID_COLUMNS; }

    bool drawPixel(uint16_t row, uint16_t col, char pixel);

    void addEntity(std::shared_ptr<Entity> entity) {
            std::lock_guard<std::mutex> lock(m);
            m_entities.push_back(entity);
        }

    bool isOffGrid(std::shared_ptr<Entity> entity);

    uint16_t checkHits();

private:
    void forEveryPixel(std::function<void(int row, int col)> function, const int rowCount = GRID_ROWS, const int columnCount = GRID_COLUMNS);

    static bool intersects(std::shared_ptr<Entity> first, std::shared_ptr<Entity> second);

    char m_grid[GRID_ROWS][GRID_COLUMNS];

    std::list<std::shared_ptr<Entity>> m_entities;

    std::mutex m;
};
}