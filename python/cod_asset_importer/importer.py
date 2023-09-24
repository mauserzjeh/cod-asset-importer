import bpy
import traceback
from . cod_asset_importer import (
    LoadedModel,
    LoadedIbsp,
    LoadedMaterial,
    Loader,
    debug_log,
    error_log,
)


class Importer:
    def xmodel(self, model: LoadedModel) -> None:
        debug_log(model.name())

    def ibsp(self, ibsp: LoadedIbsp) -> None:
        debug_log(ibsp.name())

    def material(self, material: LoadedMaterial) -> None:
        debug_log(material.name())


def import_ibsp(asset_path: str, file_path: str) -> None:
    importer = Importer()
    loader = Loader(importer=importer)
    try:
        loader.import_bsp(asset_path=asset_path, file_path=file_path)
    except:
        error_log(traceback.print_exc())


def import_xmodel(asset_path: str, file_path: str) -> bpy.types.Object | bool:
    importer = Importer()
    loader = Loader(importer=importer)
    try:
        loader.import_xmodel(
            asset_path=asset_path,
            file_path=file_path,
            angles=(0.0, 0.0, 0.0),
            origin=(0.0, 0.0, 0.0),
            scale=(1.0, 1.0, 1.0),
        )
    except:
        error_log(traceback.print_exc())
