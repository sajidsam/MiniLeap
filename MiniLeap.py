from OpenGL.GL import *
from OpenGL.GLUT import (
    glutInit, glutInitDisplayMode, glutInitWindowSize,
    glutCreateWindow, glutDisplayFunc, glutKeyboardFunc,
    glutTimerFunc, glutMainLoop, glutBitmapCharacter,
    glutPostRedisplay, glutGet, GLUT_ELAPSED_TIME,
    GLUT_DOUBLE, GLUT_RGB, glutSwapBuffers,
    GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12,
    GLUT_BITMAP_TIMES_ROMAN_24, glutMouseFunc,
    GLUT_LEFT_BUTTON, GLUT_DOWN, glutReshapeFunc
)
import random
import math

# ============================================================
# SOUND SETUP  ← only new addition
# ============================================================
import pygame
pygame.mixer.init()
sound_coin   = pygame.mixer.Sound("assets/Sound/coin.wav")
sound_dizzy  = pygame.mixer.Sound("assets/Sound/dizzy.wav")
sound_jump   = pygame.mixer.Sound("assets/Sound/jump.wav")
sound_jungle = pygame.mixer.Sound("assets/Sound/JungleSound.wav")
sound_jungle.play(-1)   # loop jungle bg forever

# ============================================================
# WINDOW CONSTANTS
# ============================================================
WIN_W = 1200
WIN_H = 600

# ============================================================
# SCREEN STATES
# ============================================================
SCREEN_SPLASH      = 0
SCREEN_STORY       = 1
SCREEN_INSTRUCTIONS= 2
SCREEN_MAIN_MENU   = 3
SCREEN_CONFIRM     = 4
SCREEN_GAME        = 5
SCREEN_GAMEOVER    = 6

current_screen = SCREEN_SPLASH

# ============================================================
# GAME GLOBALS
# ============================================================
selected_level  = 0   # 0=Jungle 1=Ice 2=Underground
cat_x           = -0.65
cat_y           = -0.70
velocity_y      = 0.0
gravity         = -0.007
jump_power      = 0.105
ground_y        = -0.70
jumping         = False
jump_count      = 0

score           = 0
injury_count    = 0
game_over_flag  = False
speed           = 0.010
speed_timer     = 0

obstacles       = []
coins           = []
stars           = []
rain_drops      = []
rain_active     = False
rain_timer      = 0
story_phase     = 0
story_timer     = 0
fly_x           = 0.0
fly_y           = 0.0
fly_dir         = 1
confirm_level   = -1

# ============================================================
# UTILITIES
# ============================================================
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def draw_rect(x, y, w, h):
    glBegin(GL_QUADS)
    glVertex2f(x,     y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x,     y + h)
    glEnd()

def draw_circle(cx, cy, r, segments=48):
    glBegin(GL_POLYGON)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + r * math.cos(a), cy + r * math.sin(a))
    glEnd()

def draw_ellipse(cx, cy, rx, ry, segments=48):
    glBegin(GL_POLYGON)
    for i in range(segments):
        a = 2 * math.pi * i / segments
        glVertex2f(cx + rx * math.cos(a), cy + ry * math.sin(a))
    glEnd()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_text_centered(y, text, font=GLUT_BITMAP_HELVETICA_18, char_w=0.011):
    approx_w = len(text) * char_w
    draw_text(-approx_w / 2, y, text, font)

def draw_star_shape(cx, cy, outer, inner, points=5):
    glBegin(GL_POLYGON)
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        r = outer if i % 2 == 0 else inner
        glVertex2f(cx + r * math.cos(angle), cy + r * math.sin(angle))
    glEnd()

# ============================================================
# CAT DRAW
# ============================================================
def draw_cat(x, y, scale=1.0):
    t = glutGet(GLUT_ELAPSED_TIME) / 120.0
    s = scale

    # body
    glColor3f(1.0, 0.6, 0.2)
    draw_rect(x, y, 0.13 * s, 0.10 * s)

    # head
    glColor3f(1.0, 0.62, 0.22)
    draw_circle(x + 0.065 * s, y + 0.145 * s, 0.055 * s)

    # ears
    glColor3f(1.0, 0.6, 0.2)
    glBegin(GL_TRIANGLES)
    glVertex2f(x + 0.025 * s, y + 0.185 * s)
    glVertex2f(x + 0.042 * s, y + 0.25 * s)
    glVertex2f(x + 0.065 * s, y + 0.185 * s)
    glVertex2f(x + 0.065 * s, y + 0.185 * s)
    glVertex2f(x + 0.088 * s, y + 0.25 * s)
    glVertex2f(x + 0.105 * s, y + 0.185 * s)
    glEnd()

    # inner ears
    glColor3f(1.0, 0.75, 0.75)
    glBegin(GL_TRIANGLES)
    glVertex2f(x + 0.033 * s, y + 0.190 * s)
    glVertex2f(x + 0.046 * s, y + 0.238 * s)
    glVertex2f(x + 0.062 * s, y + 0.190 * s)
    glVertex2f(x + 0.068 * s, y + 0.190 * s)
    glVertex2f(x + 0.082 * s, y + 0.238 * s)
    glVertex2f(x + 0.097 * s, y + 0.190 * s)
    glEnd()

    # muzzle
    glColor3f(1.0, 0.85, 0.7)
    draw_ellipse(x + 0.065 * s, y + 0.132 * s, 0.025 * s, 0.018 * s)

    # eyes
    glColor3f(0, 0, 0)
    draw_circle(x + 0.047 * s, y + 0.155 * s, 0.009 * s)
    draw_circle(x + 0.083 * s, y + 0.155 * s, 0.009 * s)
    glColor3f(1, 1, 1)
    draw_circle(x + 0.050 * s, y + 0.158 * s, 0.003 * s)
    draw_circle(x + 0.086 * s, y + 0.158 * s, 0.003 * s)

    # nose
    glColor3f(1.0, 0.4, 0.5)
    draw_circle(x + 0.065 * s, y + 0.133 * s, 0.006 * s)

    # whiskers
    glColor3f(0.4, 0.3, 0.2)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(x + 0.065 * s, y + 0.133 * s); glVertex2f(x - 0.02 * s, y + 0.140 * s)
    glVertex2f(x + 0.065 * s, y + 0.133 * s); glVertex2f(x - 0.02 * s, y + 0.128 * s)
    glVertex2f(x + 0.065 * s, y + 0.133 * s); glVertex2f(x + 0.155 * s, y + 0.140 * s)
    glVertex2f(x + 0.065 * s, y + 0.133 * s); glVertex2f(x + 0.155 * s, y + 0.128 * s)
    glEnd()

    # tail
    glColor3f(1.0, 0.55, 0.15)
    tail_wave = math.sin(t * 0.8) * 0.02
    glLineWidth(3)
    glBegin(GL_LINE_STRIP)
    for i in range(10):
        tx = x - 0.03 * s - i * 0.01 * s
        ty = y + 0.05 * s + math.sin(i * 0.8 + t) * 0.015 * s + tail_wave
        glVertex2f(tx, ty)
    glEnd()
    glLineWidth(1)

    # legs
    glColor3f(0.9, 0.5, 0.15)
    if not jumping:
        lo = math.sin(t) * 0.013
        draw_ellipse(x + 0.03 * s, y - 0.008 * s + lo, 0.016 * s, 0.013 * s)
        draw_ellipse(x + 0.10 * s, y - 0.008 * s - lo, 0.016 * s, 0.013 * s)
        # paws
        glColor3f(1.0, 0.7, 0.5)
        draw_ellipse(x + 0.03 * s, y - 0.018 * s + lo, 0.012 * s, 0.008 * s)
        draw_ellipse(x + 0.10 * s, y - 0.018 * s - lo, 0.012 * s, 0.008 * s)
    else:
        glColor3f(0.9, 0.5, 0.15)
        draw_ellipse(x + 0.02 * s, y + 0.010 * s, 0.016 * s, 0.013 * s)
        draw_ellipse(x + 0.11 * s, y + 0.010 * s, 0.016 * s, 0.013 * s)
        glColor3f(1.0, 0.7, 0.5)
        draw_ellipse(x + 0.02 * s, y + 0.000 * s, 0.012 * s, 0.008 * s)
        draw_ellipse(x + 0.11 * s, y + 0.000 * s, 0.012 * s, 0.008 * s)

