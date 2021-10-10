
def fix_rotation(x: float, y: float, z: float) -> tuple:
    return (z/2), x, y

def normalize_color_data(color_data: bytes) -> list:
    return [i / 255 for i in color_data]