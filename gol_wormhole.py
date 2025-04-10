import numpy as np
from PIL import Image
import argparse
from collections import defaultdict
import time

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255) # Use tuple for consistency even if images are grayscale

# --- Image Loading ---

def load_board(filepath):
    """Loads the starting board state from a PNG file."""
    try:
        # Use mode 'r' explicitly for reading image file
        with Image.open(filepath) as img:
            img = img.convert('RGB') # Ensure consistent RGB format
            width, height = img.size
            board = np.zeros((height, width), dtype=np.uint8)
            pixels = img.load()
            for r in range(height):
                for c in range(width):
                    # Check against tuple version of WHITE
                    if pixels[c, r][:3] == WHITE: # Slice in case of RGBA
                        board[r, c] = 1
        return board, width, height
    except FileNotFoundError:
        # Print error to standard output
        print(f"Error: Starting position file not found at {filepath}")
        exit(1) # Use built-in exit
    except Exception as e:
        # Print error to standard output
        print(f"Error loading board image {filepath}: {e}")
        exit(1) # Use built-in exit

def load_tunnels(filepath):
    """
    Loads a tunnel map (horizontal or vertical) from a PNG file.
    If a color appears more than twice, issues a warning and uses
    only the first two pixels found for that color as the portal pair.
    Returns:
        portals_by_loc (dict): Maps (row, col) -> color tuple (R, G, B) for valid portals
        portals_by_color (dict): Maps color tuple -> list of exactly [(row1, col1), (row2, col2)]
    """
    temp_portals_by_color = defaultdict(list)
    processed_portals_by_loc = {}
    final_portals_by_color = {}

    print(f"Loading tunnels from {filepath}...") # Added status print

    try:
        # Use mode 'r' explicitly for reading image file
        with Image.open(filepath) as img:
            img = img.convert('RGB') # Ensure consistent RGB format
            width, height = img.size
            pixels = img.load()
            # First pass: Collect all locations for each color
            for r in range(height):
                for c in range(width):
                    # Get RGB, ignore alpha if present
                    color = pixels[c, r][:3]
                    if color != BLACK:
                        location = (r, c)
                        temp_portals_by_color[color].append(location)

        # Second pass: Validate and process collected portals
        for color, locations in temp_portals_by_color.items():
            count = len(locations)
            if count == 2:
                # Valid pair found
                loc1, loc2 = locations[0], locations[1]
                final_portals_by_color[color] = [loc1, loc2]
                processed_portals_by_loc[loc1] = color
                processed_portals_by_loc[loc2] = color
            elif count > 2:
                # More than 2 found: Warn and use the first two
                print(f"  Warning in {filepath}: Color {color} found {count} times. Using only the first two locations: {locations[0]} and {locations[1]}.")
                loc1, loc2 = locations[0], locations[1]
                final_portals_by_color[color] = [loc1, loc2]
                processed_portals_by_loc[loc1] = color
                processed_portals_by_loc[loc2] = color
                # Locations locations[2:] are ignored for this color
            else: # count == 1 or count == 0 (though 0 shouldn't happen here)
                # Invalid input: a portal must have a pair
                print(f"  Error in {filepath}: Color {color} found only {count} time(s) at {locations}. Cannot form a portal pair. Ignoring this color.")
                # We don't add it to the final dictionaries and don't exit, just ignore.

        print(f"Finished processing tunnels for {filepath}. Found {len(final_portals_by_color)} valid wormhole pairs.")
        return processed_portals_by_loc, final_portals_by_color

    except FileNotFoundError:
        # Print error to standard output
        print(f"Error: Tunnel file not found at {filepath}")
        exit(1) # Use built-in exit
    except Exception as e:
        # Print error to standard output
        print(f"Error loading tunnel image {filepath}: {e}")
        exit(1) # Use built-in exit


# --- Neighbor Calculation with Wormholes ---

memo_neighbors = {} # Cache neighbor lookups for a given step

def get_other_portal(r, c, color, portals_by_color):
    """Finds the other portal location for a given portal."""
    locations = portals_by_color.get(color)
    # Keep ValueError for internal logic errors, as they shouldn't normally occur
    # if input validation passes, it would indicate a bug in the script itself.
    if not locations or len(locations) != 2:
        raise ValueError(f"Invalid portal data for color {color} at ({r}, {c}) during lookup")

    loc1, loc2 = locations
    if loc1 == (r, c):
        return loc2
    elif loc2 == (r, c):
        return loc1
    else:
        raise ValueError(f"Location ({r}, {c}) not found for color {color} during lookup")

