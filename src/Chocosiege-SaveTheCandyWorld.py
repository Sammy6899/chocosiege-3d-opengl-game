from math import cos, hypot, radians, sin
from random import choice, randint
from sys import platform
from time import monotonic

if platform == "win32":
    from ctypes import byref, windll
    from ctypes.wintypes import RECT

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 800
WINDOW_TITLE = "Chocosiege-Save The CandyWorld"

LANES = (-150, 0, 150)
HERO_Y = -280
ROAD_HALF_WIDTH = 260
RUN_SPEED = 170
SNOWMAN_SPEED = 25
FIRE_SPEED = 520
ENEMY_BALL_SPEED = 180
REQUIRED_CRYSTALS = 12

MAZE_ROWS = 21
MAZE_COLUMNS = 17
MAZE_CELL_SIZE = 112
EXTRA_MAZE_PATHS = 14
MAZE_DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
HILL_COLORS = ((.95, .43, .67), (.69, .40, .88), (.93, .66, .33))

player = {}
game = {}
king = {}
fireballs = []
enemy_balls = []
snowmen = []
forest_items = []
forest_scenery = []


def draw_sphere(x, y, z, radius, color, scale=(1, 1, 1)):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x, y, z)
    glScalef(*scale)
    gluSphere(gluNewQuadric(), radius, 12, 10)
    glPopMatrix()


def draw_cube(x, y, z, width, depth, height, color, angle=0):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)
    glScalef(width, depth, height)
    glutSolidCube(1)
    glPopMatrix()


def draw_cylinder(x, y, z, radius, height, color, rx=0, ry=0, rz=0):
    glPushMatrix()
    glColor3f(*color)
    glTranslatef(x, y, z)
    glRotatef(rx, 1, 0, 0)
    glRotatef(ry, 0, 1, 0)
    glRotatef(rz, 0, 0, 1)
    gluCylinder(gluNewQuadric(), radius, radius * .75, height, 10, 4)
    glPopMatrix()


def draw_floor(x1, y1, x2, y2, z, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x1, y1, z)
    glVertex3f(x2, y1, z)
    glVertex3f(x2, y2, z)
    glVertex3f(x1, y2, z)
    glEnd()


def touches(first, second, width, depth):
    return (abs(first["x"] - second["x"]) < width
            and abs(first["y"] - second["y"]) < depth)


def hurt_player():
    if game["state"] not in ("FOREST", "KINGDOM"):
        return
    if player["invincible"] > 0:
        return
    player["health"] -= 1
    player["invincible"] = 1.1
    if player["health"] <= 0:
        game["state"] = "GAME_OVER"


def draw_hero():
    speed = 12 if game["state"] in ("FOREST", "MAZE") else 5
    running = sin(game["clock"] * speed)

    glPushMatrix()
    glTranslatef(player["x"], HERO_Y, player["z"] + abs(running) * 3)
    if game["state"] in ("MAZE", "VICTORY"):
        glRotatef(-game["maze_heading"] * 90, 0, 0, 1)
    if game["state"] == "GAME_OVER":
        glRotatef(82, 0, 1, 0)

    draw_cube(0, 0, 53, 33, 21, 44, (.08, .27, .82))
    draw_cube(0, 0, 31, 31, 22, 9, (.93, .69, .08))
    draw_sphere(0, 0, 88, 17, (.96, .70, .52), (1, .92, 1.08))
    draw_sphere(0, -2, 101, 17, (.06, .05, .08), (1.05, .92, .45))
    draw_sphere(-7, 15, 90, 2.4, (.05, .04, .05))
    draw_sphere(7, 15, 90, 2.4, (.05, .04, .05))
    draw_cube(0, 12, 57, 19, 3, 17, (.86, .06, .08), 45)
    draw_cube(0, 14, 57, 10, 3, 10, (1, .78, .08), 45)

    cape_wave = sin(game["clock"] * 10) * 11
    for piece in range(3):
        glPushMatrix()
        glTranslatef(0, -16 - piece * 23, 70 - piece * 12)
        glRotatef(18 + piece * 9 + cape_wave * (piece + 1) / 3, 1, 0, 0)
        draw_cube(0, 0, 0, 38 + piece * 5, 34, 3, (.80 + piece * .04, .03, .06))
        glPopMatrix()

    for side in (-1, 1):
        swing = running * 42 * side

        glPushMatrix()
        glTranslatef(side * 20, 0, 70)
        glRotatef(-swing, 1, 0, 0)
        draw_cylinder(0, 0, -25, 5, 28, (.08, .25, .76), rx=180)
        draw_sphere(0, 0, -29, 5.5, (.96, .70, .52))
        glPopMatrix()

        glPushMatrix()
        glTranslatef(side * 10, 0, 29)
        glRotatef(swing, 1, 0, 0)
        draw_cylinder(0, 0, -27, 6, 31, (.06, .22, .72), rx=180)
        draw_cylinder(0, 0, -34, 7, 13, (.82, .03, .07), rx=180)
        glPopMatrix()

    draw_cylinder(23, 3, 62, 5, 38, (.14, .14, .18), rx=-90)
    draw_cylinder(23, 36, 62, 8, 12, (.82, .05, .06), rx=-90)
    glPopMatrix()


