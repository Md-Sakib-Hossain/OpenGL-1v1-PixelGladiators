from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time


# Global constants
WINDOW_X = 800
WINDOW_Y = 600

bullet_radius = 2


PLAYER_WIDTH = 35  # Width of the player's body

# Player and enemy health
player_health = 100
enemy_health = 100

# Global variables
player_position = WINDOW_X // 4
enemy_position = WINDOW_X - 200

orientation = "right"
enemy_orientation = "left"

# Player state
player_y = 80                    # Initial Y position (ground level)
player_velocity_x = 0            # Horizontal velocity
player_velocity_y = 0            # Vertical velocity
is_jumping = False               # Whether the player is currently jumping
is_falling_after_bounce = False  # Track if the player is falling after bouncing off a wall
player_shoot_cooldown = 0        # Cooldown for player's bullet firing
player_shoot_delay = 20          # Delay between shots (in frames)

# Enemy state
enemy_velocity_x = 0
enemy_y = 80
enemy_velocity_y = 0
enemy_is_jumping = False
enemy_shoot_cooldown = 0    # Cooldown for shooting
enemy_jump_cooldown = 0     # Cooldown between jumps
dodge_range = 100           # Range within which the enemy will dodge bullets
dodge_speed = 5             # Speed at which the enemy dodges


bullets = []
gamePaused = False
gameOver = False

collision_force = 100   # Force applied to move the player and enemy apart
collision_cooldown = 0  # Cooldown to prevent repeated collisions

blink_state = True  # Toggle for blink effect
blink_timer = 0     # Timer for blink effect
game_over_blink = False

sparks = []  # List to store active sparks (each spark is a dictionary with x, y, and lifetime)

# Star
star_speed = 2
star_size = 14
num_stars = 4

# Global variables for falling stars
star_positions = []                     # List of tuples containing the positions (x, y)
last_star_creation_time = time.time()
star_creation_delay = 3


# Key states
key_states = {
    b'w': False,
    b'a': False,
    b'd': False
}


def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) > abs(dy):           # For zone 0, 3, 4 or 7
        if dx > 0 and dy > 0:
            return 0
        elif dx < 0 and dy > 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7
    else:                           # For zone 1, 2, 5 or 6
        if dx > 0 and dy > 0:
            return 1
        elif dx < 0 and dy > 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6


def convert_to_zone0(x, y, zone):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return -y, x
    if zone == 7:
        return x, -y


def convert_to_original_zone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y

