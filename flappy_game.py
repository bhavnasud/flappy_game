import pygame, sys, time
import random
from pygame.locals import *
import copy

# set up the window
WINDOWWIDTH = 400
WINDOWHEIGHT = 400
FLOOR = 300
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Animation')
# set up direction variables
RANDOM_PLAYER = True
LEFT = 11
UP = 1
DOWN = 10
NOTMOVING = 0
MOVESPEED = 4
jumpspeed = 0
score = 0
# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

colors = [BLACK, GREEN, BLUE]
weights = [1, 1, 1, 1]
learning_rate = .01

class State:
	def __init__(self):
		self.obstacles_list = []
		self.x_pos = 0
		self.y_pos = 0
		self.score = 0
		self.jumpspeed = 0
		self.moving_dir = NOTMOVING
		self.num_iters = 0




def isTouching(rect1, rect2):
	return not ((rect1.top + rect1.height < rect2.top) or (rect1.top > rect2.top + rect2.height)
	or rect1.left + rect1.width < rect2.left or rect1.left > rect2.left + rect2.width)


def getFeature(state, action, index):
	if (index == 0):
		num_bottom_left = getNumBottomLeftRectangles(state.obstacles_list)
		if (num_bottom_left > 1 and action == "up" and state.curr['rect'].top > FLOOR - 20):
			# print("first thing")
			return 1
		else:
			return 0
	if (index == 1):
		num_rectangles_touched = 0
		for rectangle in state.obstacles_list:
			if (isTouching(state.curr['rect'], rectangle['rect'])):
				num_rectangles_touched += 1
		return num_rectangles_touched
	if (index == 2):
		next_state = get_next_state(state, action)
		return next_state.score - state.score
	if (index == 3):
		num_rects_right = 0
		#number of squares to your right
		for rectangle in state.obstacles_list:
			if not (rectangle['rect'].top > state.curr['rect'].top + state.curr['rect'].height 
			or rectangle['rect'].top + rectangle['rect'].height < state.curr['rect'].top
			or rectangle['rect'].left + rectangle['rect'].width < state.curr['rect'].left
			or rectangle['rect'].left > state.curr['rect'].left + state.curr['rect'].width + 40):
				num_rects_right += 1
		return num_rects_right

def getNumBottomLeftRectangles(rectangles):
	num_bottom_left = 0
	for rectangle in rectangles:
		if rectangle['rect'].left < WINDOWWIDTH/2 and rectangle['rect'].top > FLOOR - 10:
			num_bottom_left += 1
	return num_bottom_left

def getQValue(state, action):
	return weights[0] * getFeature(state, action, 0) + weights[1] * getFeature(state, action, 1)
	+ weights[2] * getFeature(state, action, 2) + weights[3] * getFeature(state, action, 3)

def updateWeights(state, next_state, action):
	reward = next_state.score - state.score
	next_up = getQValue(next_state, "up")
	next_nothing = getQValue(next_state, "none")
	best_next = max(next_up, next_nothing)
	difference = (reward + .5 * best_next) - getQValue(state, action)
	print("difference is ", difference)
	for i in range(len(weights)):
		weights[i] += learning_rate * difference * getFeature(state, action, i)

# def updateWeights(rectangles, )
# set up pygame
pygame.init()


# set up the block data structure
b1 = {'rect':pygame.Rect(20, FLOOR, 30, 30), 'color':RED, 'dir':NOTMOVING}
# b2 = {'rect':pygame.Rect(200, FLOOR, 20, 20), 'color':GREEN, 'dir':DOWN}
# b3 = {'rect':pygame.Rect(100, 150, 60, 60), 'color':BLUE, 'dir':DOWN}
bad = []
num_iters = 0

myfont = pygame.font.SysFont('Comic Sans MS', 30)

textsurface = myfont.render('Score : 0', True, BLACK)
textRect = textsurface.get_rect()  
# set the center of the rectangular object. 
textRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2) 

