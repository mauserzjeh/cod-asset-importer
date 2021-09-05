from __future__ import annotations

import math

class Quaternion:

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = None) -> None:
        self.x = x
        self.y = y
        self.z = z

        if w == None:
            self.w = math.sqrt((1 - math.pow(self.x, 2) - math.pow(self.y, 2) - math.pow(self.z, 2)))
        else:
            self.w = w

    def __mul__(self, other: Quaternion) -> Quaternion:
        ax = self.x
        ay = self.y
        az = self.z
        aw = self.w
        
        bx = other.x
        by = other.y
        bz = other.z
        bw = other.w

        x = aw * bx + ax * bw + ay * bz - az * by
        y = aw * by - ax * bz + ay * bw + az * bx
        z = aw * bz + ax * by - ay * bx + az * bw 
        w = aw * bw - ax * bx - ay * by - az * bz

        return Quaternion(x, y, z, w)

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z, self.w)
