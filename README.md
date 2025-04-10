# Conway's Game of Life with Wormholes

This Python script implements a modified version of Conway's Game of Life, incorporating "wormholes" that connect distant parts of the grid, as a variation of Conway's Game of Life.

The simulation reads an initial state and wormhole configurations from PNG images and outputs the state of the simulation after specific iterations (1, 10, 100, 1000) as PNG images.

## Features

1. Implements the standard rules of Conway's Game of Life as follows:

    *The universe of the Game of Life is an infinite, two-dimensional orthogonal grid of square cells, each of which is in one of two states: alive or dead (populated or unpopulated). Every cell interacts with its eight neighbors, which are the cells that are horizontally, vertically, or diagonally adjacent. At each step in time, the following transitions occur:*
    1. Any live cell with fewer than two live neighbors dies, as if by underpopulation.
    2. Any live cell with two or three live neighbors lives on to the next generation.
    3. Any live cell with more than three live neighbors dies, as if by overpopulation.
    4. Any dead cell with exactly three live neighbors becomes alive cell, as if by reproduction

2.   Simulates wormholes based on horizontal and vertical tunnel map images.

    Wormhole Dynamics
    The underlying mechanism of these wormholes lies in the manipulation of the 2D space. Unlike the classic Game of Life, where cells interact solely with their immediate neighbors, this version introduces the concept of non-local interaction. Cells that are seemingly distant from each other can now become neighbors by virtue of being connected through a wormhole.

    Horizontal Tunnel Bitmap
    The structure and connectivity of these wormholes are encoded within a horizontal tunnel bit map. In this bitmap, pixels sharing the same color represent the boundaries of a wormhole. These boundaries act as portals, allowing cells to traverse from one location on the grid to another. A crucial rule of this bitmap is that for any given non-black RGB color value, there exist exactly two pixels with that color. This ensures that each wormhole has precisely two entry/exit points.

    Vertical Tunnel Bitmap
    Similarly, there is a vertical tunnel provided, which wraps around the vertical axis. The vertical orientation of the tunnel allows for movement or flow along the vertical axis, while the wrapping design ensures that this movement is contained within the tunnel structure.

3.   Handles wormhole precedence rules for conflict resolution (Top > Right > Bottom > Left).
4.   Reads input configuration from PNG files (`starting_position.png`, `horizontal_tunnel.png`, `vertical_tunnel.png`).
5.   Outputs simulation state snapshots as PNG files (`1.png`, `10.png`, `100.png`, `1000.png`).
6.   Uses relative paths for input/output directories.
7.   Includes basic error handling for file loading and tunnel validation.

## Prerequisites

*   **Python 3.x**
*   **Required Libraries:** `Pillow` (for image manipulation) and `NumPy` (for efficient grid operations).

## Installation

1.  **Navigate:** Ensure you have the project structure described below.
2.  **Install Dependencies:** Open your terminal or command prompt, navigate *into* the `srcs/` directory (if you aren't already there), and run:
    ```bash
    pip install Pillow numpy
    ```
    *(It's recommended to use a Python virtual environment)*

## Directory Structure

The script assumes the following directory structure:

```
your-project-root/
└── srcs/
    ├── gol_wormhole.py         # <-- The Python script
    ├── problem-01/             # <-- Example input directory 1
    │   ├── starting_position.png
    │   ├── horizontal_tunnel.png
    │   └── vertical_tunnel.png
    ├── problem-02/             # <-- Example input directory 2
    │   ├── starting_position.png
    │   ├── horizontal_tunnel.png
    │   └── vertical_tunnel.png
    └── ...                     # <-- Other problem directories
```

## Input Files

Inside *each* problem directory (e.g., `GameofLifeWormhole/problem-01/`), the script expects the following three PNG files:

1.  **`starting_position.png`**:
    *   A binary image representing the initial state.
    *   **White pixels** (`(255, 255, 255)`) represent **live** cells.
    *   **Black pixels** (`(0, 0, 0)`) represent **dead** cells.
    *   Cells outside the image boundaries are considered permanently dead.

2.  **`horizontal_tunnel.png`**:
    *   A color image defining horizontal wormholes.
    *   **Black pixels** (`(0, 0, 0)`) are ignored.
    *   Any other **non-black color** indicates a horizontal portal entrance/exit.
    *   **Crucially:** For every non-black color present, there must be *exactly two* pixels with that color in this image, forming a wormhole pair.

3.  **`vertical_tunnel.png`**:
    *   A color image defining vertical wormholes.
    *   Format and rules are the same as `horizontal_tunnel.png`, but these define vertical connections.

**Constraint:** All three input PNG files within a problem directory must have the exact same width and height.

## Usage

**Recommended:** Navigate your terminal *into* the `GameofLifeWormhole/` directory first. 

```bash
cd path/to/your-project-root/GameofLifeWormhole/
```

Then, run the script, providing the **relative path** to the specific input directory (which is now just the directory name):

```bash
python gol_wormhole.py <problem_directory_name>
```

**Examples (when inside the `GameofLifeWormhole/` directory):**

*   To process the input files in `GameofLifeWormhole/problem-01/`:
    ```bash
    python gol_wormhole.py problem-01
    ```
*   To process the input files in `srcs/problem-02/`:
    ```bash
    python gol_wormhole.py problem-02
    ```

*(Alternatively, if you run the command from the `your-project-root/` directory, you would need to include `srcs/` in the paths: `python GameofLifeWormhole/gol_wormhole.py srcs/problem-01`)*

## Output Files

The script will generate the following PNG files **inside** the specified `<problem_directory_name>` (e.g., inside `srcs/problem-01/`):

*   **`1.png`**: The state of the board after 1 iteration.
*   **`10.png`**: The state of the board after 10 iterations.
*   **`100.png`**: The state of the board after 100 iterations.
*   **`1000.png`**: The state of the board after 1000 iterations.

These output images use the same format as `starting_position.png` (white for live, black for dead).

## How it Works

1.  **Load Data:** Reads the initial board state and parses the horizontal/vertical tunnel maps from the specified problem directory, validating the wormhole pairs.
2.  **Simulate:** Runs the Game of Life simulation step-by-step, up to the maximum required iteration (1000).
3.  **Calculate Neighbors:** In each step, for every cell, it calculates its 8 neighbors considering standard adjacency, wormholes (originating from the cell or the neighbor), and precedence rules (Top > Right > Bottom > Left).
4.  **Apply Rules:** Applies the standard Game of Life rules based on the live neighbor count to determine the cell's state in the *next* iteration.
5.  **Save Snapshots:** When the iteration counter reaches 1, 10, 100, or 1000, the current state of the board is saved to the corresponding PNG file within the problem directory. The simulation runs continuously.

## Notes

*   **Stable States:** If the simulation reaches a stable pattern before 1000 iterations, the output files for later iterations might be identical. This is expected behavior.
*   **Efficiency:** The script uses NumPy for faster array operations and caches neighbor lookups within a single step.