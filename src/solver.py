"""
Puzzle Solver
Jacob Henry
Jason Dinh
"""
from ortools.sat.python import cp_model
import time
# import board somehow when needed maybe? or just pass in board from main.py


class Solver:
    def __init__(self, data, sizes):
        """
        Interpret board state from previous modules
        into constraints + variables

        converts pieces count into variables,
        enforces that a block can be in only one position

        :param data:
        :type data: see board.py/main.py
        """
        # real attributes
        self.sizes = sizes
        self.walls = data[0][0]
        self.targets = data[0][1]
        self.pieces = data[1][0]
        self.board_width = data[2]
        self.board_height = self.board_width
        self.content = data[3]
        self.model = cp_model.CpModel()

        self.block_pos_bools = {}
        # each block needs an array of x,y booleans
        # IE "am i at 0,0? am I at 0,1?"
        # the block can only have one of those equal 1

        for piece in self.pieces:
            for rotation in ['', 'l', 'r', 'f']:
                size = sizes[piece[0]]
                pname = piece + rotation
                for block in range(size):
                    my_coord = []
                    for row in range(self.board_width):
                        for col in range(self.board_height):
                            my_coord.append(self.model.NewBoolVar(f'{pname}_{block}_{col}_{row}'))
                    # mimic defaultdict behavior
                    self.model.Add(sum(my_coord) <= 1)
                    try:
                        self.block_pos_bools[pname].append(my_coord)
                    except KeyError:
                        self.block_pos_bools[pname] = [my_coord]

        # syntax to access a position is
        # [shape_name][block_index][blockpos_index]
        # The blockpos index translated to x,y ends up as follows
        # 00, 01, 02, 03, 04 ...
        # 10, 11, 12, 13, 14 ...
        # the pos to the "top" is +width from current
        #  pos to the "bottom" is -width from current
        # the pos to the right is + 1 from current
        # the pos to the left is - 1 from current

    def A_piece(self, name):
        """
        Author: Jacob
        A pieces have no inherent constraints

         &

        :param string name: name of piece, must be in piece dictionary

        :return: piece
        :rtype: piece structure [ [vars...] [vars...] [vars..]  ]
        """
        piece = self.block_pos_bools[name]

        return piece

    def any_piece(self, name, offsets):
        """
        Author: Jacob

        adds pieces constraints, given offsets from block 0.
        block 0 is always the top most block
        (offsets above board_width do not work)
        (offsets below board_width do work)

        The anchor block must be the the left most block
        (offsets will never put blocks to the left of the anchor)

        This means that an offset of -7 is down one and to the right one
        NOT "to the left 7" which may be intuitive


        :param string name: name of piece, must be in piece dictionary
        :param list[int] offsets: list of offsets from leftmost block

        :return: piece
        :rtype: piece structure [ [vars...] [vars...] [vars..]  ]


        """
        # aliases
        piece = self.block_pos_bools[name]
        board_width = self.board_width
        # forbidden x indexes (how fat is shape)
        forbidden_x = []
        # forbidden y indexes (how tall is shape)
        forbidden_y = []

        for index, offset in enumerate(offsets):
            # first offset is to the left, second offset is to the right
            if offset > 0 and offset != board_width:
                forbidden_x.append(-offset % board_width)
            elif offset < 0 and offset != -board_width:
                forbidden_x.append((abs(offset) % board_width))
                forbidden_y.append(0)

            if offset < -board_width:
                row_offset = abs(offset) // board_width
                forbidden_y.append(row_offset)
            elif offset > board_width:
                row_offset = offset // board_width
                forbidden_y.append(board_width-row_offset)
            elif offset == -board_width:
                forbidden_y.append(0)
            elif offset == board_width:
                forbidden_y.append(board_width-1)

        # anchor to block 0
        block = piece[0]

        # add illegal position constraints for block 0
        # and relative constraints for its children
        for row, chunk in enumerate(self.chunk_list(block)):
            for col, pos in enumerate(chunk):
                position = col + row * board_width
                if col in forbidden_x or row in forbidden_y:
                    self.model.Add(block[position] == 0)
                else:
                    for index, offset in enumerate(offsets):
                        self.model.Add(piece[index+1][position+offset] == 1).OnlyEnforceIf(pos)
                        self.model.Add(piece[index+1][position+offset] == 0).OnlyEnforceIf(pos.Not())
        return piece

    def chunk_list(self, my_list):
        """
        Breaks position list into chunks of board_width size

        :param list my_list: list of ortools variables
        """
        for size in range(0, len(my_list), self.board_width):
            yield my_list[size:size + self.board_width]

    def wall_constraints(self):
        """
        Author Jacob
        Adds wall constraints by ensuring
        that no blocks are assigned to walls
        """
        for wall in self.walls:
            x_pos = wall[0]
            y_pos = wall[1]
            filled = []
            pos = x_pos + y_pos * self.board_width
            for piece in self.block_pos_bools:
                shape = self.block_pos_bools[piece]
                for block in shape:
                    filled.append(block[pos])
            # Walls cannot be filled by any block
            self.model.Add(sum(filled) == 0)

    def piece_constraints(self):
        """
        parses piece name and calls helper
        for each piece
        """
        for name in self.pieces:
            first = name[0]
            group = []
            filled = []
            if first == "A":
                group.append(self.A_piece(name))
                group.append(self.A_piece(name+'r'))
                group.append(self.A_piece(name+'l'))
                group.append(self.A_piece(name+'f'))
            elif first == "B":
                group.append(self.any_piece(name, [1]))
                group.append(self.any_piece(name+'r', [-self.board_width]))
                group.append(self.any_piece(name+'l', [-self.board_width]))
                group.append(self.any_piece(name+'f', [-self.board_width]))
            elif first == "C":
                group.append(self.any_piece(name, [1, 2]))
                group.append(self.any_piece(name+'r', [-self.board_width, -self.board_width*2]))
                group.append(self.any_piece(name+'l', [-self.board_width, -self.board_width*2]))
                group.append(self.any_piece(name+'f', [-self.board_width, -self.board_width*2]))
            elif first == "D":
                group.append(self.any_piece(name, [1, 2, 3]))
                group.append(self.any_piece(name+'r', [-self.board_width, -self.board_width*2, -self.board_width*3]))
                group.append(self.any_piece(name+'l', [-self.board_width, -self.board_width*2, -self.board_width*3]))
                group.append(self.any_piece(name+'f', [-self.board_width, -self.board_width*2, -self.board_width*3]))
            elif first == "E":
                group.append(self.any_piece(name, [1, 2, 3, 4]))
                group.append(self.any_piece(name+'r', [-self.board_width, -self.board_width*2, -self.board_width*3, -self.board_width*4]))
                group.append(self.any_piece(name+'l', [-self.board_width, -self.board_width*2, -self.board_width*3, -self.board_width*4]))
                group.append(self.any_piece(name+'f', [-self.board_width, -self.board_width*2, -self.board_width*3, -self.board_width*4]))
            elif first == "F":
                group.append(self.any_piece(name, [1, -self.board_width]))
                group.append(self.any_piece(name+'r', [1, -self.board_width+1]))
                group.append(self.any_piece(name+'l', [-self.board_width, -self.board_width+1]))
                group.append(self.any_piece(name+'f', [1, self.board_width+1]))
            elif first == "G":
                group.append(self.any_piece(name, [1, -self.board_width, -self.board_width+1]))
                group.append(self.any_piece(name+'l', [1, -self.board_width, -self.board_width+1]))
                group.append(self.any_piece(name+'r', [1, -self.board_width, -self.board_width+1]))
                group.append(self.any_piece(name+'f', [1, -self.board_width, -self.board_width+1]))
            elif first == "H":
                group.append(self.any_piece(name, [1, -self.board_width, -self.board_width+1, -self.board_width+2]))
                group.append(self.any_piece(name+'r', [1, -self.board_width, -self.board_width+1, -self.board_width*2]))
                group.append(self.any_piece(name+'l', [1, -self.board_width, -self.board_width+1, self.board_width+1]))
                group.append(self.any_piece(name+'f', [1, 2, -self.board_width+1, -self.board_width+2]))
            elif first == "I":
                # checked, it's good
                group.append(self.any_piece(name, [1, 2, -self.board_width+1]))
                group.append(self.any_piece(name+'r', [-self.board_width, -self.board_width+1, -self.board_width*2]))
                group.append(self.any_piece(name+'l', [1, -self.board_width+1, self.board_width+1]))
                group.append(self.any_piece(name+'f', [1, 2, self.board_width+1]))
            elif first == "J":
                # checked, good
                group.append(self.any_piece(name, [1, 2, -self.board_width+1, self.board_width+1]))
                group.append(self.any_piece(name+'r', [1, 2, -self.board_width+1, self.board_width+1]))
                group.append(self.any_piece(name+'l', [1, 2, -self.board_width+1, self.board_width+1]))
                group.append(self.any_piece(name+'f', [1, 2, -self.board_width+1, self.board_width+1]))
                # dont need rotate or flip because its the exact same?  XXXXXX
                # Do need flipped versions, otherwise solver will duplicate the piece <-- correct
            elif first == "K":
                # checked, fixed error in l rotation
                group.append(self.any_piece(name, [1, 2, -self.board_width+2]))
                group.append(self.any_piece(name+'r', [1, -self.board_width, -self.board_width*2]))
                group.append(self.any_piece(name+'l', [1, self.board_width+1, self.board_width*2+1]))
                group.append(self.any_piece(name+'f', [1, 2, self.board_width+2]))
            elif first == "L":
                # check fixed error in f rotatoin, added l rotation (same as r rotation)
                group.append(self.any_piece(name, [-self.board_width, -self.board_width+1, -self.board_width*2+1]))
                group.append(self.any_piece(name+'r', [1, self.board_width+1, self.board_width+2]))
                group.append(self.any_piece(name+'l', [1, self.board_width+1, self.board_width+2]))
                group.append(self.any_piece(name+'f', [1, self.board_width, -self.board_width+1]))
            elif first == "M":
                group.append(self.any_piece(name, [1, 2, -self.board_width+2, self.board_width+2]))
                group.append(self.any_piece(name+'r', [1, 2, self.board_width+1, self.board_width*2+1]))
                group.append(self.any_piece(name+'f', [1, 2, self.board_width, -self.board_width]))
                group.append(self.any_piece(name+'l', [1, 2, -self.board_width+1, -self.board_width*2+1]))
            elif first == "N":
                group.append(self.any_piece(name, [-self.board_width, 1, 2, -self.board_width+2]))
                group.append(self.any_piece(name+'r', [1, -self.board_width, -self.board_width*2, -self.board_width*2+1]))
                group.append(self.any_piece(name+'l', [1, -self.board_width+1, -self.board_width*2, -self.board_width*2+1]))
                group.append(self.any_piece(name+'f', [2, -self.board_width, -self.board_width+1, -self.board_width+2]))
            elif first == "O":
                group.append(self.any_piece(name, [-self.board_width, -self.board_width+1, -self.board_width+2, -self.board_width*2+2]))
                group.append(self.any_piece(name+'f', [-self.board_width, -self.board_width+1, -self.board_width+2, -self.board_width*2+2]))
                group.append(self.any_piece(name+'r', [1, -self.board_width+1, -self.board_width*2+1, -self.board_width*2+2]))
                group.append(self.any_piece(name+'l', [1, self.board_width+1, self.board_width*2+1,self.board_width*2+2]))

            for piece in group:
                for block in piece[0]:
                    filled.append(block)
            self.model.Add(sum(filled) == 1)
            filled = []

    def target_constraints(self):
        """
        Author Jacob
        Add target constraints by ensuring that one block
        is assigned to each target
        """
        for target in self.targets:
            x_pos = target[0]
            y_pos = target[1]
            filled = []
            pos = x_pos + y_pos * self.board_width
            for piece in self.block_pos_bools:
                shape = self.block_pos_bools[piece]
                for block in shape:
                    filled.append(block[pos])
            # target must be filled by only one block, from any piece
            self.model.Add(sum(filled) == 1)

    def get_all_vars(self):
        """
        returns all variables(positions) for all pieces.

        :return: list of all variables
        :rtype: [ ortools IntVar]
        """
        myvars = []
        for piece in self.block_pos_bools:
            shape = self.block_pos_bools[piece]
            for block in shape:
                for position in block:
                    myvars.append(position)
        self.model.Minimize(sum(myvars))
        return myvars

    def get_solution(self):
        """
        Performs the sequence of calls necessary to get a  Solution
        returns solution if solving successful, otherwise return status
        """
        self.wall_constraints()
        self.target_constraints()
        self.piece_constraints()
        solver = cp_model.CpSolver()
        myvars = self.get_all_vars()
        solver.parameters.max_time_in_seconds = 90.0
        start = time.time()
        status = solver.Solve(self.model)
        end = time.time()
        print(f'\nExecution time: {end - start}s')

        # num_blocks = solver.BestObjectiveBound()

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            active = []
            for var in myvars:
                if solver.Value(var) == 1:
                    active.append(var)
            return [active, self.content]
        return solver.StatusName(status)

#example callback to get number of solutions
#"""
class VarArraySolutionPrinterWithLimit(cp_model.CpSolverSolutionCallback):

    def __init__(self,limit, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solution_limit = limit

    def on_solution_callback(self):
        self.__solution_count += 1
        for var in self.__variables:
            if self.Value(var) == 1:
                print(var)
        #the self stopping mechanism doesn't work
        if self.__solution_count >= self.__solution_limit:
            print('Stop search after %i solutions' % self.__solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self.__solution_count