# ============================================================
# FLY DRAW
# ============================================================
def draw_fly(x, y, scale=1.0):
    t = glutGet(GLUT_ELAPSED_TIME) / 80.0
    s = scale
    # body
    glColor3f(0.1, 0.1, 0.1)
    draw_ellipse(x, y, 0.02 * s, 0.012 * s)
    # wings (light gray-blue, no alpha needed)
    glColor3f(0.65, 0.82, 0.92)
    wing_flap = math.sin(t * 3) * 0.008
    draw_ellipse(x - 0.025 * s, y + 0.01 * s + wing_flap, 0.022 * s, 0.008 * s)
    draw_ellipse(x + 0.025 * s, y + 0.01 * s - wing_flap, 0.022 * s, 0.008 * s)
    # eyes
    glColor3f(0.9, 0.1, 0.1)
    draw_circle(x - 0.007 * s, y + 0.005 * s, 0.004 * s)
    draw_circle(x + 0.007 * s, y + 0.005 * s, 0.004 * s)

# ============================================================
# COSMIC SPLASH BACKGROUND
# ============================================================
_stars_splash = [(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.002, 0.007)) for _ in range(300)]
_nebula_blobs = [(random.uniform(-0.8, 0.8), random.uniform(-0.6, 0.6),
                  random.uniform(0.08, 0.22),
                  random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) for _ in range(18)]

def draw_cosmic_background():
    # deep space gradient (manual quads)
    glBegin(GL_QUADS)
    glColor3f(0.01, 0.00, 0.05); glVertex2f(-1, -1); glVertex2f(1, -1)
    glColor3f(0.04, 0.00, 0.12); glVertex2f(1, 1);   glVertex2f(-1, 1)
    glEnd()

    # nebula blobs (use dim glColor3f instead of alpha)
    for bx, by, br, r, g, b in _nebula_blobs:
        glColor3f(r * 0.15, g * 0.08, b * 0.22)
        draw_circle(bx, by, br, 32)

    # stars
    glPointSize(2)
    glBegin(GL_POINTS)
    t = glutGet(GLUT_ELAPSED_TIME) / 2000.0
    for sx, sy, sr in _stars_splash:
        brightness = 0.5 + 0.5 * math.sin(t + sx * 10)
        glColor3f(brightness, brightness, brightness)
        glVertex2f(sx, sy)
    glEnd()
    glPointSize(1)

    # distant galaxy smear
    glColor3f(0.12, 0.05, 0.20)
    draw_ellipse(0.3, 0.2, 0.5, 0.15, 64)
    glColor3f(0.05, 0.08, 0.20)
    draw_ellipse(-0.4, -0.1, 0.4, 0.12, 64)

# ============================================================
# JUNGLE BACKGROUND (layered silhouettes, looping)
# ============================================================
_scroll_jungle = 0.0

def draw_jungle_bg():
    global _scroll_jungle
    # sky gradient proper 4-vertex quad
    glBegin(GL_QUADS)
    glColor3f(0.53, 0.81, 0.98); glVertex2f(-1, -1)
    glColor3f(0.53, 0.81, 0.98); glVertex2f( 1, -1)
    glColor3f(0.20, 0.55, 0.85); glVertex2f( 1,  1)
    glColor3f(0.20, 0.55, 0.85); glVertex2f(-1,  1)
    glEnd()

    # sun (no alpha needed)
    glColor3f(1.0, 0.95, 0.5)
    draw_circle(0.7, 0.7, 0.13)
    glColor3f(1.0, 0.98, 0.60)
    draw_circle(0.7, 0.7, 0.08)

    # distant hills (lightest green)
    glColor3f(0.45, 0.72, 0.35)
    _draw_hill_layer(-0.30, 0.45, 0.6, _scroll_jungle * 0.1)

    # mid-ground trees (medium green)
    glColor3f(0.22, 0.52, 0.18)
    _draw_tree_layer(-0.30, 0.55, 0.38, _scroll_jungle * 0.3, density=14)

    # foreground ferns / dark trees
    glColor3f(0.06, 0.28, 0.06)
    _draw_tree_layer(-0.70, 0.70, 0.32, _scroll_jungle * 0.6, density=10, tall=True)

    # ground
    glColor3f(0.18, 0.62, 0.10)
    draw_rect(-1, -0.80, 2, 0.12)
    glColor3f(0.10, 0.45, 0.06)
    draw_rect(-1, -0.82, 2, 0.04)

def _draw_hill_layer(base_y, amplitude, freq, scroll):
    glBegin(GL_POLYGON)
    glVertex2f(-1.1, -0.85)
    steps = 80
    for i in range(steps + 1):
        fx = -1.1 + i * 2.2 / steps
        fy = base_y + amplitude * 0.18 * math.sin((fx + scroll) * freq * math.pi)
        glVertex2f(fx, fy)
    glVertex2f(1.1, -0.85)
    glEnd()

def _draw_tree_layer(base_y, height, width, scroll, density=12, tall=False):
    for i in range(density + 2):
        tx = -1.2 + (i / density) * 2.8 + (scroll % (2.8 / density))
        tx = ((tx + 1.2) % 2.8) - 1.2
        h = height * (0.85 + 0.3 * math.sin(i * 2.3))
        w = width * (0.7 + 0.3 * math.sin(i * 1.7))
        if tall:
            # palm-like
            _draw_palm_silhouette(tx, base_y, h, w)
        else:
            # canopy circle tree
            draw_ellipse(tx, base_y + h * 0.5, w * 0.5, h * 0.55, 24)
            draw_rect(tx - 0.018, base_y, 0.036, h * 0.4)

