"""
main file to run everything
"""
import sys
import subprocess
from src import board, solver, printer
from data.errors import Errors

def install_packages():
    """
    This method opens requirements.txt file to install required python packages
    """
    # open file
    with open("requirements.txt", encoding="utf-8") as file:
        contents = file.read()
    # split the file
    contents = contents.splitlines()[1:]
    # iterate through packages and install them
    for package in contents:
        if package not in sys.modules:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    print("Requirements met!")

def read_files(input_data):
    """
    This method takes file names and calls the read_board method from the Board class
    returns a list of different data types to be inputted into solver
    """
    # call read_board method with inputted data
    data = board.Board().read_board(boardtextfile=input_data[0], piecestextfile=input_data[1])
    size = data[2]

    # checking if data is error
    if isinstance(data, ValueError):
        print(data)
    else:
        # call solver with inputted data and assigned to result
        result = solver.Solver(data, board.Board().sizes).get_solution()
        # call printer to print out the solution
        printer.Printer(result, size, board.Board().sizes).print()

def random(input_data):
    """
    This method takes a int size and calls the create random board method
    from the Board class and returns a list of different data types to be inputted
    into solver.
    """
    # call create_random_board with inputted size
    random_board = board.Board().create_random_board(input_data)

    # call read_board to read the data from random_board
    data = board.Board().read_board(board_from_random=random_board)
    size = data[2]

    # check if data is error
    if isinstance(data, ValueError):
        print(data)
    else:
        result = solver.Solver(data, board.Board().sizes).get_solution()
        printer.Printer(result, size, board.Board().sizes).print()

def start_program():
    """
    This method gathers inputs and calls the necessary module methods
    """
    # Enter type of inputs, by .txt or randomly generated
    print("\nEnter exit to stop program in any prompt")
    program_type = input("Enter Type input ex. (ReadFiles) (Random): ").lower()

    if program_type == "readfiles":

        # if by .txt then enter puzzle file name and pieces file name
        puzzle_file = input("\nEnter puzzle file name ex. (puzzle1.txt): ").lower()

        if puzzle_file == "exit":
            sys.exit(1)

        pieces_file = input("Enter pieces file name ex. (pieces1.txt): ").lower()

        if pieces_file == "exit":
            sys.exit(1)

        # call the read_files method with this data
        read_files([puzzle_file, pieces_file])
    elif program_type == "random":

        # if random then enter size of board
        print("\nPlease Refrain from inputting large numbers (20+)")
        size = input("Enter size of random puzzle ex. (10): ")

        if size == "exit":
            sys.exit(1)

        if size.isnumeric() is False:
            print(f'{ValueError(Errors.invalid_input)}\n')
            start_program()

        # for random wall creation
        # randomwall = input("Create Random Walls?(y/n): ").lower()

        # if (randomwall == "exit"):
        #     exit(1)

        # if (randomwall != "n") and (randomwall != "y"):
        #     print(f'{ValueError(Errors.invalid_input)}\n')
        #     start_program()

        # call random funtion with size inputted
        random(int(size))
    elif program_type == "exit":
        sys.exit(1)
    # if none of the inputs matches the cases then print error
    else:
        print(f'{ValueError(Errors.invalid_input)}\n')

    # rerun program
    start_program()

if __name__ == "__main__":
    # installs required packages
    install_packages()
    start_program()
