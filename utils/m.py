import numpy as np


def vec(a):
    return np.array(a)

def vec2(x, y):
    return np.array([x, y])

def vec3(x, y, z):
    return np.array([x, y, z])

def length(v):
    """Length (norm) of vector"""
    return np.linalg.norm(v)

def normalize(v):
    """Normalize vector such that length is 1"""
    return v / np.linalg.norm(v)

def unit(v):
    """Create a normalized vector from an array or list."""
    if isinstance(v, np.ndarray) is False:
        v = np.array(v)
    return np.linalg.norm(v)
