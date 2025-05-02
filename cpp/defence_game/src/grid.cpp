#include <iostream>

#include "grid.hpp"
#include "entity.hpp"

namespace iron_dome_game
{

void Grid::draw() 
{
    for (int i = GRID_ROWS - 1; i >= 0; --i)
    {
        for (int j = 0; j < GRID_COLUMNS; ++j)
        {
            std::cout << m_grid[i][j];
        }
        std::cout << std::endl;
    }
}

//============================================================================//

bool Grid::isOffGrid(std::shared_ptr<Entity> ent) {
    auto pos = ent->pos();
    return (pos.x < 0 || pos.x >= GRID_COLUMNS || pos.y < 0 || pos.y >= GRID_ROWS);
}


void Grid::refresh() 
{
    // Draw background
    forEveryPixel(
        [this](int row, int col)
        {
            m_grid[row][col] = ' ';
        }
    );

    // Draw ground
    forEveryPixel(
        [this](int row, int col)
        {
            m_grid[row][col] = '_';
        },
        1
    );

    std::lock_guard<std::mutex> lock(m);
    m_entities.remove_if([this](const auto& entity) {
        if (isOffGrid(entity)) {
            return true;
        } else {
            entity->drawOnGrid(*this);
            return false;
        }
    });
}

//============================================================================//

bool Grid::drawPixel(uint16_t row, uint16_t col, char pixel) 
{
    if (row >= 0 && row < rows() && col >= 0 && col < columns() && pixel != ' ')
    {
        m_grid[row][col] = pixel;
        return true;
    }
    return false;
}

//============================================================================//

void Grid::forEveryPixel(std::function<void(int row, int col)> function, const int rowCount, const int columnCount) 
{
    for (int i = 0; i < rowCount; ++i)
    {
        for (int j = 0; j < columnCount; ++j)
        {
            function(i, j);
        }
    }
}

//============================================================================//

    bool isPosInsideBbox(Pos point, BoundingBox bbox){
        return (point.x >= bbox.p1.x && point.x <= bbox.p2.x &&
                point.y >= bbox.p1.y && point.y <= bbox.p2.y);
    }

    bool Grid::intersects(std::shared_ptr<Entity> first, std::shared_ptr<Entity> second) 
    {
        return isPosInsideBbox(first->pos(), second->boundingBox()) || isPosInsideBbox(second->pos(), first->boundingBox());
    }


//============================================================================//

    uint16_t Grid::checkHits() 
    {
        uint16_t hits = 0;
        std::vector<std::shared_ptr<Entity>> to_remove;
        for (auto ent : m_entities){
            bool start_comparing = false;
            if (isOffGrid(ent)){
                continue;
            }
            else {
                for (auto ent2 : m_entities){
                    if (start_comparing){
                        if (ent == ent2)
                            continue;
                        if (intersects(ent, ent2) && 
                            ent->type() !=EntityType::PITCHER && ent2->type() !=EntityType::PITCHER &&
                            ent->type() !=EntityType::CANNON && ent2->type() !=EntityType::CANNON){
                            if ((ent->type() == EntityType::PLATE && ent2->type() == EntityType::ROCKET) ||
                            (ent->type() == EntityType::ROCKET && ent2->type() == EntityType::PLATE)) {
                                hits++;
                            }
                            to_remove.push_back(ent);
                            to_remove.push_back(ent2);
                        }
                    }
                    if (ent == ent2) {
                        start_comparing = true;
                    }
                }
            }
        }

        m.lock();
        for (auto entity : to_remove) {
            m_entities.remove(entity);
        }
        m.unlock();

        return hits;
    }

}