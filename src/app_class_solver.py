import pygame, sys, requests         #pygame for graphics
import pygame, sys
import requests
from bs4 import BeautifulSoup
from settings import *
from buttonClass import *
from sudoku_solver import *

class App_Solver:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.running = True
        self.grid = finishedBoard                 #for grawing grid
        self.selected = None                      #for selecting a cell
        self.mousePos = None                      #when mousePos which cell we click
        #self.board = []
        self.state = "playing"
        self.finished = False
        self.cellChanged = False
        self.playingButtons = []             #Buttons List
        self.lockedCells = []
        self.incorrectCells = []
        self.font = pygame.font.SysFont("arial", cellSize//2)      #for adding numbers to the cells
        self.grid = []
        
        #self.getPuzzle() 
                            # Extracting puzzzle fom Web
        self.load()

    def run(self, board):
        # print(board)
        # self.getBoard(board)
        while self.running:
            if self.state == "playing":
                self.playing_events()
                self.playing_update()
                self.playing_draw()
                self.getPuzzle(board)

        pygame.quit()
        sys.exit()

    # def getBoard(self,board):
    #     self.board = board

###### PLAYING STATE FUNCTIONS #####

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:                    #Quitting
                self.running = False

            # User clicks
            if event.type == pygame.MOUSEBUTTONDOWN:    
                selected = self.mouseOnGrid()
                if selected:
                    self.selected = selected
                else:
                    self.selected = None
                    for button in self.playingButtons:
                        if button.highlighted:
                            button.click()

            # User types a key
            if event.type == pygame.KEYDOWN:
                if self.selected != None and self.selected not in self.lockedCells:       #entering key in non locked cells
                    if self.isInt(event.unicode):
                        # cell changed
                        self.grid[self.selected[1]][self.selected[0]] = int(event.unicode)
                        self.cellChanged = True

    def playing_update(self):
        self.mousePos = pygame.mouse.get_pos()
        for button in self.playingButtons:
            button.update(self.mousePos)

        if self.cellChanged:
            self.incorrectCells = []
            if self.allCellsDone():
                # Check if board is correct
                self.checkAllCells()
                if len(self.incorrectCells) == 0:
                    self.finished = True


    def playing_draw(self):
        self.window.fill(WHITE)                # white 600 X 600 board

        for button in self.playingButtons:
            button.draw(self.window)

        if self.selected:                             # highlighting selected cell
            self.drawSelection(self.window, self.selected)

        self.shadeLockedCells(self.window, self.lockedCells)    #Locking cells
        self.shadeIncorrectCells(self.window, self.incorrectCells)

        self.drawNumbers(self.window)

        self.drawGrid(self.window)                 #drawing grid
        pygame.display.update()
        self.cellChanged = False

##### BOARD CHECKING FUNCTIONS #####
    def allCellsDone(self):
        for row in self.grid:
            for number in row:
                if number == 0:
                    return False
        return True

    def checkAllCells(self):
        self.checkRows()
        self.checkCols()
        self.checkSmallGrid()

    def checkSmallGrid(self):
        for x in range(3):
            for y in range(3):
                possibles = [1,2,3,4,5,6,7,8,9]
                # print("re-setting possibles")
                for i in range(3):
                    for j in range(3):
                        # print(x*3+i, y*3+j)
                        xidx = x*3+i
                        yidx = y*3+j
                        if self.grid[yidx][xidx] in possibles:
                            possibles.remove(self.grid[yidx][xidx])
                        else:
                            if [xidx, yidx] not in self.lockedCells and [xidx, yidx] not in self.incorrectCells:
                                self.incorrectCells.append([xidx, yidx])
                            if [xidx, yidx] in self.lockedCells:
                                for k in range(3):
                                    for l in range(3):
                                        xidx2 = x*3+k
                                        yidx2 = y*3+l
                                        if self.grid[yidx2][xidx2] == self.grid[yidx][xidx] and [xidx2, yidx2] not in self.lockedCells:
                                            self.incorrectCells.append([xidx2, yidx2])

    def checkRows(self):
        for yidx, row in enumerate(self.grid):
            possibles = [1,2,3,4,5,6,7,8,9]
            for xidx in range(9):
                if self.grid[yidx][xidx] in possibles:         # those which are already present in the grid is removed only 
                    possibles.remove(self.grid[yidx][xidx])
                else:
                    if [xidx, yidx] not in self.lockedCells and [xidx, yidx] not in self.incorrectCells:    #if ithe entry is not present in the poss means we have already seen it
                        self.incorrectCells.append([xidx, yidx])      #avoiding adding incorrect entry multiple times  
                    if [xidx, yidx] in self.lockedCells:      #if the unlocked entry accessed first 
                        for k in range(9):
                            if self.grid[yidx][k] == self.grid[yidx][xidx] and [k, yidx] not in self.lockedCells:
                                self.incorrectCells.append([k, yidx])


    def checkCols(self):
        for xidx in range(9):
            possibles = [1,2,3,4,5,6,7,8,9]
            for yidx, row in enumerate(self.grid):
                if self.grid[yidx][xidx] in possibles:
                    possibles.remove(self.grid[yidx][xidx])
                else:
                    if [xidx, yidx] not in self.lockedCells and [xidx, yidx] not in self.incorrectCells:
                        self.incorrectCells.append([xidx, yidx])
                    if [xidx, yidx] in self.lockedCells:
                        for k, row in enumerate(self.grid):
                            if self.grid[k][xidx] == self.grid[yidx][xidx] and [xidx, k] not in self.lockedCells:
                                self.incorrectCells.append([xidx, k])

##### HELPER FUNCTIONS #####
    def getPuzzle(self,board):
        # html_doc = requests.get("https://nine.websudoku.com/?level={}".format(difficulty)).content   #here we get html file
        # soup = BeautifulSoup(html_doc, features= "html.parser")                   
        # ids = ['f00', 'f01', 'f02', 'f03', 'f04', 'f05', 'f06', 'f07', 'f08', 'f10', 'f11',  #these are the IDs of the sudoku entry
        # 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f20', 'f21', 'f22', 'f23',
        # 'f24', 'f25', 'f26', 'f27', 'f28', 'f30', 'f31', 'f32', 'f33', 'f34', 'f35',
        # 'f36', 'f37', 'f38', 'f40', 'f41', 'f42', 'f43', 'f44', 'f45', 'f46', 'f47',
        # 'f48', 'f50', 'f51', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57', 'f58', 'f60',
        # 'f61', 'f62', 'f63', 'f64', 'f65', 'f66', 'f67', 'f68', 'f70', 'f71', 'f72',
        # 'f73', 'f74', 'f75', 'f76', 'f77', 'f78', 'f80', 'f81', 'f82', 'f83', 'f84',
        # 'f85', 'f86', 'f87', 'f88']
        # data = []
        # for cid in ids:
        #     data.append(soup.find('input', id=cid))            #extracting the ids
        # board = [[0 for x in range(9)] for x in range(9)]
        # for index, cell in enumerate(data):
        #     try:
        #         board[index//9][index%9] = int(cell['value'])   #extracting the values of IDs 
        #     except:
        #         pass

        # self.writeFile(board)
        # #print(board)
        self.grid = board
        #print(board)
        self.load()


    def writeFile(self,board):
        output_file = open("SudokuPuzzle.txt", "w+")
        for i in range(9):
            for j in range(9):
                if(board[i][j]==0):
                    output_file.write(".")
                else:
                    output_file.write(str(board[i][j]))
            output_file.write("\n")


    def shadeIncorrectCells(self, window, incorrect):
        for cell in incorrect:
            pygame.draw.rect(window, INCORRECTCELLCOLOUR, (cell[0]*cellSize+gridPos[0], cell[1]*cellSize+gridPos[1], cellSize, cellSize))

    def shadeLockedCells(self, window, locked):
        for cell in locked:
            pygame.draw.rect(window, LOCKEDCELLCOLOUR, (cell[0]*cellSize+gridPos[0], cell[1]*cellSize+gridPos[1], cellSize, cellSize))

    def drawNumbers(self, window):                            #iterating over the sudoku if entry not zero print
        for yidx, row in enumerate(self.grid):
            for xidx, num in enumerate(row):
                if num != 0:                                              
                    pos = [(xidx*cellSize)+gridPos[0], (yidx*cellSize)+gridPos[1]]
                    self.textToScreen(window, str(num), pos)

    def drawSelection(self, window, pos):            # highlighting blue cells
        pygame.draw.rect(window, LIGHTBLUE, ((pos[0]*cellSize)+gridPos[0], (pos[1]*cellSize)+gridPos[1], cellSize, cellSize))

    def drawGrid(self, window):                                                #Drawing Grid
        pygame.draw.rect(window, BLACK, (gridPos[0], gridPos[1], WIDTH-150, HEIGHT-150), 2)
        for x in range(9):
            pygame.draw.line(window, BLACK, (gridPos[0]+(x*cellSize), gridPos[1]), (gridPos[0]+(x*cellSize), gridPos[1]+450), 2 if x % 3 == 0 else 1) #if condition is for making some lines thick
            pygame.draw.line(window, BLACK, (gridPos[0], gridPos[1]+(x*cellSize)), (gridPos[0]+450, gridPos[1]++(x*cellSize)), 2 if x % 3 == 0 else 1)

    def mouseOnGrid(self):                                                      # returning the position of the cell where we click
        if self.mousePos[0] < gridPos[0] or self.mousePos[1] < gridPos[1]:
            return False
        if self.mousePos[0] > gridPos[0]+gridSize or self.mousePos[1] > gridPos[1]+gridSize:
            return False
        return ((self.mousePos[0]-gridPos[0])//cellSize, (self.mousePos[1]-gridPos[1])//cellSize)

    def loadButtons(self):                                      #load Buttons
        self.playingButtons.append(Button(  20, 40, WIDTH//7, 40,
                                            function=self.checkAllCells,
                                            colour=(27,142,207),
                                            text="Check"))
        self.playingButtons.append(Button(  140, 40, WIDTH//7, 40,
                                            colour=(117,172,112),
                                            function=self.getPuzzle,
                                            params="1",
                                            text="Easy"))
        self.playingButtons.append(Button(  WIDTH//2-(WIDTH//7)//2, 40, WIDTH//7, 40,
                                            colour=(204,197,110),
                                            function=self.getPuzzle,
                                            params="2",
                                            text="Medium"))
        self.playingButtons.append(Button( 380, 40, WIDTH//7, 40,
                                            colour=(199,129,48),
                                            function=self.getPuzzle,
                                            params="3",
                                            text="Hard"))
        self.playingButtons.append(Button(  500, 40, WIDTH//7, 40,
                                            colour=(207,68,68),
                                            function=self.getPuzzle,
                                            params="4",
                                            text="Evil"))

    def textToScreen(self, window, text, pos):                  #printing text i.e converting to img
        font = self.font.render(text, False, BLACK)
        fontWidth = font.get_width()
        fontHeight = font.get_height()
        pos[0] += (cellSize-fontWidth)//2
        pos[1] += (cellSize-fontHeight)//2
        window.blit(font, pos)

    def load(self):
        self.playingButtons = []
       # self.loadButtons()
        self.lockedCells = []
        self.incorrectCells = []
        self.finished = False

        # Setting locked cells from original board
        for yidx, row in enumerate(self.grid):
            for xidx, num in enumerate(row):
                if num != 0:
                    self.lockedCells.append([xidx, yidx])

    def isInt(self, string):
        try:
            int(string)
            return True
        except:
            return False