def _draw_palm_silhouette(x, base_y, h, w):
    # trunk
    glBegin(GL_QUADS)
    glVertex2f(x - 0.015, base_y)
    glVertex2f(x + 0.015, base_y)
    glVertex2f(x + 0.025, base_y + h)
    glVertex2f(x - 0.010, base_y + h)
    glEnd()
    # fronds
    for angle in [-0.9, -0.4, 0.0, 0.4, 0.9]:
        glBegin(GL_TRIANGLES)
        glVertex2f(x, base_y + h)
        glVertex2f(x + math.cos(angle + 1.5) * w * 0.8, base_y + h + math.sin(angle + 1.5) * h * 0.35)
        glVertex2f(x + math.cos(angle + 1.5) * w * 0.3, base_y + h + math.sin(angle + 1.5) * h * 0.15)
        glEnd()

# ============================================================
# ICE KINGDOM BACKGROUND
# ============================================================
_scroll_ice = 0.0
_ice_stars = [(random.uniform(-1, 1), random.uniform(-0.1, 1.0), random.uniform(0.002, 0.005)) for _ in range(200)]

def draw_ice_bg():
    # sky dark teal to navy - single proper quad
    glBegin(GL_QUADS)
    glColor3f(0.00, 0.10, 0.20); glVertex2f(-1, -1)
    glColor3f(0.00, 0.10, 0.20); glVertex2f( 1, -1)
    glColor3f(0.01, 0.12, 0.25); glVertex2f( 1,  1)
    glColor3f(0.01, 0.12, 0.25); glVertex2f(-1,  1)
    glEnd()

    # stars
    glPointSize(2)
    glBegin(GL_POINTS)
    t = glutGet(GLUT_ELAPSED_TIME) / 3000.0
    for sx, sy, sr in _ice_stars:
        b = 0.6 + 0.4 * math.sin(t + sx * 8)
        glColor3f(b, b, b + 0.1)
        glVertex2f(sx, sy)
    glEnd()
    glPointSize(1)

    # aurora hint (use glColor3f - blend already enabled globally)
    glColor3f(0.10, 0.55, 0.45)
    draw_ellipse(-0.2, 0.6, 0.9, 0.08, 48)
    glColor3f(0.15, 0.30, 0.65)
    draw_ellipse(0.4, 0.55, 0.6, 0.06, 48)

    # distant mountains (dark gray-blue silhouette)
    glColor3f(0.12, 0.18, 0.28)
    _draw_ice_mountains(_scroll_ice * 0.08)

    # mountain ice caps (white-blue)
    glColor3f(0.80, 0.88, 1.00)
    _draw_ice_caps(_scroll_ice * 0.08)

    # snowy ground
    glColor3f(0.65, 0.80, 0.98)
    draw_rect(-1, -0.82, 2, 0.14)
    glColor3f(0.90, 0.95, 1.00)
    draw_rect(-1, -0.72, 2, 0.03)
    # snow bumps
    for i in range(12):
        bx = -1.0 + i * 0.18 + (_scroll_ice * 0.5 % 0.18)
        glColor3f(0.95, 0.98, 1.0)
        draw_ellipse(bx, -0.72, 0.06, 0.02, 20)

def _draw_ice_mountains(scroll):
    peaks = [(-0.9,0.35),(-0.6,0.60),(-0.3,0.42),(0.0,0.72),(0.3,0.50),(0.6,0.65),(0.9,0.38),(1.2,0.55)]
    glBegin(GL_POLYGON)
    glVertex2f(-1.1, -0.20)
    for px, ph in peaks:
        ox = ((px - scroll) % 2.4) - 1.2
        glVertex2f(ox - 0.18, -0.20)
        glVertex2f(ox, ph)
        glVertex2f(ox + 0.18, -0.20)
    glVertex2f(1.1, -0.20)
    glEnd()

def _draw_ice_caps(scroll):
    peaks = [(-0.9,0.35),(-0.6,0.60),(-0.3,0.42),(0.0,0.72),(0.3,0.50),(0.6,0.65),(0.9,0.38),(1.2,0.55)]
    for px, ph in peaks:
        ox = ((px - scroll) % 2.4) - 1.2
        glBegin(GL_TRIANGLES)
        glVertex2f(ox - 0.07, ph - 0.12)
        glVertex2f(ox, ph)
        glVertex2f(ox + 0.07, ph - 0.12)
        glEnd()

# ============================================================
# UNDERGROUND BACKGROUND
# ============================================================
_scroll_ug = 0.0

def draw_underground_bg():
    # deep cave black-purple proper quad
    glBegin(GL_QUADS)
    glColor3f(0.04, 0.01, 0.10); glVertex2f(-1, -1)
    glColor3f(0.04, 0.01, 0.10); glVertex2f( 1, -1)
    glColor3f(0.08, 0.02, 0.18); glVertex2f( 1,  1)
    glColor3f(0.08, 0.02, 0.18); glVertex2f(-1,  1)
    glEnd()

    # distant crystals (light purple)
    glColor3f(0.50, 0.25, 0.70)
    _draw_crystal_layer(-0.65, 0.30, _scroll_ug * 0.12, size=0.08)

    # mid crystals (pink-purple)
    glColor3f(0.80, 0.20, 0.65)
    _draw_crystal_layer(-0.68, 0.45, _scroll_ug * 0.30, size=0.12)

    # foreground crystals teal/blue-purple
    glColor3f(0.10, 0.75, 0.70)
    _draw_crystal_layer(-0.72, 0.60, _scroll_ug * 0.55, size=0.16)
    glColor3f(0.20, 0.35, 0.85)
    _draw_crystal_layer(-0.72, 0.55, _scroll_ug * 0.58 + 0.5, size=0.14)

    # stalactites from ceiling
    glColor3f(0.15, 0.05, 0.30)
    _draw_stalactites(_scroll_ug * 0.4)

    # floor rocks
    glColor3f(0.12, 0.05, 0.22)
    draw_rect(-1, -0.85, 2, 0.18)

    # rail line
    glColor3f(0.55, 0.45, 0.35)
    draw_rect(-1, -0.705, 2, 0.012)  # top rail
    draw_rect(-1, -0.730, 2, 0.012)  # bottom rail
    # sleepers
    for i in range(20):
        sx = -1.05 + i * 0.12 + (_scroll_ug % 0.12)
        glColor3f(0.40, 0.28, 0.18)
        draw_rect(sx, -0.738, 0.07, 0.038)

    # floor surface
    glColor3f(0.18, 0.08, 0.32)
    draw_rect(-1, -0.695, 2, 0.008)