def change_lane(direction):
    player["lane"] = max(0, min(2, player["lane"] + direction))
    player["target_x"] = LANES[player["lane"]]


def fire_gun():
    if game["state"] not in ("FOREST", "KINGDOM"):
        return
    if player["fire_delay"] > 0 or player["heat"] >= 100:
        return

    fireballs.append({"x": player["x"] + 23,
                      "y": HERO_Y + 48,
                      "z": player["z"] + 62,
                      "life": 2.2})
    player["fire_delay"] = .22
    player["heat"] = min(100, player["heat"] + 14)


def update_player(seconds):
    player["x"] += (player["target_x"] - player["x"]) * min(1, seconds * 12)

    if player["jumping"]:
        player["z"] += player["jump_velocity"] * seconds
        player["jump_velocity"] -= 330 * seconds
        if player["z"] <= 0:
            player["z"] = 0
            player["jump_velocity"] = 0
            player["jumping"] = False

    player["fire_delay"] = max(0, player["fire_delay"] - seconds)
    player["invincible"] = max(0, player["invincible"] - seconds)
    player["heat"] = max(0, player["heat"] - 25 * seconds)


def draw_fireballs():   
    for ball in fireballs:
        draw_sphere(ball["x"], ball["y"], ball["z"], 11, (1, .23, .03))
        draw_sphere(ball["x"], ball["y"] - 10, ball["z"], 7, (1, .72, .04))
        draw_sphere(ball["x"], ball["y"] - 18, ball["z"], 4, (.95, .08, .02))


def update_fireballs(seconds):
    for ball in fireballs[:]:
        ball["y"] += FIRE_SPEED * seconds
        ball["life"] -= seconds
        hit = False

        for enemy in snowmen:
            if enemy["alive"] and touches(ball, enemy, 35, 42):
                enemy["health"] -= 1
                enemy["burn"] = .5
                hit = True
                if enemy["health"] <= 0:
                    enemy["alive"] = False
                    game["score"] += 100
                break

        if not hit and game["state"] == "KINGDOM":
            hit = damage_chocolate_king(ball)

        if hit or ball["life"] <= 0 or ball["y"] > 1050:
            fireballs.remove(ball)


def spawn_snowman(lane, y):
    snowmen.append({"x": LANES[lane], "y": y, "health": 2,
                    "alive": True, "burn": 0,    
                    "shot": 1.5 + randint(0, 10) / 10})


def draw_snowman(enemy):
    if not enemy["alive"]:
        return

    wobble = sin(game["clock"] * 7 + enemy["y"] * .01) * 10
    color = (1, .28, .04) if enemy["burn"] > 0 else (.78, .86, .93)

    glPushMatrix()
    glTranslatef(enemy["x"], enemy["y"], 0)
    glRotatef(wobble, 0, 0, 1)
    draw_sphere(0, 0, 28, 27, color, (1.25, .86, 1))
    draw_sphere(0, 0, 68, 22, color, (.9, 1.2, 1))
    draw_sphere(0, 0, 104, 17, (.67, .75, .82), (1.15, .9, 1.2))
    draw_sphere(-8, 13, 110, 4, (1, 0, 0))
    draw_sphere(9, 11, 105, 6, (.7, 0, 0))

    for side in (-1, 1):
        draw_cylinder(side * 13, 0, 116, 4, 27, (.18, .12, .12), ry=side * 42)
        draw_cylinder(side * 22, -1, 73, 4, 47, (.24, .15, .12), ry=side * 72, rz=side * 24)
        draw_cylinder(side * 18, 0, 56, 3, 39, (.18, .10, .10), ry=side * 60, rz=-side * 35)
        draw_cube(side * 7, 15, 93, 6, 6, 8, (1, 1, .84), 25 * side)

    draw_cylinder(0, 13, 98, 4, 22, (.95, .29, .05), ry=80)
    glPopMatrix()


def snowman_attack(enemy):
    dx = player["x"] - enemy["x"]
    dy = HERO_Y - enemy["y"]
    distance = hypot(dx, dy) or 1
    enemy_balls.append({"x": enemy["x"], "y": enemy["y"], "z": 72,   
                        "dx": dx / distance, "dy": dy / distance, "life": 4})


def update_snowmen(seconds):
    for enemy in snowmen[:]:
        enemy["y"] -= (RUN_SPEED + SNOWMAN_SPEED) * seconds
        enemy["burn"] = max(0, enemy["burn"] - seconds)
        enemy["shot"] -= seconds

        if enemy["alive"] and enemy["shot"] <= 0 and enemy["y"] > HERO_Y:
            snowman_attack(enemy)
            enemy["shot"] = 2.5

        close_x = abs(enemy["x"] - player["x"]) < 42
        close_y = abs(enemy["y"] - HERO_Y) < 42
        if enemy["alive"] and close_x and close_y and player["z"] < 48:
            hurt_player()
            enemy["alive"] = False

        if enemy["y"] < -430:
            snowmen.remove(enemy)


