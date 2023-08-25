import interface
import log

class Importer:
    def xmodel(self, model: interface.LoadedModel) -> None:
        log.debug_log(model.name())
    
    def ibsp(self, ibsp: interface.LoadedIbsp) -> None: 
        log.debug_log(ibsp.name())

    def material(self, material: interface.LoadedMaterial) -> None:
        log.debug_log(material.name())