def _draw_crystal_layer(base_y, height, scroll, size=0.1):
    count = 16
    for i in range(count + 2):
        cx = -1.2 + (i / count) * 2.8 + (scroll % (2.8 / count))
        cx = ((cx + 1.2) % 2.8) - 1.2
        h = height * (0.7 + 0.5 * math.sin(i * 2.1))
        w = size * (0.6 + 0.4 * math.sin(i * 1.5))
        # angular crystal spike
        glBegin(GL_TRIANGLES)
        glVertex2f(cx - w * 0.5, base_y)
        glVertex2f(cx, base_y + h)
        glVertex2f(cx + w * 0.5, base_y)
        glEnd()
        glBegin(GL_TRIANGLES)
        glVertex2f(cx - w * 0.3, base_y)
        glVertex2f(cx + w * 0.1, base_y + h * 0.7)
        glVertex2f(cx + w * 0.6, base_y)
        glEnd()

def _draw_stalactites(scroll):
    count = 14
    for i in range(count + 2):
        sx = -1.2 + (i / count) * 2.8 + (scroll % (2.8 / count))
        sx = ((sx + 1.2) % 2.8) - 1.2
        h = 0.12 + 0.10 * math.sin(i * 1.9)
        w = 0.04 + 0.03 * math.sin(i * 2.3)
        glBegin(GL_TRIANGLES)
        glVertex2f(sx - w, 1.0)
        glVertex2f(sx + w, 1.0)
        glVertex2f(sx, 1.0 - h)
        glEnd()

# ============================================================
# OBSTACLE DRAWING
# ============================================================
def draw_obstacle(obs):
    ox, oy, ow, oh, otype = obs[0], obs[1], obs[2], obs[3], obs[4]
    level = selected_level

    if otype == 0:  # log
        if level == 0:    glColor3f(0.55, 0.30, 0.10)
        elif level == 1:  glColor3f(0.82, 0.88, 0.95)
        else:             glColor3f(0.40, 0.28, 0.16)
        draw_rect(ox, oy, ow, oh)
        # rings on log
        if level == 0:    glColor3f(0.65, 0.40, 0.15)
        elif level == 1:  glColor3f(0.70, 0.78, 0.88)
        else:             glColor3f(0.50, 0.36, 0.22)
        draw_ellipse(ox + ow * 0.5, oy + oh * 0.5, ow * 0.45, oh * 0.45, 24)
        if level == 1:
            # snow on top
            glColor3f(0.95, 0.98, 1.0)
            draw_rect(ox, oy + oh - 0.015, ow, 0.015)

    elif otype == 1:  # rock/stone
        if level == 0:    glColor3f(0.55, 0.50, 0.45)
        elif level == 1:  glColor3f(0.50, 0.60, 0.75)
        else:             glColor3f(0.38, 0.32, 0.48)
        draw_ellipse(ox + ow * 0.5, oy + oh * 0.45, ow * 0.5, oh * 0.5, 20)
        # highlight
        if level == 0:    glColor3f(0.70, 0.65, 0.60)
        elif level == 1:  glColor3f(0.70, 0.80, 0.92)
        else:             glColor3f(0.55, 0.48, 0.62)
        draw_ellipse(ox + ow * 0.38, oy + oh * 0.55, ow * 0.20, oh * 0.15, 16)

    elif otype == 2:  # mine / cactus / mine
        if level == 1:
            # ice cactus (blue-white spiky)
            glColor3f(0.70, 0.85, 1.00)
            draw_rect(ox + ow * 0.35, oy, ow * 0.30, oh)
            glColor3f(0.80, 0.92, 1.00)
            draw_rect(ox + ow * 0.10, oy + oh * 0.45, ow * 0.30, oh * 0.20)
            draw_rect(ox + ow * 0.60, oy + oh * 0.55, ow * 0.30, oh * 0.20)
            glColor3f(0.55, 0.75, 0.95)
            # spines
            for si in range(5):
                sx2 = ox + ow * 0.35 + si * ow * 0.06
                glBegin(GL_TRIANGLES)
                glVertex2f(sx2, oy + oh)
                glVertex2f(sx2 + ow * 0.04, oy + oh + 0.03)
                glVertex2f(sx2 + ow * 0.08, oy + oh)
                glEnd()
        else:
            # mine bomb
            glColor3f(0.15, 0.15, 0.15)
            draw_circle(ox + ow * 0.5, oy + oh * 0.55, ow * 0.45)
            glColor3f(0.30, 0.30, 0.30)
            draw_circle(ox + ow * 0.5, oy + oh * 0.6, ow * 0.25)
            # fuse
            glColor3f(0.60, 0.40, 0.10)
            glLineWidth(2)
            glBegin(GL_LINE_STRIP)
            for fi in range(8):
                fx = ox + ow * 0.5 + math.sin(fi * 0.9) * 0.012
                fy = oy + oh * 0.95 + fi * 0.01
                glVertex2f(fx, fy)
            glEnd()
            glLineWidth(1)
            # spark
            t = glutGet(GLUT_ELAPSED_TIME) / 100.0
            glColor3f(1.0, 0.8 + 0.2 * math.sin(t * 5), 0.0)
            draw_circle(ox + ow * 0.5 + math.sin(t) * 0.01, oy + oh + 0.025, 0.008)
            # skull
            glColor3f(0.9, 0.9, 0.9)
            draw_circle(ox + ow * 0.5, oy + oh * 0.58, ow * 0.18)
            glColor3f(0.15, 0.15, 0.15)
            draw_circle(ox + ow * 0.42, oy + oh * 0.60, ow * 0.05)
            draw_circle(ox + ow * 0.58, oy + oh * 0.60, ow * 0.05)

# ============================================================
# COIN DRAWING
# ============================================================
def draw_coin(coin):
    cx, cy, cr = coin[0], coin[1], coin[2]
    t = glutGet(GLUT_ELAPSED_TIME) / 300.0
    squeeze = abs(math.cos(t + cx * 3))
    glColor3f(1.0, 0.85, 0.0)
    draw_ellipse(cx, cy, cr * (0.3 + squeeze * 0.7), cr)
    glColor3f(1.0, 0.95, 0.4)
    draw_ellipse(cx, cy, cr * (0.15 + squeeze * 0.4), cr * 0.7)

# ============================================================
# STAR DRAW
# ============================================================
def draw_star_item(star):
    sx, sy = star[0], star[1]
    t = glutGet(GLUT_ELAPSED_TIME) / 200.0
    scale = 1.0 + 0.15 * math.sin(t * 3)
    glColor3f(1.0, 0.95, 0.2)
    draw_star_shape(sx, sy, 0.045 * scale, 0.020 * scale)
    glColor3f(1.0, 1.0, 0.6)
    draw_star_shape(sx, sy, 0.025 * scale, 0.010 * scale)

# ============================================================
# EXPLOSION EFFECT
# ============================================================
explosions = []

