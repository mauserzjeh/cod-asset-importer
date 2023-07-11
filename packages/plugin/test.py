from importer import importer
import callbacks

imp = importer.NewImporter(10, callbacks.callbackObj)
assetPath = "E:/MOVIEMAKING/CALL OF DUTY/3D STUFF/CODASSETS/COD2ASSETS"
filePath = f"{assetPath}/maps/mp/mp_toujane.d3dbsp"
imp.ImportIBSP(assetPath=assetPath, filePath=filePath)