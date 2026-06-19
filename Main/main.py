#Trespasser - a devil sneaks into heaven.

#Everything else lives in its own file:
    #settings.py  - all the tweakable numbers
    #maze.py      - the level (editable text layout) + pickups + the gate
    #entity.py    - Mover: the shared tile-to-tile movement
    #player.py    - Devil: you (keyboard controlled)
    #angel.py     - Angel: the hunters (chase / scatter / frightened AI)
    #game.py      - the rules, states, scoring and drawing


#from game import Game

from game import Game

if __name__ == "__main__":
    Game().run()