def update_enemy_balls(seconds):
    for ball in enemy_balls[:]:
        ball["x"] += ball["dx"] * ENEMY_BALL_SPEED * seconds
        ball["y"] += ball["dy"] * ENEMY_BALL_SPEED * seconds
        ball["life"] -= seconds

        hit = (abs(ball["x"] - player["x"]) < 28
               and abs(ball["y"] - HERO_Y) < 32)
        if hit and player["z"] < 75:
            hurt_player()
        if hit or ball["life"] <= 0 or ball["y"] < -430:
            enemy_balls.remove(ball)


def draw_enemy_balls():
    for ball in enemy_balls:
        chocolate = ball.get("chocolate", False)
        color = (1, 1, 1) if chocolate else (.55, .90, 1)
        radius = 12 if chocolate else 10
        draw_sphere(ball["x"], ball["y"], ball["z"], radius, color)


def draw_crystal(x, y, z, precious=False):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(game["clock"] * 110, 0, 0, 1)
    glRotatef(45, 1, 0, 0)
    color = (1, .75, .08) if precious else (.25, .95, 1)
    glColor3f(*color)
    glScalef(1.1, 1.1, 1.5)
    glutSolidCube(35 if precious else 22)
    glPopMatrix()


def draw_forest_tree(tree):
    x, y = tree["x"], tree["y"]
    if tree["kind"] == "tree":
        draw_cylinder(x, y, 0, 11, 95, (.91, .73, .78))
        draw_sphere(x, y, 105, 39, (1, .87, .94), (1.3, 1.1, 1))
        draw_sphere(x - 25, y, 90, 29, (.87, .77, .99))
        draw_sphere(x + 27, y, 94, 31, (1, .72, .87))
    else:
        draw_sphere(x, y, 5, 75, tree["color"], (1.7, 1.25, .75))
        draw_sphere(x - 35, y, 35, 22, (1, .92, .94))


def draw_candyfloss_cloud(x, y, z, size, color):
    x += sin(game["clock"] * .35 + x * .01) * 14
    pieces = ((-53, 0, 37), (-24, 15, 47), (14, 22, 51),
              (49, 5, 39), (76, -3, 28))
    for offset_x, offset_z, radius in pieces:
        draw_sphere(x + offset_x * size, y, z + offset_z * size,
                    radius * size, color, (1.15, .52, .82))


def draw_aesthetic_background():
    edge, front, back = 1650, -1650, 1450
    sky_bands = ((-55, 100, (1, .65, .77), (.94, .50, .76)),
                 (100, 265, (.94, .50, .76), (.73, .39, .77)),
                 (265, 490, (.73, .39, .77), (.47, .28, .69)),
                 (490, 1100, (.47, .28, .69), (.22, .15, .42)))

    sides = (((-edge, front), (edge, front)),
             ((edge, front), (edge, back)),
             ((edge, back), (-edge, back)),
             ((-edge, back), (-edge, front)))

    for bottom, top, lower_color, upper_color in sky_bands:
        glBegin(GL_QUADS)
        for (x1, y1), (x2, y2) in sides:
            glColor3f(*lower_color)
            glVertex3f(x1, y1, bottom)
            glVertex3f(x2, y2, bottom)
            glColor3f(*upper_color)
            glVertex3f(x2, y2, top)
            glVertex3f(x1, y1, top)
        glEnd()

    draw_floor(-edge, front, edge, back, -55, (.81, .49, .73))
    draw_floor(-edge, front, edge, back, 1100, (.22, .15, .42))

    valley_colors = ((.35, .14, .18), (.46, .20, .21), (.32, .11, .16))
    for index in range(18):
        angle = radians(index * 20)
        x = cos(angle) * 1160
        y = HERO_Y + sin(angle) * 1160
        radius = 138 + (index % 4) * 17
        draw_sphere(x, y, 100 + (index % 3) * 20, radius,
                    valley_colors[index % 3], (1.32, 1.1, .83))

    cloud_colors = ((1, .76, .90), (.88, .74, 1), (1, .67, .84))
    for index in range(12):
        angle = radians(index * 30 + 12)
        x = cos(angle) * 1070
        y = HERO_Y + sin(angle) * 1070
        z = 370 + (index % 4) * 68
        draw_candyfloss_cloud(x, y, z, .70 + (index % 3) * .10, cloud_colors[index % 3])

    glPointSize(4)
    glBegin(GL_POINTS)
    for index in range(72):
        angle = radians(index * 5)
        glColor3f(1, .84 + (index % 3) * .05, .93)
        glVertex3f(cos(angle) * 1100, HERO_Y + sin(angle) * 1100,
                   205 + (index * 61) % 440 + sin(game["clock"] + index) * 5)
    glEnd()


def spawn_forest_object():
    chance = randint(1, 100)
    lane = randint(0, 2)
    if chance <= 48:
        forest_items.append({"type": "crystal", "x": LANES[lane], "y": 950})
    elif chance <= 77:
        spawn_snowman(lane, 950)
    else:
        forest_items.append({"type": "hill", "x": LANES[lane], "y": 950})


def draw_forest_world():
    draw_floor(-ROAD_HALF_WIDTH, -430, ROAD_HALF_WIDTH, 1100, 0, (.57, .35, .57))
    draw_floor(-650, -430, -ROAD_HALF_WIDTH, 1100, -1, (.91, .72, .88))
    draw_floor(ROAD_HALF_WIDTH, -430, 650, 1100, -1, (.83, .70, .95))

    offset = game["distance"] % 100
    for index in range(17):
        y = -400 + index * 100 - offset
        draw_cube(-82, y, 2, 7, 48, 4, (1, .77, .79))
        draw_cube(82, y, 2, 7, 48, 4, (.89, .72, 1))

    for tree in forest_scenery:
        draw_forest_tree(tree)