# --- (get_actual_neighbor, count_live_neighbors, step functions remain unchanged) ---
def get_actual_neighbor(r, c, dr, dc, width, height,
                        h_portals_loc, h_portals_color,
                        v_portals_loc, v_portals_color):
    """
    Calculates the actual coordinates of the neighbor at relative offset (dr, dc)
    from cell (r, c), considering wormholes and precedence.
    Precedence: top > right > bottom > left
    """
    global memo_neighbors
    cache_key = (r, c, dr, dc)
    if cache_key in memo_neighbors:
        return memo_neighbors[cache_key]

    nr_res, nc_res = r + dr, c + dc # Default: standard neighbor if no wormhole applies

    # --- Check Wormholes originating from (r, c) based on precedence ---
    wormhole_applied = None # Track which type of wormhole (if any) was applied

    # 1. Top Wormhole Check (Vertical Tunnel from (r, c))
    if (r, c) in v_portals_loc and dr == -1: # Asking for top neighbor (dr=-1)
        color = v_portals_loc[(r, c)]
        r_other, c_other = get_other_portal(r, c, color, v_portals_color)
        nr_res, nc_res = r_other - 1, c_other + dc
        wormhole_applied = 'top'

    # 2. Right Wormhole Check (Horizontal Tunnel from (r, c))
    if wormhole_applied is None and (r, c) in h_portals_loc and dc == 1: # Asking for right neighbor (dc=1)
        color = h_portals_loc[(r, c)]
        r_other, c_other = get_other_portal(r, c, color, h_portals_color)
        nr_res, nc_res = r_other + dr, c_other + 1
        wormhole_applied = 'right'

    # 3. Bottom Wormhole Check (Vertical Tunnel from (r, c))
    if wormhole_applied is None and (r, c) in v_portals_loc and dr == 1: # Asking for bottom neighbor (dr=1)
        color = v_portals_loc[(r, c)]
        r_other, c_other = get_other_portal(r, c, color, v_portals_color)
        nr_res, nc_res = r_other + 1, c_other + dc
        wormhole_applied = 'bottom'

    # 4. Left Wormhole Check (Horizontal Tunnel from (r, c))
    if wormhole_applied is None and (r, c) in h_portals_loc and dc == -1: # Asking for left neighbor (dc=-1)
        color = h_portals_loc[(r, c)]
        r_other, c_other = get_other_portal(r, c, color, h_portals_color)
        nr_res, nc_res = r_other + dr, c_other - 1
        wormhole_applied = 'left'

    # --- Symmetric Check: Check if the *standard* neighbor is a portal ---
    # --- affecting the connection *back* towards (r, c)         ---
    if wormhole_applied is None:
        nr_std, nc_std = r + dr, c + dc

        # Check potential standard neighbor coords are within bounds before checking portals
        if 0 <= nr_std < height and 0 <= nc_std < width:

            # 1. Top neighbor (nr_std, nc_std) has Bottom Wormhole (Vertical Tunnel)?
            #    Applies if we are coming from the cell *above* (nr_std, nc_std) -> dr = 1
            if (nr_std, nc_std) in v_portals_loc and dr == 1:
                color = v_portals_loc[(nr_std, nc_std)]
                r_other, c_other = get_other_portal(nr_std, nc_std, color, v_portals_color)
                nr_res, nc_res = r_other - 1, c_other + (c - nc_std)
                wormhole_applied = 'symm_top_target'

            # 2. Left neighbor (nr_std, nc_std) has Right Wormhole (Horizontal Tunnel)?
            #    Applies if we are coming from the cell *left* of (nr_std, nc_std) -> dc = -1
            elif wormhole_applied is None and (nr_std, nc_std) in h_portals_loc and dc == -1:
                color = h_portals_loc[(nr_std, nc_std)]
                r_other, c_other = get_other_portal(nr_std, nc_std, color, h_portals_color)
                nr_res, nc_res = r_other + (r - nr_std), c_other - 1
                wormhole_applied = 'symm_left_target'

            # 3. Bottom neighbor (nr_std, nc_std) has Top Wormhole (Vertical Tunnel)?
            #    Applies if we are coming from the cell *below* (nr_std, nc_std) -> dr = -1
            elif wormhole_applied is None and (nr_std, nc_std) in v_portals_loc and dr == -1:
                color = v_portals_loc[(nr_std, nc_std)]
                r_other, c_other = get_other_portal(nr_std, nc_std, color, v_portals_color)
                nr_res, nc_res = r_other + 1, c_other + (c - nc_std)
                wormhole_applied = 'symm_bottom_target'

            # 4. Right neighbor (nr_std, nc_std) has Left Wormhole (Horizontal Tunnel)?
            #    Applies if we are coming from the cell *right* of (nr_std, nc_std) -> dc = 1
            elif wormhole_applied is None and (nr_std, nc_std) in h_portals_loc and dc == 1:
                color = h_portals_loc[(nr_std, nc_std)]
                r_other, c_other = get_other_portal(nr_std, nc_std, color, h_portals_color)
                nr_res, nc_res = r_other + (r - nr_std), c_other + 1
                wormhole_applied = 'symm_right_target'


    # Cache the result before returning
    memo_neighbors[cache_key] = (nr_res, nc_res)
    return nr_res, nc_res


