import math

"""
Fixes rotation of props
"""
def fix_rotation(x: float, y: float, z: float) -> tuple:
    return (z/2), x, y