def spawn_explosion(x, y):
    explosions.append({'x': x, 'y': y, 'timer': 0, 'particles': [
        {'angle': random.uniform(0, math.pi * 2), 'speed': random.uniform(0.02, 0.07), 'life': random.uniform(0.5, 1.0)}
        for _ in range(20)
    ]})

def draw_explosions():
    to_remove = []
    for exp in explosions:
        exp['timer'] += 1
        if exp['timer'] > 40:
            to_remove.append(exp)
            continue
        alpha = 1.0 - exp['timer'] / 40.0
        for p in exp['particles']:
            age = exp['timer'] / 40.0
            px = exp['x'] + math.cos(p['angle']) * p['speed'] * exp['timer']
            py = exp['y'] + math.sin(p['angle']) * p['speed'] * exp['timer'] - 0.003 * exp['timer'] ** 1.5
            r = 0.006 * p['life'] * (1 - age * 0.5)
            glColor3f(1.0, 0.5 * (1 - age), 0.0)
            draw_circle(px, py, max(r, 0.002))
    for e in to_remove:
        explosions.remove(e)

# ============================================================
# RAIN
# ============================================================
def update_rain():
    global rain_drops, rain_active, rain_timer
    rain_timer += 1
    if not rain_active and rain_timer > random.randint(300, 700):
        rain_active = True
        rain_timer = 0
        rain_drops = [[random.uniform(-1, 1), random.uniform(-0.5, 1.0)] for _ in range(60)]
    if rain_active:
        for drop in rain_drops:
            drop[1] -= 0.018
            if drop[1] < -0.82:
                drop[0] = random.uniform(-1, 1)
                drop[1] = random.uniform(0.8, 1.2)
        if rain_timer > 200:
            rain_active = False
            rain_timer = 0
            rain_drops = []

def draw_rain():
    if not rain_active:
        return
    glColor3f(0.5, 0.7, 1.0)   # no alpha needed, just lighter blue
    glLineWidth(1.2)
    glBegin(GL_LINES)
    for drop in rain_drops:
        glVertex2f(drop[0], drop[1])
        glVertex2f(drop[0] - 0.005, drop[1] - 0.04)
    glEnd()
    glLineWidth(1)

# ============================================================
# INIT LEVEL
# ============================================================
def init_level():
    global cat_x, cat_y, velocity_y, jumping, jump_count
    global score, injury_count, game_over_flag, speed, speed_timer
    global obstacles, coins, stars, explosions
    global rain_drops, rain_active, rain_timer
    global _scroll_jungle, _scroll_ice, _scroll_ug

    cat_x = -0.65
    cat_y = ground_y
    velocity_y = 0.0
    jumping = False
    jump_count = 0
    score = 0
    injury_count = 0
    game_over_flag = False
    speed = 0.010
    speed_timer = 0
    rain_drops = []
    rain_active = False
    rain_timer = 0
    explosions.clear()
    stars.clear()
    _scroll_jungle = 0.0
    _scroll_ice = 0.0
    _scroll_ug = 0.0

    # spawn obstacles (type: 0=log, 1=rock, 2=mine/cactus)
    obstacles = []
    types = [0, 1, 2]
    xs = [1.0, 1.6, 2.3, 2.9]
    for i, x in enumerate(xs):
        t = types[i % 3]
        if t == 0:     ow, oh = 0.09, 0.14
        elif t == 1:   ow, oh = 0.10, 0.12
        else:          ow, oh = 0.08, 0.16
        obstacles.append([x, ground_y - oh + 0.10, ow, oh, t])

    coins = []
    for i in range(3):
        coins.append([1.2 + i * 0.8, random.uniform(-0.40, 0.20), 0.035])

# ============================================================
# COLLISION
# ============================================================
def collide_rect_cat(px, py, ox, oy, ow, oh):
    margin = 0.015
    return (
        px + 0.13 - margin > ox + margin and
        px + margin < ox + ow - margin and
        py + 0.20 - margin > oy + margin and
        py + margin < oy + oh - margin
    )

def collide_coin_cat(px, py, cx, cy, r):
    dx = (px + 0.065) - cx
    dy = (py + 0.08)  - cy
    return dx * dx + dy * dy < (r + 0.065) ** 2

def collide_star_cat(px, py, sx, sy):
    dx = (px + 0.065) - sx
    dy = (py + 0.08)  - sy
    return dx * dx + dy * dy < (0.07) ** 2

# ============================================================
# SPLASH SCREEN
# ============================================================
def draw_splash():
    draw_cosmic_background()
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    # title glow ring
    glColor3f(0.25, 0.12, 0.50)
    draw_circle(0, 0.20, 0.35, 64)

    # cat character (large)
    cat_bob = math.sin(t * 1.5) * 0.03
    draw_cat(-0.085, 0.00 + cat_bob, scale=1.6)

    # MINILEAP title
    glColor3f(1.0, 0.90, 0.20)
    draw_text(-0.38, 0.70, "M I N I L E A P", GLUT_BITMAP_TIMES_ROMAN_24)

    # subtitle
    glColor3f(0.80, 0.70, 1.00)
    draw_text_centered(0.58, "The Cosmic Cat Adventure", GLUT_BITMAP_HELVETICA_18)

    # stars around title
    for i in range(8):
        angle = t * 0.5 + i * math.pi / 4
        sx2 = 0.42 * math.cos(angle)
        sy2 = 0.65 + 0.08 * math.sin(angle * 2)
        glColor3f(1.0, 0.9, 0.3)
        draw_star_shape(sx2, sy2, 0.018, 0.008)

    # press space prompt (blinking)
    if int(t * 2) % 2 == 0:
        glColor3f(0.9, 0.9, 1.0)
        draw_text_centered(-0.82, "Press SPACE to Continue", GLUT_BITMAP_HELVETICA_18)

    # version
    glColor3f(0.4, 0.4, 0.6)
    draw_text(-0.98, -0.95, "MiniLeap v1.0  |  Magnific Studios Style", GLUT_BITMAP_HELVETICA_12)

