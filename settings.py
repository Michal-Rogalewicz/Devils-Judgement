#Game-wide constants - the control panel.

# Grid / window
TILE = 28
HUD_HEIGHT = 56
FPS = 60
TITLE = "Devils Judgement"

# Colours (R, G, B) 
BG_COLOR        = (12, 14, 28)
WALL_COLOR      = (212, 175, 84)
GATE_CLOSED     = (120, 100, 50)
GATE_OPEN       = (255, 240, 150)
DOT_COLOR       = (245, 245, 255)
HALO_COLOR      = (250, 230, 120)
SIN_COLOR       = (220, 70, 160)
DEVIL_COLOR     = (208, 48, 48)
HORN_COLOR      = (150, 30, 30)
EYE_COLOR       = (20, 20, 20)
ANGEL_COLOR     = (255, 255, 240)
ANGEL_HALO      = (240, 220, 120)
ANGEL_SCARED    = (90, 120, 235)
TEXT_COLOR      = (220, 220, 235)
DIM_TEXT        = (150, 150, 170)
WIN_COLOR       = (250, 240, 160)
LOSE_COLOR      = (220, 90, 90)

# Speeds
DEVIL_SPEED       = 6.0
ANGEL_SPEED       = 5.0
ANGEL_SCARED_SPEED = 3.0

# Scoring 
DOT_POINTS  = 10
HALO_POINTS = 50
SIN_POINTS  = 150     # big reward
REDEEM_POINTS = 100   # points for redeeming a scared angel

# Rules 
START_LIVES       = 3
HALO_DURATION     = 6.0    # seconds angels stay scared after a halo
SIN_PENALTY_ANGELS = 1     # extra angels spawned per sin (the catch)
MAX_ANGELS        = 6
REDEMPTION_FRACTION = 0.7  # collect this fraction of deeds to open the gate

# Angel mode cycling (classic scatter/chase rhythm)
SCATTER_TIME = 5.0
CHASE_TIME   = 18.0

# Game states
MENU    = "menu"
PLAYING = "playing"
PAUSED  = "paused"
WIN     = "win"
LOSE    = "lose"

# Angel modes
SCATTER    = "scatter"
CHASE      = "chase"
FRIGHTENED = "frightened"

# Movement directions (dx, dy)
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)
STOP  = (0, 0)