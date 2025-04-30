#include <unistd.h>
#include "game.hpp"

int main(int argc, char** argv)
{

    int cannonFirePower = 30;
    int cannonAngle = 40;

    // Parse command-line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg.rfind("firepower=", 0) == 0) { // Check if it starts with "firepower="
            try {
                cannonFirePower = std::stoi(arg.substr(10));
                if (cannonFirePower > 40 || cannonFirePower < 10){
                    std::cout << "Firepower not in range. Please choose a number between 10 and 40. FirePower will be set by default to 30." << std::endl;
                    cannonFirePower = 30;
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid firepower input: " << arg.substr(10) << "\n";
                return 1;
            }
        } else if (arg.rfind("angle=", 0) == 0) { // Check if it starts with "angle="
            try {
                cannonAngle = std::stoi(arg.substr(6));
                if (cannonAngle > 40 || cannonAngle < 20){
                    std::cout << "Angle not in range. Please choose a number between 20 and 40. Angle will be set by default to 40." << std::endl;
                    cannonAngle = 40;
                }
            } catch (const std::invalid_argument& e) {
                std::cerr << "Invalid angle input: " << arg.substr(6) << "\n";
                return 1;
            }
        } else {
            std::cerr << "Unknown argument: " << arg << "\n";
            return 1;
        }
    }

    iron_dome_game::Game game(cannonFirePower, cannonAngle);
    std::cout << "Cannon fire power is: " << cannonFirePower << ", Cannon angle is: " << cannonAngle << std::endl;
    sleep(3);
    game.play();

    return 0;
}