# ============================================================
# STORY SCREEN
# ============================================================
def draw_story():
    global story_phase, story_timer, fly_x, fly_y, fly_dir, current_screen

    draw_cosmic_background()
    # floor
    glColor3f(0.18, 0.62, 0.10)
    draw_rect(-1, -0.80, 2, 0.15)

    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    story_timer += 1

    if story_phase == 0:
        # cat sleeping on floor
        draw_cat(-0.08, -0.70, scale=1.2)
        # zzz
        glColor3f(0.8, 0.8, 1.0)
        draw_text(0.10, -0.40, "z", GLUT_BITMAP_HELVETICA_18)
        draw_text(0.16, -0.34, "z", GLUT_BITMAP_HELVETICA_18)
        draw_text(0.23, -0.27, "Z", GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(1, 1, 1)
        draw_text_centered(-0.92, "MiniLeap is peacefully napping...", GLUT_BITMAP_HELVETICA_18)
        if story_timer > 160:
            story_phase = 1
            story_timer = 0
            fly_x = 0.30
            fly_y = -0.42

    elif story_phase == 1:
        # cat + fly buzzing
        draw_cat(-0.08, -0.70, scale=1.2)
        # annoyed face - red eyes
        glColor3f(1, 0.2, 0.2)
        draw_circle(-0.03, -0.58, 0.008)
        draw_circle(0.03, -0.58, 0.008)
        fly_x += 0.006 * math.sin(t * 5) * fly_dir
        fly_y += 0.003 * math.cos(t * 4)
        fly_y = clamp(fly_y, -0.50, -0.30)
        draw_fly(fly_x, fly_y, scale=1.5)
        glColor3f(1, 0.8, 0.2)
        draw_text(-0.12, -0.20, "BZZZ!", GLUT_BITMAP_HELVETICA_18)
        glColor3f(1, 1, 1)
        draw_text_centered(-0.92, "A fly is disturbing MiniLeap's nap!", GLUT_BITMAP_HELVETICA_18)
        if story_timer > 180:
            story_phase = 2
            story_timer = 0

    elif story_phase == 2:
        # cat chasing fly running
        run_offset = (story_timer * 0.008) % 0.4 - 0.3
        draw_cat(-0.5 + run_offset * 3, -0.70, scale=1.2)
        fly_x = -0.2 + run_offset * 3.5
        fly_y = -0.42 + math.sin(story_timer * 0.15) * 0.08
        draw_fly(fly_x, fly_y, scale=1.5)
        glColor3f(1, 1, 1)
        draw_text_centered(-0.92, "MiniLeap chases the fly through the world!", GLUT_BITMAP_HELVETICA_18)
        if story_timer > 220:
            story_phase = 0
            story_timer = 0
            current_screen = SCREEN_INSTRUCTIONS
            return

    # skip
    glColor3f(0.55, 0.55, 0.75)
    draw_text(0.62, -0.93, "SPACE to skip", GLUT_BITMAP_HELVETICA_12)

# ============================================================
# INSTRUCTIONS SCREEN
# ============================================================
def draw_instructions():
    draw_cosmic_background()
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    glColor3f(1.0, 0.90, 0.20)
    draw_text(-0.28, 0.78, "HOW TO PLAY", GLUT_BITMAP_TIMES_ROMAN_24)

    # cat jumping demo
    bob = math.sin(t * 2) * 0.06
    draw_cat(-0.10, -0.20 + bob, scale=1.3)
    if bob > 0.02:
        pass  # jumping visually

    # instruction cards
    _draw_card(-0.90, 0.50, 0.80, 0.20)
    glColor3f(0.2, 0.9, 0.3)
    draw_text(-0.84, 0.64, "JUMP", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.9, 0.9, 0.9)
    draw_text(-0.84, 0.54, "Press  SPACE", GLUT_BITMAP_HELVETICA_18)

    _draw_card(-0.90, 0.22, 0.80, 0.20)
    glColor3f(0.3, 0.6, 1.0)
    draw_text(-0.84, 0.36, "DOUBLE JUMP", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.9, 0.9, 0.9)
    draw_text(-0.84, 0.26, "Press SPACE twice in air", GLUT_BITMAP_HELVETICA_18)

    _draw_card(-0.90, -0.08, 0.80, 0.22)
    glColor3f(1.0, 0.7, 0.2)
    draw_text(-0.84, 0.08, "COLLECT", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(1.0, 0.85, 0.0)
    draw_coin([-0.80, -0.03, 0.03])
    glColor3f(0.9, 0.9, 0.9)
    draw_text(-0.72, -0.02, "Coins = +1 Score", GLUT_BITMAP_HELVETICA_18)
    glColor3f(1.0, 0.95, 0.2)
    draw_star_item([-0.80, -0.14])
    glColor3f(0.9, 0.9, 0.9)
    draw_text(-0.72, -0.14, "Star = -1 Injury", GLUT_BITMAP_HELVETICA_18)

    _draw_card(-0.90, -0.38, 0.80, 0.22)
    glColor3f(1.0, 0.3, 0.3)
    draw_text(-0.84, -0.22, "DANGER", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.9, 0.9, 0.9)
    draw_text(-0.84, -0.32, "3 injuries = Game Over", GLUT_BITMAP_HELVETICA_18)
    draw_text(-0.84, -0.44, "Mine/Cactus = Instant Death!", GLUT_BITMAP_HELVETICA_12)

    # injury hearts display
    glColor3f(1.0, 0.3, 0.3)
    for i in range(3):
        draw_heart(0.30 + i * 0.12, 0.10)

    if int(t * 2) % 2 == 0:
        glColor3f(0.9, 0.9, 1.0)
        draw_text_centered(-0.88, "Press SPACE to Choose Your World!", GLUT_BITMAP_HELVETICA_18)

def _draw_card(x, y, w, h):
    glColor3f(0.08, 0.06, 0.20)
    draw_rect(x, y, w, h)
    glColor3f(0.35, 0.25, 0.65)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y); glVertex2f(x + w, y)
    glVertex2f(x + w, y + h); glVertex2f(x, y + h)
    glEnd()
    glLineWidth(1)

def draw_heart(cx, cy):
    # simple heart
    glBegin(GL_POLYGON)
    for i in range(100):
        t = 2 * math.pi * i / 100
        hx = cx + 0.022 * (16 * math.sin(t) ** 3) / 16
        hy = cy + 0.022 * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 16
        glVertex2f(hx, hy)
    glEnd()

# ============================================================
# MAIN MENU
# ============================================================
level_buttons = [
    (-0.75, -0.10, 0.40, 0.55),  # Jungle
    (-0.15, -0.10, 0.40, 0.55),  # Ice
    ( 0.45, -0.10, 0.40, 0.55),  # Underground
]
level_names    = ["Jungle", "Ice Kingdom", "Underground"]
level_subtitles= ["Tropical Adventure", "Frozen Tundra", "Crystal Cavern"]

def draw_main_menu():
    draw_cosmic_background()
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    glColor3f(1.0, 0.90, 0.20)
    draw_text(-0.35, 0.82, "SELECT YOUR WORLD", GLUT_BITMAP_TIMES_ROMAN_24)

    glColor3f(0.70, 0.70, 1.00)
    draw_text_centered(0.72, "Click a world to begin your adventure!", GLUT_BITMAP_HELVETICA_18)

    # level cards
    colors = [
        (0.08, 0.35, 0.08),   # jungle green
        (0.05, 0.15, 0.35),   # ice blue
        (0.15, 0.05, 0.30),   # underground purple
    ]
    border_colors = [
        (0.20, 0.80, 0.20),
        (0.40, 0.80, 1.00),
        (0.70, 0.30, 1.00),
    ]
    preview_fn = [_preview_jungle, _preview_ice, _preview_underground]

    for i, (bx, by, bw, bh) in enumerate(level_buttons):
        # card bg
        glColor3f(*colors[i])
        draw_rect(bx, by, bw, bh)

        # animated border
        pulse = 0.5 + 0.5 * math.sin(t * 2 + i * 1.2)
        bc = border_colors[i]
        glColor3f(bc[0] * pulse, bc[1] * pulse, bc[2] * pulse)
        glLineWidth(2.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bx, by); glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh); glVertex2f(bx, by + bh)
        glEnd()
        glLineWidth(1)

        # mini preview
        preview_fn[i](bx + bw * 0.5, by + bh * 0.62, 0.17)

        # level number
        glColor3f(*border_colors[i])
        draw_text(bx + 0.03, by + bh - 0.05, f"{i + 1}.", GLUT_BITMAP_TIMES_ROMAN_24)

        # name
        glColor3f(1, 1, 1)
        name_w = len(level_names[i]) * 0.009
        draw_text(bx + bw / 2 - name_w, by + 0.18, level_names[i], GLUT_BITMAP_TIMES_ROMAN_24)

        # subtitle
        glColor3f(0.75, 0.85, 0.75 if i == 0 else (0.85 if i == 1 else 0.80))
        sub_w = len(level_subtitles[i]) * 0.0075
        draw_text(bx + bw / 2 - sub_w, by + 0.08, level_subtitles[i], GLUT_BITMAP_HELVETICA_12)

    # mini cat walking across bottom
    cx = -1.0 + (t * 0.25) % 2.2
    draw_cat(cx, -0.88, scale=0.8)

