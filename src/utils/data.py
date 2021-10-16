import math

def fix_rotation(x: float, y: float, z: float) -> tuple:
    return (z/2), x, y

def normalize_color_data(color_data: bytes) -> list:
    return [i / 255 for i in color_data]

def bumpmap_to_normalmap(color_data: list) -> list:
    output = [0.0] * len(color_data)
    for i in range(0, len(color_data), 4):
        r = color_data[i]
        g = color_data[i + 1]
        b = color_data[i + 2]
        a = color_data[i + 3]

        nr = (a * 2.0 - 1.0) * 0.5 + 0.5
        ng = (r * 2.0 - 1.0) * 0.5 + 0.5
        nb = 1.0 - (nr * nr) - (ng * ng)
        nb = math.sqrt(nb) * 0.5 + 0.5 if nb > 0.0 else 0.0

        output[i] = nr
        output[i + 1] = 1.0 - ng
        output[i + 2] = nb
        output[i + 3] = 1.0

    return output

