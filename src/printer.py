"""
Solution Printer
"""
from PIL import Image, ImageDraw


class Printer:
    """
    This class prints out the solution in image form
    """

    def __init__(self, result, size, sizes):
        """
        Class Variables
        """
        self.result = result[0]
        if isinstance(self.result, str):
            raise ValueError(self.result)
        self.size = size
        self.original_puzzle = result[1].copy()
        self.modified_puzzle = result[1]
        self.sizes = sizes
        self.colors = {
            '@':[64,64,64],
            '#':[160,160,160],
            '$':[200,100,100],
            'A':[255,0,0],
            'B':[255,128,50],
            'C':[255,255,0],
            'D':[170,255,40],
            'E':[0,255,0],
            'F':[90,255,128],
            'G':[0,255,255],
            'H':[50,128,200],
            'I':[80,180,255],
            'J':[128,0,255],
            'K':[200,80,200],
            'L':[255,0,128],
            'M':[230,83,30],
            'N':[245,184,103],
            'O':[225,255,203]
        }

    def combine_result_puzzle(self):
        """
        combines result and puzzle into one data for easy printing
        """
        for block in self.result:
            block_split = str(block).split("_")
            block_type = block_split[0][0]
            block_x = int(block_split[2])
            block_y = int(block_split[3])
            string_to_list = list(self.modified_puzzle[block_x])
            string_to_list[block_y] = block_type
            self.modified_puzzle[block_x] = "".join(string_to_list)

    def print(self):
        """
        Prints Board of boardtextfile
        Board is a 2d array
        """
        if isinstance(self.result, str):
            print(self.result)

        # define image attributes
        cell_size = 50
        cell_border = 3

        height = self.size*cell_size
        width = self.size*cell_size

        # new image solved instance
        image_solved = Image.new(mode='RGBA', size=(height, width), color="black")
        draw_solved = ImageDraw.Draw(image_solved)

        # run combine_result_puzzle method
        self.combine_result_puzzle()

        # solved printer
        for i, row in enumerate(self.modified_puzzle):
            for j, col in enumerate(row):

                # setting color
                fill = tuple(self.colors[self.modified_puzzle[i][j]])

                # drawing cell
                draw_solved.rectangle(
                    ([(j*cell_size+cell_border, i*cell_size+cell_border),
                    ((j+1)*cell_size-cell_border,(i+1)*cell_size-cell_border)]),
                    fill=fill
                )

        image_solved.show()
        self.print_notsolved()

    def print_notsolved(self):
        """
        prints not solved solution
        """
        # define image attributes
        cell_size = 50
        cell_border = 3

        height = self.size*cell_size
        width = self.size*cell_size

        # not solved instance
        image_notsolved = Image.new(mode='RGBA', size=(height, width), color="black")
        draw_notsolved = ImageDraw.Draw(image_notsolved)

        # not solved printer
        for i, row in enumerate(self.original_puzzle):
            for j, col in enumerate(row):

                # setting color
                fill = tuple(self.colors[self.original_puzzle[i][j]])

                # drawing cell
                draw_notsolved.rectangle(
                    ([(j*cell_size+cell_border, i*cell_size+cell_border),
                    ((j+1)*cell_size-cell_border,(i+1)*cell_size-cell_border)]),
                    fill=fill
                )

        image_notsolved.show()
