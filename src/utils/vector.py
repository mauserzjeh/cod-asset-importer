from __future__ import annotations


from . import quaternion

class Vector3:
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: float | int) -> Vector3:
        rx = self.x * other
        ry = self.y * other
        rz = self.z * other

        return Vector3(rx, ry, rz)

    def __add__(self, other: Vector3) -> Vector3:
        rx = self.x + other.x
        ry = self.y + other.y
        rz = self.z + other.z

        return Vector3(rx, ry, rz)

    def __IADD__(self, other: Vector3):
        self.x += other.x
        self.y += other.y
        self.z += other.z

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.z)

    def rotate_by_quaternion(self, quaternion: quaternion.Quaternion) -> Vector3:
        u = Vector3(quaternion.x, quaternion.y, quaternion.z)
        s = quaternion.w

        return (u * (2.0 * self.dot(u))) + (self * (s * s - u.dot(u))) + (self.cross(u) * s * 2.0)

    def dot(self, other: Vector3) -> float:
        rx = self.x * other.x
        ry = self.y * other.y
        rz = self.z * other.z

        return (rx + ry + rz)
    
    def cross(self, other: Vector3) -> Vector3:
        vx = self.x
        vy = self.y
        vz = self.z

        ox = other.x
        oy = other.y
        oz = other.z

        rx = (oy * vz) - (oz * vy)
        ry = (oz * vx) - (ox * vz)
        rz = (ox * vy) - (oy * vx)

        return Vector3(rx, ry, rz)