def draw_forest_items():
    for item in forest_items:
        if item["type"] == "crystal":
            height = 43 + sin(game["clock"] * 5) * 7
            draw_crystal(item["x"], item["y"], height)
        else:
            draw_sphere(item["x"], item["y"], 5, 47, (.95, .32, .59), (1.35, .9, .7))
            draw_sphere(item["x"], item["y"], 35, 19, (1, .75, .12))


def update_forest_world(seconds):
    game["distance"] += RUN_SPEED * seconds
    game["spawn_timer"] -= seconds
    if game["spawn_timer"] <= 0:
        spawn_forest_object()
        game["spawn_timer"] = .72

    for tree in forest_scenery:
        tree["y"] -= RUN_SPEED * seconds
        if tree["y"] < -470:
            tree["y"] += 1710
            tree["x"] = choice((-430, -350, 350, 430))
            tree["color"] = choice(HILL_COLORS)

    for item in forest_items[:]:
        item["y"] -= RUN_SPEED * seconds
        close = (abs(item["x"] - player["x"]) < 40    
                 and abs(item["y"] - HERO_Y) < 40)
        if close and item["type"] == "crystal":
            game["crystals"] += 1
            game["score"] += 25
            forest_items.remove(item)
        elif close and item["type"] == "hill":
            if player["z"] < 52:
                hurt_player()
            forest_items.remove(item)
        elif item["y"] < -430:
            forest_items.remove(item)

    if game["crystals"] >= REQUIRED_CRYSTALS:
        enter_chocolate_kingdom()


def enter_chocolate_kingdom():
    game["state"] = "KINGDOM"
    forest_items.clear()
    forest_scenery.clear()
    snowmen.clear()
    enemy_balls.clear()
    fireballs.clear()
    player["x"] = 0
    player["target_x"] = 0
    player["lane"] = 1
    player["z"] = 0


def draw_chocolate_kingdom():
    draw_floor(-ROAD_HALF_WIDTH, -430, ROAD_HALF_WIDTH, 1100, 0, (.31, .12, .09))
    draw_floor(-650, -430, -ROAD_HALF_WIDTH, 1100, -1, (.42, .17, .13))
    draw_floor(ROAD_HALF_WIDTH, -430, 650, 1100, -1, (.42, .17, .13))

    for side in (-1, 1):
        draw_cube(side * 430, 320, 85, 170, 500, 170, (.28, .08, .03))
        draw_cylinder(side * 360, 560, 0, 55, 230, (.36, .10, .04))
        draw_sphere(side * 360, 560, 245, 64, (.48, .15, .05))

    draw_cube(-172, 650, 120, 176, 90, 240, (.34, .09, .03))
    draw_cube(172, 650, 120, 176, 90, 240, (.34, .09, .03))
    draw_cube(0, 650, 230, 170, 90, 28, (.44, .16, .07))

    lift = min(245, game["door_timer"] * 155)
    draw_cube(0, 595, 110 + lift, 165, 45, 205, (.10, .03, .02))
    draw_cube(0, 571, 112 + lift, 122, 5, 12, (.91, .66, .20))

    if game["state"] == "DOOR_OPEN":
        for index in range(3):
            draw_crystal((index - 1) * 45, 565, 58 + index * 8, True)


def draw_chocolate_king():
    if game["state"] != "KINGDOM":
        return

    color = (1, .35, .12) if king["hit_flash"] > 0 else (.30, .10, .04)
    x, y = king["x"], king["y"]
    draw_sphere(x, y, 105, 78, color, (1.18, .78, 1.28))
    draw_sphere(x, y, 210, 55, (.38, .13, .05), (1.15, .9, 1.1))

    for side in (-1, 1):
        draw_sphere(x + side * 24, y - 43, 225, 8, (1, .07, .02))
        draw_cylinder(x + side * 76, y, 127, 15, 110, color, ry=side * 72)
        draw_cylinder(x + side * 47, y, 30, 22, 76, (.22, .07, .02))
        draw_cube(x + side * 34, y, 283, 32, 32, 58, (1, .73, .03), side * 12)

    draw_cube(x, y, 265, 95, 55, 20, (1, .67, .02))
    draw_cylinder(x, y - 58, 185, 16, 44, (.15, .04, .02), ry=90)


def damage_chocolate_king(fireball):
    if king["health"] <= 0:
        return False
    close_x = abs(fireball["x"] - king["x"]) < 90
    close_y = abs(fireball["y"] - king["y"]) < 70
    if close_x and close_y:
        king["health"] -= 1
        king["hit_flash"] = .15
        return True
    return False


def chocolate_king_attack():
    for lane in LANES:
        if abs(lane - king["x"]) < 230:
            enemy_balls.append({"x": king["x"], "y": king["y"] - 35,
                                "z": 80, "dx": (lane - king["x"]) / 420,
                                "dy": -1, "life": 4, "chocolate": True})


