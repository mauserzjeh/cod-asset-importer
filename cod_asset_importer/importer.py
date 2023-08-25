from .interface import (
    debug_log,
    LoadedModel,
    LoadedIbsp,
    LoadedMaterial
)

class Importer:
    def xmodel(self, model: LoadedModel) -> None:
        debug_log(model.name())
    
    def ibsp(self, ibsp: LoadedIbsp) -> None: 
        debug_log(ibsp.name())

    def material(self, material: LoadedMaterial) -> None:
        debug_log(material.name())