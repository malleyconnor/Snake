# Importing any necessary libraries
import pygame
import time
import random
from enum import IntEnum

# Defining some colors used in the game
blue_tint = 20
green_tint= 40
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
dark_red = pygame.Color(127, 0, 0)
medium_red = pygame.Color(200, 10, 10)
red = pygame.Color(255, 0, 0)
light_red = pygame.Color(255, 127, 127)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
dark_gray = pygame.Color(63, 63, 63+blue_tint)
gray = pygame.Color(127, 127, 127+blue_tint)
medium_gray = pygame.Color(160, 160, 160+blue_tint)
light_gray = pygame.Color(191, 191, 191+blue_tint)
dark_green = pygame.Color(63, 63+green_tint, 63)
green = pygame.Color(127,127+green_tint,127)
medium_green = pygame.Color(160,160+green_tint,160)
light_green = pygame.Color(127,127+3*green_tint,127)

# This gives a numeric value to each direction
class Direction(IntEnum):
	UP    = 0
	RIGHT = 1
	DOWN  = 2
	LEFT  = 3

# This keeps track of the game state (start screen, playing, game over screen)
class GameState(IntEnum):
    START = 0
    PLAYING = 1
    END = 2

# The main class for the Snake Game
class SnakeGame:
    RES_X = 720 # X Resolution
    RES_Y = 480 # Y Resolution
    GRID_SIZE = 30 # Size of the grid squares
    BACKGROUND_COLOR = dark_gray # Background color
    TARGET_FPS = 5 # Frames per second for the game to render at
    TARGET_SPF = 1/TARGET_FPS # Seconds per frame

    # This will initalize all the parameters in the Snake Game
    def __init__(self):
        # initial score
        self.score = 0

        # Initialising pygame
        pygame.init()

        # Initialise game window
        pygame.display.set_caption('Snake Game')
        self.game_window = pygame.display.set_mode((self.RES_X, self.RES_Y))
        
        # FPS (frames per second) controller
        self.clock = pygame.time.Clock()
		
        # Position of the fruit (eating this makes the snake grow)
        self.fruit = self.Fruit()

        # This is our snake object
        self.snake = self.Snake(speed=self.GRID_SIZE)
        
        # Queue of events (arrow key presses)
        self.event_queue = []

        # Sound mixer
        pygame.mixer.init()
        self.fruit_sound = pygame.mixer.Sound('boom.mp3')
        self.last_move = -1
        self.game_state = GameState.START

    class Snake:
        def __init__(self, speed):
            # Speef of snake
            self.speed = speed

            self.body = [[SnakeGame.GRID_SIZE*10,  SnakeGame.GRID_SIZE*5],
                         [SnakeGame.GRID_SIZE*9,   SnakeGame.GRID_SIZE*5],
                         [SnakeGame.GRID_SIZE*8,   SnakeGame.GRID_SIZE*5],
                         [SnakeGame.GRID_SIZE*7,   SnakeGame.GRID_SIZE*5]]
			
            # Position of the head
            self.position = [SnakeGame.GRID_SIZE*10,  SnakeGame.GRID_SIZE*5]
			
            # Start facing right
            self.direction = Direction.RIGHT

        # Change the snakes direction
        def change_direction(self, direction):
            """
            Changes the snakes direction.

            Input:
                direction (Direction object) - Which direction to change to

            Returns:
                None
            """
            if direction == Direction.UP and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif direction == Direction.DOWN and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif direction== Direction.LEFT and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif direction == Direction.RIGHT and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT

        def update_position(self):
            """
            Updates the position of the snakes head (self.position) based on it's current direction.
            """
            # Updates the position of the snakes head
            if self.direction == Direction.UP:
                self.position[1] -= SnakeGame.GRID_SIZE
            if self.direction == Direction.DOWN:
                self.position[1] += SnakeGame.GRID_SIZE
            if self.direction == Direction.LEFT:
                self.position[0] -= SnakeGame.GRID_SIZE
            if self.direction == Direction.RIGHT:
                self.position[0] += SnakeGame.GRID_SIZE

        def extend_head(self):
            """
            Extends the snakes body by adding self.position to the beginning of the queue.
            """
            # Move the snake forward using the queue
            self.body.insert(0, list(self.position))

        def remove_tail(self):
            """
            Removes the snakes tail. This will only be triggered if we are not colliding with a fruit.
            """
            self.body.pop()

    class Fruit:
        def __init__(self):
            # Position of the fruit
            self.position = [random.randint(0, (SnakeGame.RES_X//SnakeGame.GRID_SIZE)-1) * (SnakeGame.GRID_SIZE), 
                             random.randint(0, (SnakeGame.RES_Y//SnakeGame.GRID_SIZE)-1) * (SnakeGame.GRID_SIZE)]
            self.is_spawned = True

    def is_game_over(self):
        """
        Returns true if the position of the snake should trigger the game to be over.
        (e.g. If the snake is out of bounds or its head is colliding with its body)
        """
        # Game Over conditions
        if self.snake.position[0] < 0 or self.snake.position[0] > self.RES_X-self.GRID_SIZE:
            return True
        if self.snake.position[1] < 0 or self.snake.position[1] > self.RES_Y-self.GRID_SIZE:
            return True

        # Touching the snake body
        for block in self.snake.body[1:]:
            if self.snake.position[0] == block[0] and self.snake.position[1] == block[1]:
                return True

    def spawn_fruit(self):
        """
        Updates then position of the fruit to a random position, and sets the fruit.is_spawned flag to True
        """
        self.fruit.position = [
            random.randint(0, (self.RES_X//self.GRID_SIZE)-1) * (self.GRID_SIZE),
            random.randint(0, (self.RES_Y//self.GRID_SIZE)-1) * (self.GRID_SIZE)
        ]
        self.fruit.is_spawned = True

    def collision_with_fruit(self):
        """
        Checks if the snakes head is currently colliding with the fruit.

        Returns:
            True if snakes head matches the position of the fruit, else False
        """
        # Collision with fruit
        if self.snake.position[0] == self.fruit.position[0] and \
            self.snake.position[1] == self.fruit.position[1]:
            return True
        else:
            return False

    # Function to display the start screen
    def draw_start_screen(self):
        self.game_window.fill(self.BACKGROUND_COLOR)
        my_font = pygame.font.SysFont('times new roman', 50)

        # Create a "Start" button
        start_button = my_font.render("Hit Enter to Start", True, white)
        start_button_rect = start_button.get_rect()
        start_button_rect.center = (self.RES_X // 2, self.RES_Y // 2)

        self.game_window.blit(start_button, start_button_rect)

        pygame.display.update()

        # Check for mouse click to start the game
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_state = GameState.PLAYING

    # displaying Score function
    def show_score(self):
        choice = 1 
        color = white 
        font = 'times new roman' 
        size = 20
        # creating font object score_font
        score_font = pygame.font.SysFont(font, size)
        
        # create the display surface object 
        # score_surface
        score_surface = score_font.render('Score : ' + str(self.score), True, color)
        
        # create a rectangular object for the text
        # surface object
        score_rect = score_surface.get_rect()
        
        # displaying text
        self.game_window.blit(score_surface, score_rect)
			 
    # Display the game over screen
    def draw_game_over(self):
        self.game_window.fill(self.BACKGROUND_COLOR)
        # creating font object my_font
        my_font = pygame.font.SysFont('times new roman', 50)
        
        # creating a text surface on which text 
        # will be drawn
        game_over_surface = my_font.render(
            'Your Score is : ' + str(self.score), True, red)
        
        # create a rectangular object for the text 
        # surface object
        game_over_rect = game_over_surface.get_rect()
        
        # setting position of the text
        game_over_rect.midtop = (self.RES_X/2, self.RES_Y/4)
        
        # blit will draw the text on screen
        self.game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        
        # after 2 seconds we will quit the program
        time.sleep(2)
        
        # deactivating pygame library
        pygame.quit()
        
        # quit the program
        quit()

    # Draws the background on the screen
    def draw_background(self):
        self.game_window.fill(self.BACKGROUND_COLOR)
        for x in range(0, self.RES_X, self.GRID_SIZE):
            for y in range(0, self.RES_Y, self.GRID_SIZE):
                pygame.draw.rect(self.game_window, dark_gray, (x, y, self.GRID_SIZE, self.GRID_SIZE))
                pygame.draw.rect(self.game_window, gray, (x+1, y+1, self.GRID_SIZE-2, self.GRID_SIZE-2))
                pygame.draw.rect(self.game_window, medium_gray, (x+3, y+3, self.GRID_SIZE-6, self.GRID_SIZE-6))
                pygame.draw.rect(self.game_window, light_gray, (x+4, y+4, self.GRID_SIZE-8, self.GRID_SIZE-8))

    # Draws the snake on the screen
    def draw_snake(self):
        for pos in self.snake.body:
            pygame.draw.rect(self.game_window, light_green, pygame.Rect(pos[0]+1, pos[1]+1, self.GRID_SIZE-2, self.GRID_SIZE-2))
            pygame.draw.rect(self.game_window, medium_green, pygame.Rect(pos[0]+2, pos[1]+2, self.GRID_SIZE-4, self.GRID_SIZE-4))
            pygame.draw.rect(self.game_window, green, pygame.Rect(pos[0]+3, pos[1]+3, self.GRID_SIZE-6, self.GRID_SIZE-6))
            pygame.draw.rect(self.game_window, dark_green, pygame.Rect(pos[0]+4, pos[1]+4, self.GRID_SIZE-8, self.GRID_SIZE-8))

    # Draws the fruit on the screen
    def draw_fruit(self):
        pygame.draw.rect(self.game_window, light_red, pygame.Rect(self.fruit.position[0], self.fruit.position[1], self.GRID_SIZE, self.GRID_SIZE))
        pygame.draw.rect(self.game_window, red, pygame.Rect(self.fruit.position[0]+1, self.fruit.position[1]+1, self.GRID_SIZE-2, self.GRID_SIZE-2))
        pygame.draw.rect(self.game_window, medium_red, pygame.Rect(self.fruit.position[0]+3, self.fruit.position[1]+3, self.GRID_SIZE-6, self.GRID_SIZE-6))
        pygame.draw.rect(self.game_window, dark_red, pygame.Rect(self.fruit.position[0]+4, self.fruit.position[1]+4, self.GRID_SIZE-8, self.GRID_SIZE-8))


    # Processes pygame events and key presses
    def get_events(self):
        # handling key events
        # Queues the events into self.event_queue
        # The latest event can be retrieved with self.event_queue.pop(len(self.event_queue)-1)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = Direction.UP
                    self.event_queue.append(change_to)
                elif event.key == pygame.K_DOWN:
                    change_to = Direction.DOWN
                    self.event_queue.append(change_to)
                elif event.key == pygame.K_LEFT:
                    change_to = Direction.LEFT
                    self.event_queue.append(change_to)
                elif event.key == pygame.K_RIGHT:
                    change_to = Direction.RIGHT
                    self.event_queue.append(change_to)
                self.event_queue.append(change_to)

    # Gets the latest key press (if any)
    def get_latest_event(self):
        # If there is a valid event in the queue, set the new direction
        if len(self.event_queue) > 0:
            change_to = self.event_queue.pop(len(self.event_queue)-1)
        # Otherwise keep the same direction
        else:
            change_to = self.snake.direction

        # We processed the latest event, we can empty the queue
        self.event_queue = []
        return change_to


    # Main Function
    def play(self):
        while True:
            if not (self.game_state == GameState.PLAYING):
                self.draw_start_screen()
                continue

            # Queue up any events
            self.get_events()

            # Ensures we're updating the frame at 10 FPS (the inputs will be processed at a much higher rate)
            if time.perf_counter() - self.last_move > self.TARGET_SPF:
                self.last_move = time.perf_counter()

                # Get latest key press (UP, DOWN, LEFT, or RIGHT)
                direction = self.get_latest_event()

                # Update the snakes direction
                self.snake.change_direction(direction)

                # Update the snakes position based on it's current direciton
                self.snake.update_position()

                # Extend the snakes head, we will remove from the tail
                # if we end up colliding with a fruit
                self.snake.extend_head()


                # If we collide with the fruit, update the game score, despawn the fruit
                # and play some sounds. Otherwise, we will remove from the tail to keep the
                # size of the snake the same.
                if self.collision_with_fruit():
                   self.score += 10
                   self.fruit.is_spawned = False
                   self.fruit_sound.play()
                else:
                    self.snake.remove_tail()

                # If the fruit has been de-spawned, spawn a new one. 
                if not self.fruit.is_spawned:
                    self.spawn_fruit()

                # Draw the background, the snake, and the fruit
                self.draw_background()
                self.draw_snake()
                self.draw_fruit()

                # Check if we've reached a game over condition
                if self.is_game_over():
                    self.game_state = GameState.END
                    self.draw_game_over()

                # Display the current score
                self.show_score()

                # Refresh game screen
                pygame.display.update()

            # Frame Per Second /Refresh Rate
            self.clock.tick(100)


game = SnakeGame()
game.play()