def update_chocolate_king(seconds):
    if game["state"] != "KINGDOM":
        return

    king["x"] += king["direction"] * 55 * seconds
    if abs(king["x"]) > 155:
        king["x"] = 155 if king["x"] > 0 else -155
        king["direction"] *= -1

    king["attack_timer"] -= seconds
    king["hit_flash"] = max(0, king["hit_flash"] - seconds)
    if king["attack_timer"] <= 0:
        chocolate_king_attack()
        king["attack_timer"] = 2.0

    if king["health"] <= 0:
        king["health"] = 0
        game["state"] = "DOOR_OPEN"
        game["door_timer"] = 0
        game["precious_crystals"] = 3
        game["score"] += 500
        enemy_balls.clear()
        fireballs.clear()


def update_kingdom_door(seconds):
    game["door_timer"] += seconds
    if game["door_timer"] >= 2.0:
        enter_cupcake_maze()


def generate_cupcake_maze():
    maze = [[1 for _ in range(MAZE_COLUMNS)] for _ in range(MAZE_ROWS)]
    maze[1][1] = 0
    stack = [(1, 1)]

    while stack:
        row, column = stack[-1]
        choices = []

        for row_step, column_step in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            next_row = row + row_step
            next_column = column + column_step
            inside = (0 < next_row < MAZE_ROWS - 1
                      and 0 < next_column < MAZE_COLUMNS - 1)
            if inside and maze[next_row][next_column] == 1:
                choices.append((next_row, next_column, row_step, column_step))

        if choices:
            next_row, next_column, row_step, column_step = choice(choices)
            maze[row + row_step // 2][column + column_step // 2] = 0
            maze[next_row][next_column] = 0
            stack.append((next_row, next_column))
        else:
            stack.pop()

    extra_paths = 0
    attempts = 0
    while extra_paths < EXTRA_MAZE_PATHS and attempts < 300:
        attempts += 1
        row = randint(1, MAZE_ROWS - 2)
        column = randint(1, MAZE_COLUMNS - 2)
        if maze[row][column] == 0:
            continue

        above = maze[row - 1][column]
        below = maze[row + 1][column]
        left = maze[row][column - 1]
        right = maze[row][column + 1]

        joins_vertical_paths = above == 0 and below == 0 and left == 1 and right == 1
        joins_horizontal_paths = left == 0 and right == 0 and above == 1 and below == 1
        if joins_vertical_paths or joins_horizontal_paths:
            maze[row][column] = 0
            extra_paths += 1

    maze[0][1] = 0
    maze[MAZE_ROWS - 1][MAZE_COLUMNS - 2] = 0
    return maze


def enter_cupcake_maze():
    game["state"] = "MAZE"
    game["maze_row"] = 0
    game["maze_column"] = 1
    game["maze_heading"] = 0
    game["camera_angle"] = 270
    game["camera_target"] = 270
    player["x"] = 0
    player["target_x"] = 0
    player["z"] = 0
    player["jumping"] = False
    reveal_maze_paths()


def draw_cupcake(x, y, row, column):
    colors = ((1, .49, .70), (.78, .55, .96),
              (1, .77, .48), (.58, .88, .83))
    frosting = colors[(row * 3 + column) % len(colors)]

    draw_cube(x, y, 74, MAZE_CELL_SIZE + 3, MAZE_CELL_SIZE + 3, 148, (.77, .40, .34))
    draw_cube(x, y, 48, MAZE_CELL_SIZE + 5, MAZE_CELL_SIZE + 5, 92, (.91, .61, .48))
    draw_cylinder(x, y, 8, 40, 94, (.67, .34, .23))
    draw_cylinder(x, y, 16, 36, 80, (.94, .67, .53))
    draw_sphere(x, y, 112, 43, frosting, (1.02, 1.02, .72))
    draw_sphere(x, y, 143, 35, frosting, (1, 1, .74))
    draw_sphere(x, y, 170, 24, (1, .88, .93), (1, 1, .78))
    draw_sphere(x, y, 191, 9, (.87, .10, .23))


def reveal_maze_paths():     
    row = game["maze_row"]
    column = game["maze_column"]
    game["maze_seen"].add((row, column))

    for row_step, column_step in MAZE_DIRECTIONS:
        next_row = row + row_step
        next_column = column + column_step
        while (0 <= next_row < MAZE_ROWS    
               and 0 <= next_column < MAZE_COLUMNS
               and game["maze"][next_row][next_column] == 0):  
            game["maze_seen"].add((next_row, next_column))
            next_row += row_step
            next_column += column_step


def draw_cupcake_maze():
    hero_row = game["maze_row"]
    hero_column = game["maze_column"]
    top_view = game["camera_mode"] == 2

    if top_view:  
        left = -hero_column * MAZE_CELL_SIZE - 95
        right = (MAZE_COLUMNS - 1 - hero_column) * MAZE_CELL_SIZE + 95
        bottom = HERO_Y - hero_row * MAZE_CELL_SIZE - 95
        top = HERO_Y + (MAZE_ROWS - 1 - hero_row) * MAZE_CELL_SIZE + 95
        draw_floor(left, bottom, right, top, -2, (.82, .54, .76))
    else:
        draw_floor(-1150, HERO_Y - 850, 1150, HERO_Y + 1150, -2, (.82, .54, .76))

    walls = []    
    for row in range(MAZE_ROWS):
        y = HERO_Y + (row - hero_row) * MAZE_CELL_SIZE 
        if not top_view and not -750 < y < 1150:
            continue

        for column in range(MAZE_COLUMNS):
            x = (column - hero_column) * MAZE_CELL_SIZE
            if not top_view and abs(x) > 1050:  
                continue
            if game["maze"][row][column] == 1:
                walls.append((x, y, row, column))
            elif top_view or (row, column) in game["maze_seen"]:
                color = (.92, .73, .89) if (row + column) % 2 else (.82, .65, .93) 
                draw_floor(x - 49, y - 49, x + 49, y + 49, 0, color)

    exit_cell = (MAZE_ROWS - 1, MAZE_COLUMNS - 2)
    if top_view or exit_cell in game["maze_seen"]:
        exit_x = (exit_cell[1] - hero_column) * MAZE_CELL_SIZE
        exit_y = HERO_Y + (exit_cell[0] - hero_row) * MAZE_CELL_SIZE
        for index in range(3):
            height = 72 + sin(game["clock"] * 4 + index) * 11  
            draw_crystal(exit_x + (index - 1) * 31, exit_y, height, True) 

    if top_view:
        eye_x = ((MAZE_COLUMNS - 1) / 2 - hero_column) * MAZE_CELL_SIZE 
        eye_y = HERO_Y + ((MAZE_ROWS - 1) / 2 - hero_row) * MAZE_CELL_SIZE  
    else:
        angle = radians(game["camera_angle"])
        eye_x = player["x"] + cos(angle) * 52  
        eye_y = HERO_Y + sin(angle) * 52  
    walls.sort(key=lambda wall: ((wall[0] - eye_x) ** 2  
                                 + (wall[1] - eye_y) ** 2), reverse=True)

    for x, y, row, column in walls:
        if top_view:
            colors = ((1, .49, .70), (.78, .55, .96),
                      (1, .77, .48), (.58, .88, .83))
            frosting = colors[(row * 3 + column) % len(colors)]
            draw_cube(x, y, 48, MAZE_CELL_SIZE + 3, MAZE_CELL_SIZE + 3, 96, (.77, .40, .34)) 
            draw_sphere(x, y, 107, 43, frosting, (1, 1, .60))
            draw_sphere(x, y, 134, 9, (.87, .10, .23))
        else:
            draw_cupcake(x, y, row, column)


def move_through_maze(row_step, column_step):
    next_row = game["maze_row"] + row_step
    next_column = game["maze_column"] + column_step
    inside = 0 <= next_row < MAZE_ROWS and 0 <= next_column < MAZE_COLUMNS
    if not inside or game["maze"][next_row][next_column] == 1:
        return

    game["maze_row"] = next_row           
    game["maze_column"] = next_column     
    player["x"] = 0
    player["target_x"] = 0
    game["score"] += 5
    reveal_maze_paths()                   

    if next_row == MAZE_ROWS - 1 and next_column == MAZE_COLUMNS - 2:
        game["state"] = "VICTORY"          
        game["ending_timer"] = 0
        game["score"] += 1000


def handle_maze_controls(key):
    heading = game["maze_heading"]  

    if key in (b"a", b"d"):
        turn = -1 if key == b"a" else 1
        new_heading = (heading + turn) % 4
        row_step, column_step = MAZE_DIRECTIONS[new_heading]
        next_row = game["maze_row"] + row_step
        next_column = game["maze_column"] + column_step
        inside = 0 <= next_row < MAZE_ROWS and 0 <= next_column < MAZE_COLUMNS
        if inside and game["maze"][next_row][next_column] == 0:
            game["maze_heading"] = new_heading  
            game["camera_target"] = (270 - new_heading * 90) % 360
            move_through_maze(row_step, column_step)   

    elif key in (b"w", b"s"):
        row_step, column_step = MAZE_DIRECTIONS[heading]
        direction = 1 if key == b"w" else -1  
        move_through_maze(row_step * direction, column_step * direction)  


def update_maze_camera(seconds):
    difference = (game["camera_target"] - game["camera_angle"] + 180) % 360 - 180
    if abs(difference) < .3:
        game["camera_angle"] = game["camera_target"]
    else:
        game["camera_angle"] = (game["camera_angle"] + difference * min(1, seconds * 8)) % 360


def reset_game(show_start_screen=False):   
    player.clear()
    player.update(x=0, target_x=0, lane=1, z=0, jump_velocity=0,
                  jumping=False, health=5, heat=0, fire_delay=0,
                  invincible=0)

    game.clear()
    game.update(state="START" if show_start_screen else "FOREST",
                clock=0, last_frame=monotonic(), distance=0, crystals=0,
                score=0, spawn_timer=.2, camera_mode=0, camera_height=220,
                camera_angle=270, door_timer=0, precious_crystals=0,
                maze=generate_cupcake_maze(), maze_row=0, maze_column=1,
                maze_seen={(0, 1)}, maze_heading=0, camera_target=270,
                maze_message_timer=0, ending_timer=0, maze_zoom=2450)
    king.clear()
    king.update(x=0, y=340, health=30, attack_timer=1.8,
                direction=1, hit_flash=0)

    fireballs.clear()
    enemy_balls.clear()
    snowmen.clear()
    forest_items.clear()
    forest_scenery.clear()

    for index in range(18):   
        forest_scenery.append({"x": choice((-410, -330, 330, 410)), 
                               "y": -350 + index * 95,
                               "kind": "tree" if index % 3 else "hill",
                               "color": HILL_COLORS[index % 3]})


def draw_text(x, y, message, font=GLUT_BITMAP_HELVETICA_18):  
    glColor3f(1, 1, 1)                    
    glMatrixMode(GL_PROJECTION)           
    glPushMatrix()                        
    glLoadIdentity()                      
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    glMatrixMode(GL_MODELVIEW)            
    glPushMatrix()                        
    glLoadIdentity()                      
    glRasterPos2f(x, y)                   
    for character in message:
        glutBitmapCharacter(font, ord(character))
    glPopMatrix()                         

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()                         
    glMatrixMode(GL_MODELVIEW)


def update_window_size():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    if platform != "win32":
        return

    user32 = windll.user32
    window = (user32.FindWindowW(None, WINDOW_TITLE)
              or user32.GetForegroundWindow()
              or user32.GetActiveWindow())
    rectangle = RECT()
    if window and user32.GetClientRect(window, byref(rectangle)):
        width = rectangle.right - rectangle.left
        height = rectangle.bottom - rectangle.top
        if width > 0 and height > 0:
            WINDOW_WIDTH = width           
            WINDOW_HEIGHT = height        


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(72, WINDOW_WIDTH / max(1, WINDOW_HEIGHT), .1, 4500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    angle = radians(game["camera_angle"])

    if game["state"] in ("MAZE", "VICTORY") and game["precious_crystals"]:
        if game["camera_mode"] == 2:
            center_x = ((MAZE_COLUMNS - 1) / 2 - game["maze_column"]) * MAZE_CELL_SIZE
            center_y = HERO_Y + ((MAZE_ROWS - 1) / 2 - game["maze_row"]) * MAZE_CELL_SIZE
            gluLookAt(center_x, center_y, game["maze_zoom"], 
                      center_x, center_y, 0,                 
                      0, 1, 0)                              
        else:
            look = radians((game["camera_angle"] + 180) % 360)
            gluLookAt(player["x"] + cos(angle) * 52, HERO_Y + sin(angle) * 52, 178, 
                      player["x"] + cos(look) * 185, HERO_Y + sin(look) * 185, 68,  
                      0, 0, 1)                                                      

    elif game["camera_mode"] == 1:
        look = radians((game["camera_angle"] + 180) % 360)
        gluLookAt(player["x"], HERO_Y - 8, player["z"] + 91,               
                  player["x"] + cos(look) * 400, HERO_Y + sin(look) * 400, 70, 
                  0, 0, 1)
    elif game["camera_mode"] == 2:
        gluLookAt(player["x"] + cos(angle) * 80, HERO_Y + sin(angle) * 80, 760, 
                  player["x"], HERO_Y, 0,                                       
                  cos(angle), sin(angle), 0)
    else:
        gluLookAt(player["x"] + cos(angle) * 420, HERO_Y + sin(angle) * 420, game["camera_height"], 
                  player["x"], HERO_Y + 35, 52,                                                      
                  0, 0, 1)


def draw_hud():
    draw_text(15, WINDOW_HEIGHT - 30, "SUGARFLARE: SAVE CANDYWORLD")
    status = (f"Hearts: {player['health']}/5   Heat: {int(player['heat'])}/100   "
              f"Trail Crystals: {game['crystals']}/{REQUIRED_CRYSTALS}   "
              f"Score: {game['score']}   View: {int(game['camera_angle'])} deg")
    draw_text(15, WINDOW_HEIGHT - 58, status)

    state = game["state"]
    if state == "FOREST":
        draw_text(15, WINDOW_HEIGHT - 86, "Mission: Run through the forest, fight snowmen, collect crystals")
    elif state == "KINGDOM":
        draw_text(15, WINDOW_HEIGHT - 86, f"CHOCOLATE KING HEALTH: {king['health']}/30")
    elif state == "DOOR_OPEN":
        draw_text(15, WINDOW_HEIGHT - 86, "THE CHOCOLATE KING IS DEFEATED - THE DOOR IS OPENING!")
    elif state == "MAZE":
        view_name = "TOP VIEW" if game["camera_mode"] == 2 else "HERO VIEW"
        draw_text(15, WINDOW_HEIGHT - 86,
                  f"CUPCAKE MAZE   Precious Crystals: {game['precious_crystals']}/3   {view_name}   Find the exit and save Candyworld")
        if game["maze_message_timer"] < 7:
            draw_text(max(15, WINDOW_WIDTH // 2 - 300), WINDOW_HEIGHT // 2 + 95,
                      "Find the path to candyworld and save the world! Good luck!")

    center_messages = {"START": "PRESS ENTER TO START THE RUN",
                       "PAUSED": "PAUSED - PRESS P TO CONTINUE",
                       "GAME_OVER": "THE HERO FELL - PRESS R TO RESTART"}
    if state in center_messages:
        draw_text(max(20, WINDOW_WIDTH // 2 - 220), WINDOW_HEIGHT // 2, center_messages[state])

    if state == "VICTORY":
        draw_text(max(15, WINDOW_WIDTH // 2 - 260), WINDOW_HEIGHT // 2 + 25, "Congratulations! You just saved Candyworld!")
        if game["ending_timer"] >= 2.5:
            draw_text(max(15, WINDOW_WIDTH // 2 - 38), WINDOW_HEIGHT // 2 - 20, "The End")

    controls = ("W/A/S/D move | T or right-click top view | UP/DOWN zoom | P pause | R restart"
                if state == "MAZE" else
                "A/D lanes | SPACE jump | Left click fire | Arrow keys camera | P pause | R restart")
    draw_text(15, 20, controls)


def keyboard_listener(key, x, y):
    key = key.lower()
    if key == b"r":                        
        reset_game()
    elif key == b"\r" and game["state"] == "START": 
        game["state"] = "FOREST"
        game["last_frame"] = monotonic()
    elif key == b"p" and game["state"] in ("FOREST", "KINGDOM", "MAZE", "PAUSED"): 
        if game["state"] == "PAUSED":
            game["state"] = game["previous_state"] 
        else:
            game["previous_state"] = game["state"] 
            game["state"] = "PAUSED"
        game["last_frame"] = monotonic()
    elif game["state"] == "MAZE":
        if key == b"t":                    
            game["camera_mode"] = 0 if game["camera_mode"] == 2 else 2
        else:
            handle_maze_controls(key)      
    elif game["state"] in ("FOREST", "KINGDOM"):
        if key == b"a":
            change_lane(-1)                
        elif key == b"d":
            change_lane(1)                 
        elif key == b" " and not player["jumping"]: 
            player["jumping"] = True
            player["jump_velocity"] = 185  


def special_key_listener(key, x, y):
    if key == GLUT_KEY_UP:
        if game["state"] == "MAZE" and game["camera_mode"] == 2:
            game["maze_zoom"] = max(1100, game["maze_zoom"] - 150) 
        else:
            game["camera_height"] = min(500, game["camera_height"] + 20) 
    elif key == GLUT_KEY_DOWN:
        if game["state"] == "MAZE" and game["camera_mode"] == 2:
            game["maze_zoom"] = min(3600, game["maze_zoom"] + 150) 
        else:
            game["camera_height"] = max(110, game["camera_height"] - 20) 
    elif key == GLUT_KEY_LEFT and game["state"] != "MAZE":
        game["camera_angle"] = (game["camera_angle"] - 8) % 360     
    elif key == GLUT_KEY_RIGHT and game["state"] != "MAZE":
        game["camera_angle"] = (game["camera_angle"] + 8) % 360     


def mouse_listener(button, state, x, y):
    if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
        fire_gun()                         
    elif state == GLUT_DOWN and button == GLUT_RIGHT_BUTTON:
        if game["state"] in ("MAZE", "VICTORY"):
            game["camera_mode"] = 0 if game["camera_mode"] == 2 else 2 
        else:
            game["camera_mode"] = (game["camera_mode"] + 1) % 3        


def idle():
    now = monotonic()                      
    seconds = min(now - game["last_frame"], .04) 
    game["last_frame"] = now
    state = game["state"]

    if state in ("FOREST", "KINGDOM"):
        game["clock"] += seconds
        update_player(seconds)             
        update_fireballs(seconds)          
        update_enemy_balls(seconds)        
        if state == "FOREST":
            update_forest_world(seconds)   
            update_snowmen(seconds)        
        else:
            update_chocolate_king(seconds) 
    elif state == "DOOR_OPEN":
        game["clock"] += seconds
        update_kingdom_door(seconds)       
    elif state == "MAZE":
        game["clock"] += seconds
        game["maze_message_timer"] += seconds
        update_maze_camera(seconds)        
        update_player(seconds)
    elif state == "VICTORY":
        game["clock"] += seconds
        game["ending_timer"] += seconds

    glutPostRedisplay()                   


def show_screen():
    update_window_size()                   
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()                       
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT) 
    setup_camera()                         
    draw_aesthetic_background()            

    state = game["state"]

    if state in ("KINGDOM", "DOOR_OPEN"):
        draw_chocolate_kingdom()           
    elif state in ("MAZE", "VICTORY") and game["precious_crystals"]:
        draw_cupcake_maze()                
    else:
        draw_forest_world()                

    draw_forest_items()                    
    for enemy in snowmen:
        draw_snowman(enemy)                
    draw_enemy_balls()                    
    draw_chocolate_king()                  
    draw_fireballs()                       

    if game["camera_mode"] != 1 or state in ("MAZE", "VICTORY"):
        draw_hero()
    draw_hud()                            
    glutSwapBuffers()                     


def main():
    reset_game(show_start_screen=True)     
    glutInit()                             
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)  
    glutInitWindowPosition(0, 0)          
    glutCreateWindow(WINDOW_TITLE.encode())
    glutDisplayFunc(show_screen)          
    glutKeyboardFunc(keyboard_listener)   
    glutSpecialFunc(special_key_listener) 
    glutMouseFunc(mouse_listener)         
    glutIdleFunc(idle)                    
    glutMainLoop()                        


if __name__ == "__main__":
    main()