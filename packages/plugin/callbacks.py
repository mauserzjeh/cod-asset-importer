from importer import importer


def callbackIbsp(loadedIbsp: importer.LoadedIBSP):
    print(f"ibsp {loadedIbsp}")

def callbackModel(loadedModel: importer.LoadedModel):
    print(f"xmodel {loadedModel}")

def callbackMaterial(loadedMaterial: importer.LoadedMaterial):
    return 

    print(f"material {loadedMaterial.Material.Name}")
    for m in loadedMaterial.Textures.keys():
        print(f"texture {m}")



callbackObj = importer.Callbacks()
callbackObj.SetCallbackIBSP(f=callbackIbsp)
callbackObj.SetCallbackModel(f=callbackModel)
callbackObj.SetCallbackMaterial(f=callbackMaterial)