def draw_points(x, y):
    glPointSize(3)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def MidpointLine(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

    zone = find_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(x1, y1, zone)
    x2, y2 = convert_to_zone0(x2, y2, zone)

    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    d_NE = 2 * dy - 2 * dx
    d_E = 2 * dy

    for i in range(x1, x2):
        x, y = convert_to_original_zone(x1, y1, zone)
        if d >= 0:
            d = d + d_NE
            draw_points(x, y)
            x1 += 1
            y1 += 1
        else:
            d = d + d_E
            draw_points(x, y)
            x1 += 1


# Process for applying Midpoint Circle Algorithm
def draw_circle_points(x, y, cx, cy):
    glPointSize(3)
    glBegin(GL_POINTS)
    glVertex2f(x + cx, y + cy)
    glEnd()

def circlePoints(x, y, cx, cy):
    draw_circle_points(x, y, cx, cy)
    draw_circle_points(y, x, cx, cy)
    draw_circle_points(-y, x, cx, cy)
    draw_circle_points(-x, y, cx, cy)
    draw_circle_points(-x, -y, cx, cy)
    draw_circle_points(-y, -x, cx, cy)
    draw_circle_points(y, -x, cx, cy)
    draw_circle_points(x, -y, cx, cy)


def MidpointCircle(r, cx, cy):
    d = 1 - r
    x = 0
    y = r
    circlePoints(x, y, cx, cy)

    while x < y:
        if d < 0:
            d = d + 2 * x + 3
            x += 1
        else:
            d = d + 2 * (x - y) + 5
            x += 1
            y -= 1
        circlePoints(x, y, cx, cy)

def draw_player_right(x, y):
    # Neck to Hip (point 9 to 1)
    glColor3f(0.0, 0.8, 1.0)
    # glColor3f(1, 1, 1)
    MidpointLine(x+5, y+10, x, y-35)

    # Right Leg
    # Hip to Right Knee (point 1 to point 7)
    MidpointLine(x, y-35, x+10, y-55)

    # Right Knee to Right Ankle (point 7 to point 5)
    MidpointLine(x+10, y-55, x+10, y-70)

    # Right Ankle to Right Foot (point 5 to point 6)
    MidpointLine(x+10, y-70, x+15, y-70)

    # Left Leg
    # Hip to Left Knee (point 1 to point 2)
    MidpointLine(x, y-35, x+2, y-60)

    # Left Knee to Left Ankle (point 2 to point 3)
    MidpointLine(x+2, y-60, x-5, y-70)

    # Left Ankle to Left Foot (point 3 to point 4)
    MidpointLine(x-5, y-70, x, y-70)

    # Right Arm
    # Neck to Right Elbow (point 9 to point 12)
    MidpointLine(x+5, y+10, x+15, y-5)

    # Right Elbow to Right Wrist (point 12 to point 13)
    MidpointLine(x+15, y-5, x+20, y)


    # Left Arm
    # Neck to Left Elbow (point 9 to point 10)
    MidpointLine(x+5, y+10, x+10, y)

    # Left Elbow to Left Wrist (point 10 to point 11)
    MidpointLine(x+10, y, x+20, y+5)

    # Head of player
    MidpointCircle(7, x+5, y+20)

    # Gun barrel
    glColor3f(0.5, 0.5, 0.5)
    MidpointLine(x+20, y+2, x+35, y+2)  
    # Gun handle
    glColor3f(0.5, 0.5, 0.5)
    MidpointLine(x+20, y+2, x+20, y-3)


def draw_player_left(x, y):

    # Neck to Hip (point 9 to 1)
    glColor3f(0.0, 0.8, 1.0)
    # glColor3f(1, 1, 1)
    MidpointLine(x-5, y+10, x, y-35)

    # Left Leg
    # Hip to Left Knee (point 1 to point 7)
    MidpointLine(x, y-35, x-10, y-55)

    # Left Knee to Left Ankle (point 7 to point 5)
    MidpointLine(x-10, y-55, x-10, y-70)

    # Left Ankle to Left Foot (point 5 to point 6)
    MidpointLine(x-15, y-70, x-10, y-70)

    # Right Leg
    # Hip to Right Knee (point 1 to point 2)
    MidpointLine(x, y-35, x-2, y-60)

    # Right Knee to Right Ankle (point 2 to point 3)
    MidpointLine(x-2, y-60, x+5, y-70)

    # Right Ankle to Right Foot (point 3 to point 4)
    MidpointLine(x, y-70, x+5, y-70)

    # Left Arm
    # Neck to Left Elbow (point 9 to point 12)
    MidpointLine(x-5, y+10, x-15, y-5)

    # Left Elbow to Left Wrist (point 12 to point 13)
    MidpointLine(x-15, y-5, x-20, y)

    # Right Arm
    # Neck to Right Elbow (point 9 to point 10)
    MidpointLine(x-5, y+10, x-10, y)

    # Right Elbow to Right Wrist (point 10 to point 11)
    MidpointLine(x-10, y, x-20, y+5)

    # Draw head of player
    MidpointCircle(7, x-5, y+20)

    # Gun barrel
    glColor3f(0.5, 0.5, 0.5)
    MidpointLine(x-35, y+3,x-20, y+3)
    # Gun handle
    glColor3f(0.5, 0.5, 0.5)
    MidpointLine(x-20, y+2,x-20, y-3)

def draw_enemy_left(x, y):
    # Draw the enemy stickman facing left
    glColor3f(1.0, 0.5, 0.0)  # Orange color

    # Neck to Hip (point 9 to 1)
    MidpointLine(x - 5, y + 10, x, y - 35)

    # Left Leg
    # Hip to Left Knee (point 1 to point 7)
    MidpointLine(x, y - 35, x - 10, y - 55)

    # Left Knee to Left Ankle (point 7 to point 5)
    MidpointLine(x - 10, y - 55, x - 10, y - 70)

    # Left Ankle to Left Foot (point 5 to point 6)
    MidpointLine(x - 15, y - 70, x - 10, y - 70)

    # Right Leg
    # Hip to Right Knee (point 1 to point 2)
    MidpointLine(x, y - 35, x - 2, y - 60)

    # Right Knee to Right Ankle (point 2 to point 3)
    MidpointLine(x - 2, y - 60, x + 5, y - 70)

    # Right Ankle to Right Foot (point 3 to point 4)
    MidpointLine(x, y - 70, x + 5, y - 70)

    # Left Arm
    # Neck to Left Elbow (point 9 to point 12)
    MidpointLine(x - 5, y + 10, x - 15, y - 5)

    # Left Elbow to Left Wrist (point 12 to point 13)
    MidpointLine(x - 15, y - 5, x - 20, y)

    # Right Arm
    # Neck to Right Elbow (point 9 to point 10)
    MidpointLine(x - 5, y + 10, x - 10, y)

    # Right Elbow to Right Wrist (point 10 to point 11)
    MidpointLine(x - 10, y, x - 20, y + 5)

    # Draw head of player
    MidpointCircle(7, x - 5, y + 20)

    # Gun barrel
    glColor3f(0.5, 0.5, 0.5)  
    MidpointLine(x-35, y+3,x-20, y+3)
    # Gun handle
    glColor3f(0.5, 0.5, 0.5) 
    MidpointLine(x-20, y+2,x-20, y-3)


def draw_enemy_right(x, y):
    # Draw the enemy stickman facing right
    # Neck to Hip (point 9 to 1)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+5, y+10, x, y-35)

    # Right Leg
    # Hip to Right Knee (point 1 to point 7)
    glColor3f(1, 0.5, 0)
    MidpointLine(x, y-35, x+10, y-55)

    # Right Knee to Right Ankle (point 7 to point 5)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+10, y-55, x+10, y-70)

    # Right Ankle to Right Foot (point 5 to point 6)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+10, y-70, x+15, y-70)

    # Left Leg
    # Hip to Left Knee (point 1 to point 2)
    glColor3f(1, 0.5, 0)
    MidpointLine(x, y-35, x+2, y-60)

    # Left Knee to Left Ankle (point 2 to point 3)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+2, y-60, x-5, y-70)

    # Left Ankle to Left Foot (point 3 to point 4)
    glColor3f(1, 0.5, 0)
    MidpointLine(x-5, y-70, x, y-70)

    # Right Arm
    # Neck to Right Elbow (point 9 to point 12)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+5, y+10, x+15, y-5)

    # Right Elbow to Right Wrist (point 12 to point 13)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+15, y-5, x+20, y)

    # Left Arm
    # Neck to Left Elbow (point 9 to point 10)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+5, y+10, x+10, y)

    # Left Elbow to Left Wrist (point 10 to point 11)
    glColor3f(1, 0.5, 0)
    MidpointLine(x+10, y, x+20, y+5)

    # Head of player
    glColor3f(1, 0.5, 0)
    MidpointCircle(7, x+5, y+20)
        # Gun barrel
    glColor3f(0.5, 0.5, 0.5) 
    MidpointLine(x+20, y+2, x+35, y+2)  
    # Gun handle
    glColor3f(0.5, 0.5, 0.5)  
    MidpointLine(x+20, y+2, x+20, y-3) 
    

def draw_arrow():
    glColor3f(0.0, 1.0, 0.0)
    MidpointLine(20, 560, 80, 560)
    MidpointLine(20, 560, 40, 580)
    MidpointLine(20, 560, 40, 540)


def draw_cross():
    glColor3f(1.0, 0.0, 0.0)
    MidpointLine(730, 540, 770, 580) #aa
    MidpointLine(730, 580, 770, 540)


def draw_pause_button():
    glColor3f(1.0, 0.75, 0.0)
    MidpointLine(380, 575, 380, 525)
    MidpointLine(410, 575, 410, 525)


def draw_play_button():
    glColor3f(1.0, 0.75, 0.0)
    MidpointLine(380, 575, 420, 550)
    MidpointLine(380, 575, 380, 525)
    MidpointLine(380, 525, 420, 550)

######draw stars part#########
def initialize_stars():
    """Initialize positions of falling stars."""
    global star_positions
    star_positions = []
    for i in range(num_stars):
        x = random.randint(star_size, WINDOW_X - star_size)
        y = WINDOW_Y + i * 100
        star_positions.append((x, y))

def draw_star(center_x, center_y, size=14):
    # glColor3f(0.8, 0.0, 1.0)
    glColor3f(0.8, 1.0, 1.0)

    # Calculate the angles and the points for the five-pointed star
    points = []
    for i in range(5):
        angle = i * 2 * math.pi / 5  # Angle for each point
        x = center_x + size * math.sin(angle)  # X-coordinate for each point
        y = center_y + size * math.cos(angle)  # Y-coordinate for each point
        points.append((x, y))

    # Draw lines between the points to form the star shape
    for i in range(len(points)):
        next_point = points[(i + 2) % len(points)]  # Skipping one point to form the star
        MidpointLine(points[i][0], points[i][1], next_point[0], next_point[1])

def draw_stars():
    glColor3f(0.8, 1.0, 1.0)  # Star color
    for x, y in star_positions:
        draw_star(x, y, star_size)

max_stars = 4  # Set the maximum number of stars allowed in a frame
def create_new_star():
    """Create a new star at a random position if the maximum limit is not reached."""
    global star_positions, last_star_creation_time
    if len(star_positions) >= max_stars:
        return  # Don't create new stars if the maximum limit is reached

    current_time = time.time()
    if current_time - last_star_creation_time >= star_creation_delay:
        last_star_creation_time = current_time
        x = random.randint(star_size, WINDOW_X - star_size)
        y = WINDOW_Y + star_size
        while any(((x - star[0]) ** 2 + (y - star[1]) ** 2) ** 0.5 <= 2 * star_size for star in star_positions):
            y += 2 * star_size
        star_positions.append((x, y))


def update_stars():
    global star_positions, player_health, player_position, player_y, sparks

    for i in range(len(star_positions) - 1, -1, -1):
        x, y = star_positions[i]
        star_positions[i] = (x, y - star_speed)  # Move the star down

        # # Check collision with the player
        # if (player_position - PLAYER_WIDTH // 2 <= x <= player_position + PLAYER_WIDTH // 2 and
        #         player_y <= y <= player_y + 70):  # Adjust 70 for player's height
        #     player_health = max(player_health - 5, 0)  # Reduce player's health
        #     print(f"Player hit by star! Health: {player_health}")
        #     star_positions.pop(i)  # Remove the star

        # Check collision with the player
        player_left = player_position - PLAYER_WIDTH // 2
        player_right = player_position + PLAYER_WIDTH // 2
        player_top = player_y + 40                          # Adjust for player's height
        player_bottom = player_y

        star_left = x - star_size
        star_right = x + star_size
        star_top = y + star_size
        star_bottom = y - star_size

        # AABB collision detection
        if (player_left <= star_right and player_right >= star_left and
                player_bottom <= star_top and player_top >= star_bottom):
            player_health = max(player_health - 5, 0)  # Reduce player's health
            print(f"Player hit by star! Health: {player_health}")
            # Add light blue spark effect
            sparks.append({'x': x, 'y': y, 'lifetime': 10, 'color': (0.0, 0.5, 1.0)})  # Light blue color
            star_positions.pop(i)  # Remove the star

        # Remove stars that fall off the screen
        elif y < -star_size:
            star_positions.pop(i)

######END OF DRAWING STARS##############################


def handle_player_mov(key):
    global player_position, orientation, player_y, player_velocity_y, player_velocity_x, is_jumping

    if not is_jumping:      # Only allow movement if not already jumping
        if orientation == "right":  # When facing right
            if key == b'd' and player_position <= 750:
                player_position += 10  # Move right
            elif key == b'a':
                orientation = "left"  # Flip to face left

        elif orientation == "left":  # When facing left
            if key == b'a' and player_position >= 50:
                player_position -= 10  # Move left
            elif key == b'd':
                orientation = "right"  # Flip to face right

    # Jump (W)
    if key == b'w' and not is_jumping:
        player_velocity_y = 15  # Set initial upward velocity
        is_jumping = True

    # Right Arc (W+D)
    if key == b'd':
        if is_jumping:
            player_velocity_x = 2  # Move right while jumping
        else:
            player_position += 30  # Move right on the ground
        orientation = "right"  # Face right

    # Left Arc (W+A)
    if key == b'a':
        if is_jumping:
            player_velocity_x = -2  # Move left while jumping
        else:
            player_position -= 30  # Move left on the ground
        orientation = "left"  # Face left

def enemy_ai():
    global enemy_position, enemy_orientation, enemy_is_jumping, bullets
    global enemy_y, enemy_velocity_y, enemy_velocity_x
    global enemy_shoot_cooldown, enemy_jump_cooldown

    # Face the player
    if player_position < enemy_position:
        enemy_orientation = "left"
    else:
        enemy_orientation = "right"

    # Check for nearby bullets and dodge by jumping
    dx, dy = check_nearby_bullets()
    if dx is not None and dy is not None and not enemy_is_jumping and enemy_jump_cooldown <= 0:
        # Dodge by jumping
        enemy_velocity_y = 15  # Set initial upward velocity
        enemy_is_jumping = True
        enemy_jump_cooldown = 180  # 4 second cooldown (240 frames)

        # Set horizontal velocity for arc movement based on bullet direction
        if dx > 0:  # Bullet is coming from the right
            enemy_velocity_x = -2  # Jump left arc
        else:  # Bullet is coming from the left
            enemy_velocity_x = 2  # Jump right arc

        print("Enemy dodged a bullet!")

    # Random movement
    if random.randint(0, 100) < 10:  # 10% chance to move
        if enemy_orientation == "left" and enemy_position > 0:
            enemy_position -= 5  # Move left
        elif enemy_orientation == "right" and enemy_position < WINDOW_X:
            enemy_position += 5  # Move right

    # Random jump with arcs
    if enemy_jump_cooldown <= 0 and random.randint(0, 100) < 2 and not enemy_is_jumping:  # 2% chance to jump
        enemy_velocity_y = 15
        enemy_is_jumping = True
        enemy_jump_cooldown = 240  # 4 second cooldown (240 frames)

        # Set horizontal velocity for arc movement
        if enemy_orientation == "left":
            enemy_velocity_x = -2  # Move left while jumping
        else:
            enemy_velocity_x = 2  # Move right while jumping

        # Ensure enemy stays within screen boundaries
        if enemy_position + enemy_velocity_x < 0:  # Left boundary
            enemy_velocity_x = 2  # Force jump to the right
        elif enemy_position + enemy_velocity_x > WINDOW_X:  # Right boundary
            enemy_velocity_x = -2  # Force jump to the left

    # Apply gravity to enemy
    GRAVITY = 0.5
    if enemy_is_jumping:
        enemy_velocity_y -= GRAVITY
        enemy_y += enemy_velocity_y  # Update vertical position
        enemy_position += enemy_velocity_x

        enemy_position = max(0, min(enemy_position, WINDOW_X))

        # Check if enemy has landed
        if enemy_y <= 80:
            enemy_y = 80
            enemy_velocity_y = 0
            enemy_velocity_x = 0
            enemy_is_jumping = False
            # print("Enemy landed")

    # Reduce cooldown
    if enemy_jump_cooldown > 0:
        enemy_jump_cooldown -= 1

    # Shoot bullets at the player with a cooldown
    if enemy_shoot_cooldown <= 0:
        # Calculate direction to player with random vertical offset
        target_y = player_y + random.randint(-30, 30)  # Random vertical offset
        # Calculate direction to player
        dx = player_position - enemy_position
        dy = target_y - enemy_y
        magnitude = (dx ** 2 + dy ** 2) ** 0.5
        if magnitude == 0:
            return  # Avoid division by zero

        dx /= magnitude
        dy /= magnitude

        # Set bullet velocity based on direction
        bullet_speed = 5
        velocity_x = dx * bullet_speed
        velocity_y = dy * bullet_speed

        # Spawn bullet from the enemy's hand position
        bullet_x = enemy_position - 30 if enemy_orientation == "left" else enemy_position + 10 # Adjust for hand position
        bullet_y = enemy_y   # Adjust for hand position

        # Add bullet to the list
        bullets.append({'x': bullet_x, 'y': bullet_y, 'velocity_x': velocity_x, 'velocity_y': velocity_y})

        # Reset cooldown
        enemy_shoot_cooldown = 60  # 1 second cooldown (60 frames)
    else:
        enemy_shoot_cooldown -= 1


def check_nearby_bullets():
    global bullets, enemy_position, enemy_y

    for bullet in bullets:
        # Calculate distance between bullet and enemy
        dx = bullet['x'] - enemy_position
        dy = bullet['y'] - enemy_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # If bullet is within dodge range, return its direction
        if distance <= dodge_range:
            return dx, dy

    return None, None  # No nearby bullets

def show_sparks():
    global sparks

    for spark in sparks[:]:  # Iterate over a copy of the list
        x, y, lifetime = spark['x'], spark['y'], spark['lifetime']
        if lifetime > 0:
            # glColor3f(1.0, 1.0, 0.0)  # Yellow color
            # for _ in range(4):  # Draw 4 small lines
            #     angle = random.uniform(0, 2 * 3.14159)  # Random angle
            #     dx = 15 * random.uniform(0.5, 1.5) * math.cos(angle)  # Random length
            #     dy = 15 * random.uniform(0.5, 1.5) * math.sin(angle)  # Random length
            #     MidpointLine(x, y, x + dx, y + dy)
            # spark['lifetime'] -= 1  # Reduce the spark's lifetime
            # Set spark color (default to yellow if no color is specified)
            if 'color' in spark:
                glColor3f(*spark['color'])  # Use specified color (e.g., light blue)
            else:
                glColor3f(1.0, 1.0, 0.0)  # Default to yellow
            for _ in range(4):  # Draw 4 small lines
                angle = random.uniform(0, 2 * 3.14159)  # Random angle
                dx = 15 * random.uniform(0.5, 1.5) * math.cos(angle)  # Random length
                dy = 15 * random.uniform(0.5, 1.5) * math.sin(angle)  # Random length
                MidpointLine(x, y, x + dx, y + dy)
            spark['lifetime'] -= 1  # Reduce the spark's lifetime
        else:
            sparks.remove(spark)  # Remove the spark when its lifetime is over

player_bar = 100
enemy_bar = 100

def draw_health_bar():
    global player_bar, enemy_bar

    p_x_start, p_y_start = 20, 420
    p_bar_width, p_bar_height = 20, 80
    player_filled_height = int((player_bar / 100) * p_bar_height)

    for y in range(p_y_start, p_y_start + player_filled_height + 1):
        if player_bar == 100:
            glColor3f(0, 1, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 90:  
            glColor3f(0, 0.925, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 80:  
            glColor3f(0, 0.85, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 70:  
            glColor3f(0, 0.775, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 60:
            glColor3f(0, 0.7, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 50:  
            glColor3f(0, 0.625, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 40:  
            glColor3f(0, 0.55, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 30:  
            glColor3f(0, 0.475, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 20:  
            glColor3f(0, 0.4, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 10:  
            glColor3f(0, 0.325, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        elif player_bar > 0: 
            glColor3f(.85, 0, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)
        else:
            glColor3f(0.7, 0, 0)
            MidpointLine(p_x_start, y, p_x_start + p_bar_width, y)

    e_x_start, e_y_start = 760, 420
    e_bar_width, e_bar_height = 20, 80
    enemy_filled_height = int((enemy_bar / 100) * e_bar_height)

    for y in range(e_y_start, e_y_start + enemy_filled_height + 1):
        if enemy_bar == 100:
            glColor3f(1.0, 0.647, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 90:
            glColor3f(1.0, 0.6, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 80:
            glColor3f(1.0, 0.55, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 70:
            glColor3f(1.0, 0.5, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 60:
            glColor3f(1.0, 0.45, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 50:
            glColor3f(1.0, 0.4, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 40:
            glColor3f(1.0, 0.35, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 30:
            glColor3f(1.0, 0.3, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 20:
            glColor3f(1.0, 0.25, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 10:
            glColor3f(1.0, 0.2, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        elif enemy_bar > 0:
            glColor3f(0.85,0, 0.0)  
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)
        else:
            glColor3f(0.7, 0.1, 0.0) 
            MidpointLine(e_x_start, y, e_x_start + e_bar_width, y)


def check_bullet_collisions():
    global bullets, player_health, enemy_health, player_y, enemy_y, sparks, gameOver,player_bar,enemy_bar

    for bullet in bullets[:]:
        # Check if bullet hits the player
        if (player_position - 10 <= bullet['x'] <= player_position + 10 and
                player_y - 70 <= bullet['y'] <= player_y + 30):
            player_bar = max(player_bar - 10, 0)
            player_health = max(0, player_health - 10)
            bullets.remove(bullet)
            sparks.append({'x': bullet['x'], 'y': bullet['y'], 'lifetime': 10})  # Add spark effect

            print(f"Player hit by bullet! Health: {player_health}")

        # Check if bullet hits the enemy
        if (enemy_position - 10 <= bullet['x'] <= enemy_position + 10 and
                enemy_y - 70 <= bullet['y'] <= enemy_y + 30):
            enemy_bar = max(enemy_bar - 10, 0)
            enemy_health = max(0, enemy_health - 10)
            bullets.remove(bullet)
            sparks.append({'x': bullet['x'], 'y': bullet['y'], 'lifetime': 10})  # Add spark effect

            print(f"Enemy hit by bullet! Health: {enemy_health}")

    if player_health <= 0 or enemy_health <= 0:
        game_over()


def update_game():
    global bullets, player_position, player_y, player_velocity_y, player_velocity_x, is_jumping, orientation, is_falling_after_bounce
    global enemy_position, enemy_velocity_y, enemy_is_jumping, enemy_shoot_cooldown
    global gameOver, sparks, collision_cooldown, collision_force, player_shoot_cooldown

    enemy_ai()
    # Apply gravity
    GRAVITY = 0.5
    if is_jumping:
        player_velocity_y -= GRAVITY  # Reduce upward velocity
        player_y += player_velocity_y  # Update vertical position
        player_position += player_velocity_x  # Update horizontal position

        # Disable horizontal movement while falling after bouncing
        if not is_falling_after_bounce:
            player_position += player_velocity_x  # Update horizontal position

        # Bounce off left wall
        if player_position - PLAYER_WIDTH // 2 < 0:
            player_position = PLAYER_WIDTH // 2
            player_velocity_x = abs(player_velocity_x)  # Bounce to the right
            orientation = "right"  # Change orientation to face right
            is_falling_after_bounce = True  # Enter falling after bounce state

        # Bounce off right wall
        if player_position + PLAYER_WIDTH // 2 > WINDOW_X:
            player_position = WINDOW_X - PLAYER_WIDTH // 2
            player_velocity_x = -abs(player_velocity_x)  # Bounce to the left
            orientation = "left"  # Change orientation to face left
            is_falling_after_bounce = True  # Enter falling after bounce state

        # Check if player has landed
        if player_y <= 80:  # Ground level
            player_y = 80
            player_velocity_y = 0
            player_velocity_x = 0
            is_jumping = False
            is_falling_after_bounce = False  # Exit falling after bounce state

    # Keep player within window bounds (ground movement)
    player_position = max(PLAYER_WIDTH // 2, min(player_position, WINDOW_X - PLAYER_WIDTH // 2))

    # Reduce player's shoot cooldown
    if player_shoot_cooldown > 0:
        player_shoot_cooldown -= 1

    for bullet in bullets:
        bullet['x'] += bullet['velocity_x']
        bullet['y'] += bullet['velocity_y']

    # Remove bullets off-screen
    bullets = [bullet for bullet in bullets if 0 <= bullet['x'] <= WINDOW_X and 0 <= bullet['y'] <= WINDOW_Y]

    # Check for collision between player and enemy
    if collision_cooldown <= 0 and abs(player_position - enemy_position) < 20:  # Collision detection
        # Apply momentum to player and enemy
        if player_position < enemy_position:
            player_position -= collision_force
            enemy_position += collision_force
        else:
            player_position += collision_force
            enemy_position -= collision_force

        # Add spark effect at the midpoint of collision
        spark_x = (player_position + enemy_position) // 2
        spark_y = 80  # Ground level
        sparks.append({'x': spark_x, 'y': spark_y, 'lifetime': 10})

        # Set collision cooldown
        collision_cooldown = 60  # 1 second cooldown (60 frames)

    # Reduce collision cooldown
    if collision_cooldown > 0:
        collision_cooldown -= 1


def restart_game():
    global bullets, gameOver, gamePaused, orientation, is_jumping, enemy_orientation
    global player_position, enemy_position, player_y, player_velocity_y,  player_velocity_x
    global player_health, enemy_health, enemy_y, sparks, game_over_blink, blink_timer, blink_state,player_bar,enemy_bar
    global enemy_velocity_y, enemy_velocity_x, num_stars, star_positions

    print("Starting Over!")

    player_position = WINDOW_X // 4
    enemy_position = WINDOW_X - 200

    # Reset player vertical and horizontal states
    player_y = 80  # Ground level
    enemy_y = 80
    player_velocity_y = 0
    player_velocity_x = 0
    enemy_velocity_y = 0
    enemy_velocity_x = 0
    orientation = "right"
    enemy_orientation = "left"
    is_jumping = False

    # Reset health
    player_health = 100
    enemy_health = 100
    player_bar = 100
    enemy_bar = 100

    gameOver = False
    gamePaused = False
    game_over_blink = False
    blink_timer = 0
    blink_state = True

    bullets = []
    sparks = []
    num_stars = 4

    star_positions = []  
    initialize_stars()


def toggle_pause():
    global gamePaused
    if not gamePaused:
        gamePaused = True           # I am pausing it because active
        print("Game is paused!")
    else:
        gamePaused = False          # I am un-pausing it because inactive
        print("Game is active!")

def game_over():
    global gameOver, gamePaused, bullets, num_stars, game_over_blink

    if not gameOver:  # Ensure this runs only once
        print("Game Over!")
        bullets = []  # Clear all bullets
        num_stars = 0
        game_over_blink = True
        gamePaused = True
    gameOver = True

def render_text(x, y, text):
    glColor3f(1.0, 0.0, 0.0)  # Red color
    glRasterPos2f(x, y)  # Set the position for the text
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))  # Render each character

# Setup Function:
# This function sets up the OpenGL environment, specifically configuring the viewport and projection matrix.
def iterate():
    glViewport(0, 0, WINDOW_X, WINDOW_Y)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WINDOW_X, 0.0, WINDOW_Y, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# Animation Control:
# This function ensures that the game continuously updates and renders frames at a regular interval.
def animate(value):
    global gameOver, gamePaused
    if not gameOver and not gamePaused:
        update_game()
        update_stars()
        create_new_star()
    glutTimerFunc(16, animate, 0)
    glutPostRedisplay()

# Rendering Function: This function handles the actual drawing of objects on the screen
def show_screen():
    global gamePaused, bullets, player_position, enemy_position, orientation, player_y, gameOver
    global game_over_blink, blink_state, blink_timer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_stars()
    draw_health_bar()
    iterate()

    if not gameOver:
        if orientation == "right":
            draw_player_right(player_position, int(player_y))
        elif orientation == "left":
            draw_player_left(player_position, int(player_y))

        if enemy_orientation == "right":
            draw_enemy_right(enemy_position, int(enemy_y))
        elif enemy_orientation == "left":
            draw_enemy_left(enemy_position, int(enemy_y))

        draw_arrow()
        draw_cross()
        if gamePaused:
            draw_play_button()
        else:
            draw_pause_button()

        for bullet in bullets:
            glColor3f(1.0, 0.0, 0.0)
            MidpointCircle(2, bullet['x'], bullet['y'])

        # Draw sparks
        show_sparks()

    else:
        # Game-over screen
        if game_over_blink:
            # Blink the "GAME OVER!" message
            if blink_timer % 30 == 0:  # Toggle every 30 frames
                blink_state = not blink_state

            if blink_state:
                render_text(WINDOW_X // 2 - 50, WINDOW_Y // 2, "GAME OVER!")  # Render the message

            blink_timer += 2

            # Reset the game after the blink
            if blink_timer > 60:  # Blink for 60 frames (1 second at 60 FPS)
                restart_game()
                game_over_blink = False
                blink_timer = 0
                blink_state = True

    glutSwapBuffers()
    check_bullet_collisions()

def keyboardListener(key, x, y): 
    global gamePaused, bullets
    
    if not gameOver and not gamePaused:
        # Update key states
        if key in key_states:
            key_states[key] = True  # Key is pressed
        handle_player_mov(key)

    glutPostRedisplay()

def keyboardUpListener(key, x, y):
    global key_states

    # Update key states
    if key in key_states:
        key_states[key] = False  # Key is released

def mouseInput(button, state, x, y):
    global gamePaused, gameOver, player_y, player_position, orientation, player_shoot_cooldown

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            mouse_x = x
            mouse_y = WINDOW_Y - y

            if 10 <= mouse_x <= 90 and 530 <= mouse_y <= 590:
                # print("Restart button clicked")
                restart_game()

            elif 370 <= mouse_x <= 430 and 520 <= mouse_y <= 580:
                if not gameOver:                         # When the game is active, you can execute toggle
                    # print("Pause/Play button clicked")
                    toggle_pause()
                else:
                    # If the game is over and the Play Button is clicked, resume the game
                    gamePaused = False
                    gameOver = False
                    print("Game resumed!")

            elif 710 <= mouse_x <= 790 and 510 <= mouse_y <= 590:
                # print("Exit button clicked")
                print("Goodbye!")
                gameOver = True
                glutLeaveMainLoop()

            elif not gamePaused and not gameOver and player_shoot_cooldown <= 0:
                # Calculate the direction vector from the player to the mouse click
                dx = mouse_x - player_position
                dy = mouse_y - player_y

                # Restrict shooting to the direction the player is facing
                if (orientation == "right" and dx >= 0) or (orientation == "left" and dx <= 0):

                    # Normalize the direction vector
                    magnitude = (dx ** 2 + dy ** 2) ** 0.5
                    if magnitude == 0:
                        return  # Avoid division by zero

                    dx /= magnitude
                    dy /= magnitude

                    # Set bullet velocity based on direction
                    bullet_speed = 5
                    velocity_x = dx * bullet_speed
                    velocity_y = dy * bullet_speed

                    # Spawn bullet from the player's hand position
                    bullet_x = player_position - 10 if orientation == "left" else player_position + 40  # Adjust for hand position
                    bullet_y = player_y + 2  # Adjust for hand position

                    # Add bullet to the list
                    bullets.append({'x': bullet_x, 'y': bullet_y, 'velocity_x': velocity_x, 'velocity_y': velocity_y})

                    player_shoot_cooldown = player_shoot_delay

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutInitWindowSize(WINDOW_X, WINDOW_Y)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Pixel Gladiators!")
glutDisplayFunc(show_screen)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseInput)
glutTimerFunc(16, animate, 0)
window_height = glutGet(GLUT_WINDOW_HEIGHT)
initialize_stars()
glutMainLoop()