def _preview_jungle(cx, cy, r):
    # mini tree silhouettes
    glColor3f(0.10, 0.45, 0.10)
    draw_circle(cx, cy, r * 0.7, 20)
    glColor3f(0.06, 0.30, 0.06)
    draw_circle(cx - r * 0.5, cy - r * 0.15, r * 0.5, 16)
    draw_circle(cx + r * 0.5, cy - r * 0.15, r * 0.5, 16)
    glColor3f(0.18, 0.60, 0.10)
    draw_rect(cx - r * 0.80, cy - r * 1.1, r * 1.6, r * 0.25)

def _preview_ice(cx, cy, r):
    # mini mountain
    glColor3f(0.12, 0.20, 0.35)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx - r * 0.8, cy - r * 0.8)
    glVertex2f(cx, cy + r * 0.6)
    glVertex2f(cx + r * 0.8, cy - r * 0.8)
    glEnd()
    glColor3f(0.85, 0.93, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx - r * 0.25, cy + r * 0.25)
    glVertex2f(cx, cy + r * 0.6)
    glVertex2f(cx + r * 0.25, cy + r * 0.25)
    glEnd()
    glColor3f(0.65, 0.80, 0.98)
    draw_rect(cx - r * 0.80, cy - r * 0.85, r * 1.6, r * 0.18)

def _preview_underground(cx, cy, r):
    glColor3f(0.10, 0.60, 0.60)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx - r * 0.5, cy - r * 0.6)
    glVertex2f(cx - r * 0.2, cy + r * 0.4)
    glVertex2f(cx + r * 0.1, cy - r * 0.6)
    glEnd()
    glColor3f(0.70, 0.15, 0.60)
    glBegin(GL_TRIANGLES)
    glVertex2f(cx + r * 0.1, cy - r * 0.6)
    glVertex2f(cx + r * 0.3, cy + r * 0.2)
    glVertex2f(cx + r * 0.6, cy - r * 0.6)
    glEnd()
    glColor3f(0.18, 0.05, 0.32)
    draw_rect(cx - r * 0.80, cy - r * 0.80, r * 1.6, r * 0.22)

# ============================================================
# CONFIRM SCREEN
# ============================================================
def draw_confirm():
    draw_cosmic_background()
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    lvl_name = level_names[confirm_level] if confirm_level >= 0 else "?"

    # cat bounce
    bob = math.sin(t * 3) * 0.04
    draw_cat(-0.07, -0.15 + bob, scale=1.4)

    glColor3f(1.0, 0.90, 0.20)
    draw_text(-0.22, 0.60, lvl_name, GLUT_BITMAP_TIMES_ROMAN_24)

    glColor3f(0.9, 0.9, 1.0)
    draw_text_centered(0.38, "Are you Ready?", GLUT_BITMAP_TIMES_ROMAN_24)

    if int(t * 2) % 2 == 0:
        glColor3f(0.4, 1.0, 0.5)
        draw_text_centered(-0.75, "Press SPACE to Start!", GLUT_BITMAP_HELVETICA_18)

    glColor3f(0.6, 0.6, 0.8)
    draw_text_centered(-0.88, "Press M for Main Menu", GLUT_BITMAP_HELVETICA_12)

# ============================================================
# GAME SCREEN
# ============================================================
def draw_game():
    global _scroll_jungle, _scroll_ice, _scroll_ug

    # draw background
    if selected_level == 0:
        draw_jungle_bg()
        _scroll_jungle += speed * 0.8
    elif selected_level == 1:
        draw_ice_bg()
        _scroll_ice += speed * 0.8
    else:
        draw_underground_bg()
        _scroll_ug += speed * 0.8

    # rain for jungle
    if selected_level == 0:
        draw_rain()

    # obstacles
    for obs in obstacles:
        draw_obstacle(obs)

    # coins
    for coin in coins:
        draw_coin(coin)

    # stars
    for star in stars:
        draw_star_item(star)

    # explosions
    draw_explosions()

    # cat
    draw_cat(cat_x, cat_y)

    # HUD
    _draw_hud()

    if game_over_flag:
        _draw_game_over()

def _draw_hud():
    # score bg
    glColor3f(0.05, 0.05, 0.05)
    draw_rect(-1.0, 0.88, 0.46, 0.10)
    glColor3f(1.0, 0.90, 0.20)
    draw_text(-0.97, 0.92, f"Score: {score}", GLUT_BITMAP_HELVETICA_18)

    # injury hearts
    for i in range(3):
        if i < 3 - injury_count:
            glColor3f(1.0, 0.2, 0.2)
        else:
            glColor3f(0.3, 0.3, 0.3)
        draw_heart(0.62 + i * 0.13, 0.935)

    # speed indicator
    glColor3f(0.7, 0.7, 1.0)
    if speed < 0.016:   diff = "Easy"
    elif speed < 0.022: diff = "Medium"
    else:               diff = "Hard"
    draw_text(0.60, 0.88, diff, GLUT_BITMAP_HELVETICA_12)

    # level name
    glColor3f(0.8, 0.8, 1.0)
    draw_text(-0.97, 0.80, level_names[selected_level], GLUT_BITMAP_HELVETICA_12)

