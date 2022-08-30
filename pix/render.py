import cv2
import numpy as numpy


def depth_line(depth, p0, p1, color=[255], th=1):
    pass

def line_2d(ima, p0, p1, color=[255,255,255], th=1):
    p0 = tuple(p0[0:2])
    p1 = tuple(p1[0:2])
    cv2.line(ima, p0, p1, color=color, thickness=th)

def line(ima, p0, p1, color=[255, 255, 255], th=1):
    """Render line in either 2d or 3d.

       p0, p1 (2d): draw single 2d line
       p0, p1 (3d): draw single 3d line, assumes ima is a depth image
       p0, p1 (2d) arrays: draw 2d polygon 

    """
    if len(p0) == 3:
        return depth_line(ima, p0, p1, color, th)
    else:
        return line_2d(ima, p0, p1, color, th)

def points(ima, pts, color=[255, 255, 255], th=2):
    for p in pts:
        center = tuple((int(p[0]), int(p[1])))
        if len(p) == 3:
            c = int(p[2])
            color = [c, c, c]
            # issue#1: force white for now, depth range is invalid
        cv2.circle(ima, center, th, color, -1)