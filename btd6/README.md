# BTD6 Automation Project

This project is a personal automation script for Bloons Tower Defense 6 (BTD6). It automates the process of playing the game using predefined strategies and map placements.

\*Note: Not ready to use out of the box, as this project is intended for personal use.

## Project Structure

-   `runner.py`: The main script that handles the game automation.
-   `mapPlacementMaker.py`: A helper script to create map placement files.
-   `keybinds.py`: Contains keybindings for various actions in the game.
-   `strategies/`: Directory containing strategy files.
-   `maps/`: Directory containing map placement files.

## How to Use

### Setting Up

1. Ensure you have the required dependencies installed:

    - `pyautogui`
    - `pynput`

2. Place your strategy files in the `strategies/` directory. Each strategy file should contain instructions for the game.

3. Place your map files in the `maps/` directory. Each map file should contain the positions of towers for a specific strategy.

### Running the Automation

1. Open `runner.py` and set the `MAP_NAME`, `STRATEGY_NAME`, and `STRATEGY_EXTRA` variables to the desired values.

2. Run the script:
    ```sh
    python runner.py
    ```

### Creating Map Placement Files

1. Open `mapPlacementMaker.py` and set the `mapName` and `strategyName` variables to the desired values.

2. Run the script:

    ```sh
    python mapPlacementMaker.py
    ```

3. Follow the text instructions to place towers and set targeting.

## Notes

-   This project is intended for personal use and is not meant to be shared or used by others.
-   Ensure that the game is running in windowed fullscreen mode and the resolution matches the coordinates used in the scripts.
