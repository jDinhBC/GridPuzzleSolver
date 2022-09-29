"""
List of errors
"""

class Errors:
    """
    List of Errors
    """
    insufficient_board_size = "Board must at least be 5x5 (3x3 puzzle)"
    board_no_walls = "Board does not have walls"
    board_hole_in_wall = "Board must be encased in a wall"
    board_no_goal = "Board must have at least 1 target"
    board_no_pieces = "Board must have at least 1 piece"
    board_not_square = "Board must be a uniform square"
    goal_notequal_pieces = "Number of targets do not match pieces' square count"
    file_not_exists = "File does not exist"
    targets_not_connected = "Targets are not all connected"
    puzzle_file_empty = "Puzzle file is empty"
    pieces_file_empty = "Pieces file is empty"
    invalid_input = "Invalid Input"
    