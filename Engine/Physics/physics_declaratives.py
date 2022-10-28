from panda3d.core import Vec3

""" Horse Mounting parameters """
# X works as Y and Y works as X:
# Our horse (un)mounting animations have been made with imperfect positions,
# so, I had to change child positions to get more satisfactory result
# with these animations in my game.
mounting_pos = Vec3(0.6, -0.16, -0.41)
saddle_pos = Vec3(0, -0.32, 0.35)