def _draw_game_over():
    # dark overlay
    glColor3f(0.04, 0.04, 0.04)
    draw_rect(-1, -1, 2, 2)

    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    glColor3f(1.0, 0.25, 0.25)
    draw_text(-0.30, 0.30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)

    glColor3f(1.0, 0.85, 0.10)
    draw_text_centered(0.08, f"Coins Collected: {score}", GLUT_BITMAP_HELVETICA_18)

    # coin display
    for i in range(min(score, 10)):
        draw_coin([-0.48 + i * 0.10, -0.05, 0.025])

    if int(t * 2) % 2 == 0:
        glColor3f(0.5, 1.0, 0.5)
        draw_text_centered(-0.30, "R  -  Restart", GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.5, 0.7, 1.0)
        draw_text_centered(-0.48, "SPACE  -  Main Menu", GLUT_BITMAP_HELVETICA_18)

# ============================================================
# DISPLAY CALLBACK
# ============================================================
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    if current_screen == SCREEN_SPLASH:
        draw_splash()
    elif current_screen == SCREEN_STORY:
        draw_story()
    elif current_screen == SCREEN_INSTRUCTIONS:
        draw_instructions()
    elif current_screen == SCREEN_MAIN_MENU:
        draw_main_menu()
    elif current_screen == SCREEN_CONFIRM:
        draw_confirm()
    elif current_screen == SCREEN_GAME:
        draw_game()
    elif current_screen == SCREEN_GAMEOVER:
        draw_game()   # draws game_over overlay on top of scene

    glutSwapBuffers()

# ============================================================
# UPDATE
# ============================================================
def update(value):
    global cat_y, velocity_y, jumping, jump_count
    global score, injury_count, game_over_flag
    global speed, speed_timer, current_screen
    global obstacles, coins, stars

    if current_screen == SCREEN_GAME and not game_over_flag:
        # physics
        velocity_y += gravity
        cat_y += velocity_y

        if cat_y <= ground_y:
            cat_y = ground_y
            velocity_y = 0
            jumping = False
            jump_count = 0

        speed_timer += 1
        if speed_timer % 400 == 0:
            speed = min(speed + 0.003, 0.030)

        # rain
        if selected_level == 0:
            update_rain()

        # obstacles
        to_respawn = []
        for obs in obstacles:
            obs[0] -= speed
            if obs[0] + obs[2] < -1.1:
                to_respawn.append(obs)
            else:
                if collide_rect_cat(cat_x, cat_y, obs[0], obs[1], obs[2], obs[3]):
                    otype = obs[4]
                    if otype == 2:  # mine / cactus = instant death
                        sound_dizzy.play()          # ← dizzy sound on bomb hit
                        spawn_explosion(obs[0] + obs[2] * 0.5, obs[1] + obs[3] * 0.5)
                        injury_count = 3
                    else:
                        injury_count += 1
                        spawn_explosion(obs[0] + obs[2] * 0.5, obs[1] + obs[3] * 0.5)
                        # spawn star after injury
                        if len(stars) == 0:
                            stars.append([cat_x + 0.5, random.uniform(-0.30, 0.10)])
                    obs[0] = 2.0  # push off screen immediately
                    if injury_count >= 3:
                        game_over_flag = True

        for obs in to_respawn:
            # random type weighted
            otype = random.choices([0, 1, 2], weights=[4, 4, 2])[0]
            if otype == 0:     ow, oh = 0.09, 0.14
            elif otype == 1:   ow, oh = 0.10, 0.12
            else:              ow, oh = 0.08, 0.16
            obs[0] = random.uniform(1.1, 1.8)
            obs[1] = ground_y - oh + 0.10
            obs[2] = ow
            obs[3] = oh
            obs[4] = otype

        # coins
        for coin in coins:
            coin[0] -= speed
            if coin[0] + coin[2] < -1.1:
                coin[0] = random.uniform(1.1, 2.0)
                coin[1] = random.uniform(-0.40, 0.20)
            elif collide_coin_cat(cat_x, cat_y, coin[0], coin[1], coin[2]):
                sound_coin.play()                   # ← coin collect sound
                score += 1
                coin[0] = random.uniform(1.1, 2.0)
                coin[1] = random.uniform(-0.40, 0.20)

        # stars
        for star in stars[:]:
            star[0] -= speed
            if star[0] < -1.2:
                stars.remove(star)
            elif collide_star_cat(cat_x, cat_y, star[0], star[1]):
                injury_count = max(0, injury_count - 1)
                stars.remove(star)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# ============================================================
# INPUT
# ============================================================
def keyboard(key, x, y):
    global jumping, velocity_y, jump_count
    global current_screen, game_over_flag
    global selected_level, confirm_level
    global story_phase, story_timer

    try:
        key = key.decode().lower()
    except Exception:
        return

    if current_screen == SCREEN_SPLASH:
        if key == ' ':
            current_screen = SCREEN_STORY
            story_phase = 0
            story_timer = 0

    elif current_screen == SCREEN_STORY:
        if key == ' ':
            current_screen = SCREEN_INSTRUCTIONS

    elif current_screen == SCREEN_INSTRUCTIONS:
        if key == ' ':
            current_screen = SCREEN_MAIN_MENU

    elif current_screen == SCREEN_MAIN_MENU:
        if key == '1':
            confirm_level = 0; current_screen = SCREEN_CONFIRM
        elif key == '2':
            confirm_level = 1; current_screen = SCREEN_CONFIRM
        elif key == '3':
            confirm_level = 2; current_screen = SCREEN_CONFIRM

    elif current_screen == SCREEN_CONFIRM:
        if key == ' ':
            selected_level = confirm_level
            init_level()
            current_screen = SCREEN_GAME
        elif key == 'm':
            current_screen = SCREEN_MAIN_MENU

    elif current_screen == SCREEN_GAME:
        if key == ' ':
            if game_over_flag:
                current_screen = SCREEN_MAIN_MENU
                game_over_flag = False
            elif jump_count < 2:
                if jump_count == 1:         # ← 2nd press = double jump → play sound
                    sound_jump.play()
                jumping = True
                velocity_y = jump_power
                jump_count += 1
        elif key == 'r' and game_over_flag:
            selected_level = confirm_level
            init_level()
            current_screen = SCREEN_GAME

def mouse_click(button, state, mx, my):
    global current_screen, confirm_level

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_screen == SCREEN_MAIN_MENU:
            # convert window coords to GL coords
            gl_x = (mx / WIN_W) * 2.0 - 1.0
            gl_y = 1.0 - (my / WIN_H) * 2.0

            for i, (bx, by, bw, bh) in enumerate(level_buttons):
                if bx <= gl_x <= bx + bw and by <= gl_y <= by + bh:
                    confirm_level = i
                    current_screen = SCREEN_CONFIRM
                    break

# ============================================================
# SETUP
# ============================================================
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WIN_W, WIN_H)
glutCreateWindow(b"MiniLeap - The Cosmic Cat Adventure")

glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_click)
glutReshapeFunc(reshape)
glutTimerFunc(16, update, 0)

glutMainLoop() 