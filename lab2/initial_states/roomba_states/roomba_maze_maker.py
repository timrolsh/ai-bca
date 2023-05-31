from random import choice
from sys import argv
from copy import deepcopy

FLOOR = '.'
WALL = '#'

def makeGrid(r,c):
	grid = []
	for i in range(r):
		grid.append([FLOOR for j in range(c)])
	return grid

def getRandCoord(r, c):
	return choice(range(r)), choice(range(c))

def getRandWallCoords(r,c,l, horiz = None):
	horiz = choice((True, False)) if horiz == None else horiz
	dr, dc = (0, 1) if horiz else (1,0)

	coords = [getRandCoord(r if horiz else r - l,c - l if horiz else c)]
	while len(coords) < l:
		coords.append((coords[-1][0] +  dr, coords[-1][1] +  dc))
	return coords

def makeWalls(grid, coords):
	for i, j in coords:
		grid[i][j] = WALL

def createWallSymmetry(grid, r, c, hor_sym, ver_sym, rot_sym):
	for i in range(r):
		for j in range(c):
			if hor_sym:
				if grid[i][j] == WALL or grid[i][c-j-1] == WALL :
					grid[i][j] = WALL
					grid[i][c-j-1] = WALL 
			if ver_sym:
				if grid[i][j] == WALL or grid[r-i-1][j] == WALL :
					grid[i][j] = WALL
					grid[r-i-1][j] = WALL 
			if rot_sym:
				if grid[i][j] == WALL or grid[r-i-1][c-j-1] == WALL :
					grid[i][j] = WALL
					grid[r-i-1][c-j-1] = WALL 

## Tweak params for grid 

WIDTH = 12
HEIGHT = 10
WALL_LENS = [1,2,3,4]
NUM_WALLS = [0,3,0,1]
VER_SYM = False
HOR_SYM = True
ROT_SYM = False
START_POS_1 = [0,0]
START_POS_2 = [HEIGHT - START_POS_1[0] - 1,WIDTH - START_POS_1[1] - 1]

assert len(WALL_LENS) == len(NUM_WALLS)

grid = makeGrid(HEIGHT, WIDTH)
coords= []
for l, num in zip(WALL_LENS, NUM_WALLS):
	for i in range(num):
		coords += getRandWallCoords(HEIGHT, WIDTH, l)

makeWalls(grid,coords)
createWallSymmetry(grid, HEIGHT, WIDTH, HOR_SYM, VER_SYM, ROT_SYM)

grid[START_POS_1[0]][START_POS_1[1]] = FLOOR
grid[START_POS_2[0]][START_POS_2[1]] = FLOOR

print("{} {}".format(HEIGHT, WIDTH))
print("{} {}".format(START_POS_1[0], START_POS_1[1]))
print("{} {}".format(START_POS_2[0], START_POS_2[1]))

for i in range(HEIGHT):
	for j in range(WIDTH):
		print(grid[i][j], end="")
	print("\n", end = "")