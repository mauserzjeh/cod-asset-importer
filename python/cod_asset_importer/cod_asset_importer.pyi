from typing import List, Dict
import importer

class XMODEL_VERSION:
    V14: int
    V20: int
    V25: int
    V62: int

class GAME_VERSION:
    CoD: int
    CoD2: int
    CoD4: int
    CoD5: int
    CoDBO1: int

class TEXTURE_TYPE:
    Unused: int
    Color: int
    Normal: int
    Specular: int
    Roughness: int
    Detail: int

class Loader:
    def __init__(self, importer: importer.Importer) -> None: ...
    def import_bsp(self, asset_path: str, file_path: str) -> None: ...
    def import_xmodel(
        self,
        asset_path: str,
        file_path: str,
        selected_version: GAME_VERSION,
        angles: List[float],
        origin: List[float],
        scale: List[float],
    ) -> None: ...

class LoadedIbsp:
    def name(self) -> str: ...
    def surfaces(self) -> List[LoadedSurface]: ...

class LoadedModel:
    def name(self) -> str: ...
    def version(self) -> XMODEL_VERSION: ...
    def angles(self) -> List[float]: ...
    def origin(self) -> List[float]: ...
    def scale(self) -> List[float]: ...
    def materials(self) -> Dict[str, LoadedMaterial]: ...
    def surfaces(self) -> List[LoadedSurface]: ...
    def bones(self) -> List[LoadedBone]: ...

class LoadedMaterial:
    def name(self) -> str: ...
    def version(self) -> XMODEL_VERSION: ...
    def textures(self) -> List[LoadedTexture]: ...

class LoadedTexture:
    def name(self) -> str: ...
    def texture_type(self) -> TEXTURE_TYPE: ...
    def width(self) -> int: ...
    def height(self) -> int: ...
    def data(self) -> List[float]: ...

class LoadedSurface:
    def material(self) -> str: ...
    def vertices(self) -> List[float]: ...
    def normals(self) -> List[List[float]]: ...
    def colors(self) -> List[float]: ...
    def uvs(self) -> List[float]: ...
    def loops_len(self) -> int: ...
    def polygons_len(self) -> int: ...
    def polygon_loop_starts(self) -> List[int]: ...
    def polygon_loop_totals(self) -> List[int]: ...
    def polygon_vertices(self) -> List[int]: ...
    def weight_groups(self) -> Dict[int, Dict[int, float]]: ...

class LoadedBone:
    def name(self) -> str: ...
    def parent(self) -> int: ...
    def position(self) -> List[float]: ...
    def rotation(self) -> List[float]: ...
