"""
Board Initializer
"""
import os.path
import random
from data.errors import Errors


class Board:
    """
    This class defines the board, reads board files, or creates the board
    """

    def __init__(self):
        """
        Author : Jason
        Class Variables
        """
        self.walls = set()
        self.targets = set()
        self.wall = '@'
        self.empty = '#'
        self.target = '$'
        self.sizes = {
            'A': 1,
            'B': 2,
            'C': 3,
            'D': 4,
            'E': 5,
            'F': 3,
            'G': 4,
            'H': 5,
            'I': 4,
            'J': 5,
            'K': 4,
            'L': 4,
            'M': 5,
            'N': 5,
            'O': 5
        }

    def read_board(self, boardtextfile=None, piecestextfile=None, board_from_random=None):
        """
        Author : Jason
        Read Board by .txt
        '@' = wall
        '#' = empty
        '$' = targets

        Returns board in 3d array [  [walls]  ,  [targets]  ]
        walls and targets are 2d arrays containing coordinates of
        their respective element
        """

        # opening file
        if not board_from_random:
            file_path = os.path.join('./data', boardtextfile)
            if os.path.isfile(file_path):
                if boardtextfile is not None:
                    with open(file_path, encoding="utf-8") as file:
                        contents = file.read()
                        print(f'\nReading puzzle file {boardtextfile} ... Success!')
                else:
                    return ValueError(Errors.puzzle_file_empty)
            else:
                return ValueError(f'{boardtextfile} {Errors.file_not_exists}')
        else:
            contents = board_from_random[0]

        # board validation: check for walls
        assert((contents.count(self.wall) != 0)), Errors.board_no_walls

        assert((contents.count(self.wall) >= 8)), Errors.insufficient_board_size

        # Target Validation: check least 1 target
        amount_targets = contents.count(self.target)
        assert(amount_targets != 0), Errors.board_no_goal

        # getting board width and height
        contents = contents.splitlines()
        board_height = len(contents)
        board_width = max(len(line) for line in contents)

        # board validation : check board is square
        assert(board_height == board_width), Errors.board_not_square

        # track of walls and targets
        walls = []
        for row in range(board_width):
            wall_row = []
            for col in range(board_height):
                coords = (row,col)
                try:
                    if contents[row][col] == self.target:
                        self.targets.add(coords)
                    elif contents[row][col] == self.wall:
                        self.walls.add(coords)
                        wall_row.append(coords)
                except IndexError:
                    pass
            walls.append(wall_row)

        # board validation: check for holes in walls
        if (len(walls[0]) == board_width) or (len(walls[-1] == board_width)):
            # removes first and last row
            walls.pop(0)
            walls.pop(-1)
            # checking middle walls
            for row in walls:
                assert(len(row) == 2), Errors.board_hole_in_wall

        # Target Validation: check targets are all connected
        if len(self.targets) != 1:
            for target in self.targets:
                x_coord = target[0]
                y_coord = target[1]
                uppie = (x_coord,y_coord+1)
                down = (x_coord,y_coord-1)
                right = (x_coord+1,y_coord)
                left = (x_coord-1,y_coord)
                assert((uppie in self.targets) or (down in self.targets) or
                (right in self.targets) or (left in self.targets)), Errors.targets_not_connected

        # setting board
        board = [self.walls, self.targets]

        if board_from_random:
            pieces = board_from_random[1]
            result = [board, pieces, board_width, contents]
            return result

        # getting pieces
        pieces = self.read_pieces(piecestextfile)

        # checking if pieces errored
        if isinstance(pieces, ValueError):
            return pieces

        #assert(amount_targets == pieces[1]), Errors.goal_notequal_pieces

        # return board if valid
        result = [board, pieces, board_width, contents]
        return result

    def create_random_board(self, size):
        """
        Author : Jason
        create random board based on size (square)
        """
        # creating board of #s based on size
        random_board = [[self.empty for j in range(size)] for i in range(size)]

        # creating walls
        for coord in range(size):
            random_board[0][coord] = "@"
            random_board[-1][coord] = "@"
            random_board[coord][0] = "@"
            random_board[coord][-1] = "@"

        # creating targets
        # set variables
        current_number_of_targets = 1
        # random total amount of targets to be generated
        total_number_of_targets = random.randint(2,(size-2)**2)
        # random starting target point coordinate
        starting_target = [random.randint(1,size-2), random.randint(1,size-2)]
        # setting the starting target
        random_board[starting_target[0]][starting_target[1]] = self.target
        # creating list of accumulated made target coordinates
        current_targets = [[starting_target[0], starting_target[1]]]

        while current_number_of_targets != total_number_of_targets:
            # select random target to expand from
            current_target_of_expansion = current_targets[random.randint(0,len(current_targets)-1)]
            # grabbing x and y coords
            x_cord = current_target_of_expansion[0]
            y_cord = current_target_of_expansion[1]
            # creating list of coordinate possibilites based on 4 directions up down left right
            next_coords = [[x_cord,y_cord+1],[x_cord,y_cord-1],[x_cord+1,y_cord],[x_cord-1,y_cord]]
            # grabbing random coordinate possibility
            next_coord = next_coords[random.randint(0,3)]
            # if the board's next coordinate is empty
            if random_board[next_coord[0]][next_coord[1]] == self.empty:
                # set that coordinate to a target
                random_board[next_coord[0]][next_coord[1]] = self.target
                # add the current target coordinate to the list
                current_targets.append([next_coord[0] , next_coord[1]])
                # accumulate number of targets
                current_number_of_targets += 1

        # turn 2d list into string
        board = ""
        for row in random_board:
            for ele in row:
                board += ele
            board += "\n"

        pieces = self.create_random_pieces(total_number_of_targets)
        return [board, pieces]

    def create_random_pieces(self, total_targets):
        """
        Selecting random pieces depending on total targets
        """
        # accumulator pieces list: minimum 1 target
        # pieces will keep track of the sum of the pieces
        pieces = [self.sizes['A']]
        result = ['A1']

        # loop to run until sum of pieces match number of targets
        while sum(pieces) != total_targets:
            # grabbing random piece from dictionary
            random_piece = random.choice(list(self.sizes.items()))[0]
            # if sum of that random piece + the sum of the pieces already is < the total targets
            if self.sizes[random_piece] + sum(pieces) <= total_targets:
                # add to the pieces
                pieces.append(self.sizes[random_piece])
                # find out number of variant of the same pieces
                num_piece = 1
                for count in result:
                    if random_piece in count:
                        num_piece +=1
                # append to result, capable of being used in the solver
                result.append(f'{random_piece}{num_piece}')

        return [result, total_targets]

    def read_pieces(self, piecestextfile):
        """
        Reads textfile for pieces
        """
        total_targets = 0
        # opening file to read
        file_path = os.path.join('./data', piecestextfile)
        if os.path.isfile(file_path):
            if piecestextfile is not None:
                with open(file_path, encoding="utf-8") as file:
                    contents = file.read()
                    print(f'Reading puzzle file {piecestextfile} ... Success!\n')
            else:
                # check for errors
                return ValueError(Errors.puzzle_file_empty)
        else:
            return ValueError(f'{piecestextfile} {Errors.file_not_exists}')

        # setting pieces
        pieces = contents.splitlines()

        # finding total number of piece values
        for piece in pieces:
            total_targets += self.sizes[piece[0]]

        # return list of pieces and total_targets
        return [pieces, total_targets]
