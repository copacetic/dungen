from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy

from time import sleep
import random
import sys
import signal

def signalHandler(signal, frame):
  print("SIGINT received")
  sys.exit()

SIZE = 50
SCREEN_WIDTH, SCREEN_HEIGHT = 600.0, 600.0
X_STEP_SIZE = SCREEN_WIDTH / SIZE
Y_STEP_SIZE = SCREEN_HEIGHT / SIZE
DIRECTIONS = [(1,0),(0,1),(-1,0),(0,-1)]

class Tile:
  def __init__(self, occupied=None):
    if occupied != None:
      self.occupied = occupied
    else:
      self.occupied = bool(random.getrandbits(1))

  def setOccupancy(self, occupancy):
    self.occupied = occupancy
    return self

def drawGrid(grid):
    #(0, SCREEN_HEIGHT)  (SCREEN_WIDTH, SCREEN_HEIGHT)
    #|---|
    #|   |
    #|___|
    #(0,0)  (SCREEN_WIDTH,0)
    to_draw = []

    glClear(GL_COLOR_BUFFER_BIT)
    for row in range(len(grid)):
      for column in range(len(grid[row])):
        currTile = grid[row][column]
        if currTile.occupied == True:
          low_x = column * X_STEP_SIZE
          low_y = row * Y_STEP_SIZE
          high_x = low_x + X_STEP_SIZE
          high_y = low_y + Y_STEP_SIZE
          a_square =  [
                        [low_x, low_y],
                        [high_x, low_y],
                        [high_x, high_y],
                        [low_x, low_y],
                        [high_x, high_y],
                        [low_x, high_y]
                      ]
          to_draw.extend(a_square)

    the_vbo = vbo.VBO(numpy.array(to_draw, 'i'))
    the_vbo.bind();
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_INT, 0, the_vbo)
    glDrawArrays(GL_TRIANGLES, 0, len(to_draw))
    glDisableClientState(GL_VERTEX_ARRAY)
    glutSwapBuffers();

def isInboundCoord(x, y):
  return (x >= 0 and x < SIZE) and (y >= 0 and y < SIZE)

def getWalls(grid, cell):
  walls = []
  x, y = cell[0], cell[1]
  for direction in DIRECTIONS:
    newX = x + direction[0]
    newY = y + direction[1]
    if isInboundCoord(newX, newY) and grid[newX][newY].occupied:
      walls.append((newX, newY))
  return walls

def modded_prims():
  if SIZE <= 0:
    print("Error: SIZE is <= 0")

  grid = [[Tile(occupied=True) for _x in range(SIZE)] for _y in range(SIZE)]
  picked = grid[0][0]
  maze = set([(0,0)])
  walls = getWalls(grid, (0,0))
  while len(walls) > 0:
    randWall = random.sample(walls, 1)[0]
    randDirection = random.sample(DIRECTIONS, 1)[0]
    randNeighborX = randWall[0] + randDirection[0]
    randNeighborY = randWall[1] + randDirection[1]

    if isInboundCoord(randNeighborX, randNeighborY) and ((randNeighborX, randNeighborY) not in maze):
      # add both the wall we picked and the wall in the rand direction to the maze
      maze.add(randWall)
      maze.add((randNeighborX, randNeighborY))

      walls.extend(getWalls(grid, (randNeighborX, randNeighborY)))

    # set cells in maze as unoccupied, for rendering later
    for cell in maze:
      grid[cell[0]][cell[1]].setOccupancy(False)
    walls.remove(randWall)
    yield grid

def initSimulation():
  return modded_prims()

def display():
  gen = initSimulation()
  for grid in gen:
    drawGrid(grid)

def initGL():
  print("Initializing opengl...")
  glClearColor(1.0,1.0,1.0,0.0)
  glColor3f(0.0,0.0, 0.0)
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  gluOrtho2D(0.0,int(SCREEN_WIDTH),0.0,(SCREEN_HEIGHT))

def main():
  print("Registering exit signal handler...")
  signal.signal(signal.SIGINT, signalHandler)
  glutInit()
  glutInitWindowSize(int(SCREEN_WIDTH),int(SCREEN_HEIGHT))
  print("Creating window...")
  glutCreateWindow("Copacetic's Dungeon Generator")
  glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
  glutDisplayFunc(display)
  glutIdleFunc(display)
  initGL()
  glutMainLoop()

if __name__ == '__main__':
  main()