def count_live_neighbors(r, c, board, width, height,
                         h_portals_loc, h_portals_color,
                         v_portals_loc, v_portals_color):
    """Counts live neighbors for cell (r, c) considering wormholes."""
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue # Skip self

            nr, nc = get_actual_neighbor(r, c, dr, dc, width, height,
                                         h_portals_loc, h_portals_color,
                                         v_portals_loc, v_portals_color)

            # Check if the neighbor coordinates are within the board bounds
            if 0 <= nr < height and 0 <= nc < width:
                count += board[nr, nc]
            # Cells outside the boundary are permanently dead (contribute 0)

    return count

def step(board, width, height,
         h_portals_loc, h_portals_color,
         v_portals_loc, v_portals_color):
    """Performs one iteration of the Game of Life with Wormholes."""
    global memo_neighbors
    memo_neighbors.clear() # Clear neighbor cache for the new step

    new_board = np.zeros_like(board)
    for r in range(height):
        for c in range(width):
            live_neighbors = count_live_neighbors(r, c, board, width, height,
                                                  h_portals_loc, h_portals_color,
                                                  v_portals_loc, v_portals_color)
            current_state = board[r, c]

            # Apply Game of Life rules
            if current_state == 1: # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_board[r, c] = 0 # Dies
                else:
                    new_board[r, c] = 1 # Lives
            else: # Dead cell
                if live_neighbors == 3:
                    new_board[r, c] = 1 # Becomes alive

    return new_board
# --- End unchanged functions ---

# --- Output ---

def save_board(board, filepath):
    """Saves the board state to a PNG file."""
    height, width = board.shape
    img = Image.new('RGB', (width, height), color=BLACK)
    pixels = img.load()
    for r in range(height):
        for c in range(width):
            if board[r, c] == 1:
                pixels[c, r] = WHITE
    try:
        img.save(filepath)
    except Exception as e:
        # Print error to standard output
        print(f"Error saving board image {filepath}: {e}")
        # We might not want to exit here, maybe just report the error and continue?
        # Depending on requirements. Exiting might be safer if saving fails.
        # exit(1)


# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(description="Run Conway's Game of Life with Wormholes.")
    # argparse handles relative paths correctly, so no change needed here.
    parser.add_argument("input_dir", help="Directory containing starting_position.png, horizontal_tunnel.png, and vertical_tunnel.png")
    args = parser.parse_args()

    input_dir = args.input_dir
    # Construct relative paths within the input directory
    base_path = input_dir.rstrip('/') # Remove potential trailing slash
    start_pos_file = f"{base_path}/starting_position.png"
    h_tunnel_file = f"{base_path}/horizontal_tunnel.png"
    v_tunnel_file = f"{base_path}/vertical_tunnel.png"

    print("Loading initial state...")
    board, width, height = load_board(start_pos_file)
    print(f"Board dimensions: {width}x{height}")

    print("Loading horizontal tunnels...")
    h_portals_loc, h_portals_color = load_tunnels(h_tunnel_file)
    print(f"Found {len(h_portals_color)} horizontal wormholes.")

    print("Loading vertical tunnels...")
    v_portals_loc, v_portals_color = load_tunnels(v_tunnel_file)
    print(f"Found {len(v_portals_color)} vertical wormholes.")

    output_iterations = {1, 10, 100, 1000}
    max_iterations = max(output_iterations)

    print(f"Starting simulation for {max_iterations} iterations...")
    start_time = time.time()

    # Single Simulation Loop
    for i in range(1, max_iterations + 1):
        board = step(board, width, height,
                     h_portals_loc, h_portals_color,
                     v_portals_loc, v_portals_color)

        if i in output_iterations:
            output_filename = f"{base_path}/{i}.png"
            print(f"Saving state after iteration {i} to {output_filename}...")
            save_board(board, output_filename)

        if i % 50 == 0 and i not in output_iterations:
             current_time = time.time()
             elapsed = current_time - start_time
             print(f"  Completed iteration {i}/{max_iterations} ({elapsed:.2f}s elapsed)")

    end_time = time.time()
    print(f"\nSimulation finished in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()