state = State()
state.obstacles_list = []
state.score = 0
state.jumpspeed = 0
state.curr = b1
state.num_iters = 0


#calculate the next state with both possible actions


def get_next_state(state, action):
	next_state = copy.deepcopy(state)
	next_state.score += .4
	# if (state.num_iters % 2 == 0):
	# 	print("hello")
	# 	next_state.score += .5
	if (RANDOM_PLAYER):
		if (action == "up"):
			next_state.curr['dir'] = UP
			next_state.jumpspeed = 10
	next_state.num_iters += 1
	next_state.obstacles_list = []
	
	for b in state.obstacles_list:
		if (isTouching(state.curr['rect'], b['rect'])):
			next_state.score -= 2
		b['rect'].left -= MOVESPEED
		if b['rect'].right >= 0:
			next_state.obstacles_list.append(b)
	if next_state.curr['dir'] == DOWN and next_state.curr['rect'].top >= FLOOR:
		next_state.jumpspeed = 0
		next_state.curr['dir'] = NOTMOVING
	elif (next_state.jumpspeed == 0 and next_state.curr['dir'] == UP):
		# print("hello")
		next_state.curr['dir'] = DOWN
	elif next_state.curr['dir'] == UP or next_state.curr['dir'] == DOWN:
		next_state.curr['rect'].top -= next_state.jumpspeed
		if next_state.curr['rect'].top > FLOOR:
			next_state.curr['rect'].top = FLOOR
		if next_state.curr['rect'].top < 0:
			next_state.curr['rect'].top = 0
		next_state.jumpspeed -= 2
	return next_state
# run the game loop
while True:
	next_state_up = get_next_state(state, "up")
	next_state_nothing = get_next_state(state, "none")
	for event in pygame.event.get():
		# if event.type == QUIT:
		# 	pygame.quit()
		# 	sys.exit()
		if event.type == KEYDOWN:
			print("key pressed")
			#do nothing
	#add new rectangle with higher probability if few rectangles
	if ((random.random() < .4 and len(state.obstacles_list) <= 6) or (random.random() < .1)):
		
		color = colors[random.randint(0, 2)]
		x_pos = random.randint(WINDOWWIDTH/2, WINDOWWIDTH - 15)
		width = random.randint(10, 40)
		height = random.randint(10, 40)
		if(random.random() < .33):
			y_pos = FLOOR
		else:
			y_pos = random.randint(10, FLOOR - 10)
		new_rect = {'rect':pygame.Rect(x_pos, y_pos, width, height), 'color':color, 'dir':DOWN}
		next_state_up.obstacles_list.append(new_rect)
		next_state_nothing.obstacles_list.append(new_rect)

	#move randomly with 50 percent chance, or choose optimal action with 50 percent chance
	if (random.random() < .5):
		if (random.random() < .1):
			updateWeights(state, next_state_up, "up")
			state = next_state_up
		else:
			updateWeights(state, next_state_nothing, "none")
			state = next_state_nothing
		# print("moving randomly")
	else:
		if (getQValue(state, "up") > getQValue(state, "none")):
			# print("choosing up")
			updateWeights(state, next_state_up, "up")
			state = next_state_up
		else:
			# print("choosing nothing")
			updateWeights(state, next_state_nothing, "none")
			state = next_state_nothing


	# print("weight 1 ", weights[1])
	print("weight 2 ", weights[2])
	print("weight 3 ", weights[3])
	#update gui
	windowSurface.fill(WHITE)
	textsurface = myfont.render("Score : " + str(state.score), True, BLACK)
	windowSurface.blit(textsurface, textRect) 
	for obstacle in state.obstacles_list:
		pygame.draw.rect(windowSurface, obstacle['color'], obstacle['rect'])
	pygame.draw.rect(windowSurface, state.curr['color'], state.curr['rect'])
	pygame.display.update()


	time.sleep(0.02)

