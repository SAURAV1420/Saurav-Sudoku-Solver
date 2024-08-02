import sys
import math
from app_class_solver import *

class Vertice:
    def __init__(self,index,content):
        self.index = index
        self.content = content
        self.neighbors = []
        self.saturationDegree = 0
        self.degree = 0
        

    def calculateSaturation(self):
        for neighbor in self.neighbors:
            if neighbor.getContent() != "N":
                self.saturationDegree += 1

    def getContent(self):
        return self.content

    

    def setContent(self,content):
        self.content = content

    def increaseSaturation(self):
        self.saturationDegree += 1

    def decrementSaturation(self):
        self.saturationDegree += 1

    def getSaturation(self):
        return self.saturationDegree

    def setNeighbor(self,vertice):
        self.neighbors.append(vertice)
        self.degree += 1

    def possibleColors(self,order):
        possibilities = list(range(1,order+1))
        setOfpossibilities = set(possibilities)
        alreadyExist = set()
        for neighbor in self.neighbors:
            if neighbor.getContent() == "N":
                continue
            alreadyExist.add(int(neighbor.getContent()))
        setOfpossibilities = setOfpossibilities - alreadyExist
        if (len(setOfpossibilities) == 0):
            return -1
        return list(setOfpossibilities)

    def increaseSaturationNeighbors(self):
        for neighbor in self.neighbors:
            neighbor.increaseSaturation()

    def decrementSaturationNeighbors(self):
        for neighbor in self.neighbors:
            neighbor.decrementSaturation()


class Graph:
    def __init__(self,cells):
        self.numberOfVertices = len(cells)
        self.order = int(math.sqrt(self.numberOfVertices))
        self.blocDimension = int(math.sqrt(self.order))
        self.vertices = self.buildVertices(cells,self.numberOfVertices)
        self.blocs = self.buildBlocs(self.numberOfVertices,self.blocDimension,self.order)
        self.mergeNeighbors(self.order)
        self.board=[]


    def getBoard(self):
        return self.board
        

    def solver(self,output_file_name):
        if self.dSatur():
            print ("A solution has been found! Check the file",output_file_name)
        else:
            print("Impossible to find a solution")



    def buildVertices(self,cells,numberOfVertices):
        vertices = {}
        for i in range(numberOfVertices):
            vertices[i] = Vertice(i,cells[i])
        return vertices
    
    def buildBlocs(self,numberOfVertices,blocDimension,order):
        blocList = []
        for firstBlocVertical in range (0,numberOfVertices,blocDimension*order):
            for firstBlocHorizontal in range(firstBlocVertical, firstBlocVertical+order, blocDimension):
                bloc = set()
                for vertical in range(firstBlocHorizontal,firstBlocHorizontal + order*blocDimension-1,order):
                    for horizontal in range(vertical,vertical+blocDimension):
                        bloc.add(horizontal)
                blocList.append(bloc)
        return blocList

    def lineNeighbors(self,index,order):
        mod = index % order
        dif = order - mod
        lim = index + dif

        neighbors = set()
        for i in range(index-mod,lim):
            neighbors.add(i)
        return neighbors

    def columnNeighbors(self,index,order):
        neighbors = set()
        for goingUp in range(index,0,-order):
            neighbors.add(goingUp)
        for goindDown in range(index,self.numberOfVertices,order):
            neighbors.add(goindDown)
        return neighbors

    def blocNeighbors(self,index):
        for bloc in self.blocs:
            if index in bloc:
                return bloc

    def mergeNeighbors(self,order):
        for vertice in self.vertices:
            lineNeighbors = self.lineNeighbors(vertice,order)
            columnNeighbors = self.columnNeighbors(vertice,order)
            blocNeighbors = self.blocNeighbors(vertice)
            neighbors = lineNeighbors | columnNeighbors | blocNeighbors
            self.assignNeihbors(vertice,neighbors)

    def assignNeihbors(self,vertice,neighbors):
        for neighbor in neighbors:
            if (vertice != neighbor):
                self.vertices[vertice].setNeighbor(self.vertices[neighbor])
        self.vertices[vertice].calculateSaturation()

    def biggerSaturation(self):
        biggerSaturation = 0
        biggerIndex = 0
        for vertice in self.vertices:
            if self.vertices[vertice].getSaturation() > biggerSaturation and self.vertices[vertice].getContent() == "N":
                biggerSaturation = self.vertices[vertice].getSaturation()
                biggerIndex = vertice
        return biggerIndex  

    def allColorful(self):
        for vertice in self.vertices:
            if self.vertices[vertice].getContent() == "N":
                return False
        return True

    def uncoloredVertices(self):
        uncoloredVertices = set()
        for vertice in self.vertices:
            if (self.vertices[vertice].getContent() == "N"):
                uncoloredVertices.add(vertice)
        return uncoloredVertices



    def dSatur(self):
        if self.allColorful():
            return True
        biggerSaturation = self.biggerSaturation()
        possibleColors = self.vertices[biggerSaturation].possibleColors(self.order)
        if possibleColors == -1:
            return False
        if not possibleColors:
            return False
        for color in possibleColors:
            self.vertices[biggerSaturation].setContent(color)
            self.vertices[biggerSaturation].increaseSaturationNeighbors()
            if self.dSatur():
                return True
            else:
                self.vertices[biggerSaturation].decrementSaturationNeighbors()
                self.vertices[biggerSaturation].setContent("N")
        return False


    def writeFile(self,output_file_name):
        output_file = open(output_file_name, "w+")
        lisst=[]
        for vertices in self.vertices:                
            if(vertices % self.order == 0 and vertices != 0):
                self.board.append(lisst)
                lisst=[]
                print("\n",file=output_file)
            print(self.vertices[vertices].getContent()," ",end="",file=output_file)
            sttr = str(self.vertices[vertices].getContent())
            #print(sttr)
            if(sttr[0] == '\''):
                lisst.append(int(sttr[1]))
            else:
                lisst.append(int(sttr))

        self.board.append(lisst)
        # app_solver = App_Solver()
        # app_solver.run(self.board)
        print(self.board)

#if __name__ == "__main__":
class Solver:

    def solve(self):
        input_file_name = ""
        output_file_name = ""
        if len(sys.argv) == 1:
            input_file_name = "SudokuPuzzle.txt"     #sys.argv[1]
            output_file_name = "Output.txt"          #sys.argv[2]
        else:
            print("Invalid number of arguments. Aborting...")
            sys.exit()
        input_file = open(input_file_name,"r")
        cells = ""
        for line in input_file:
            cells = cells + ((line.replace("\n","").replace(".","N")))
        cells = list(cells)
        graph = Graph(cells)
        graph.solver(output_file_name)
        graph.writeFile(output_file_name)
        return(graph.getBoard())
    

            





