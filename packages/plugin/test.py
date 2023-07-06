from assets import assets

ibsp = assets.IBSP()
try:
    ibsp.Load("E:/MOVIEMAKING/CALL OF DUTY/3D STUFF/CODASSETS/COD2ASSETS/maps/mp/mp_decoy.d3dbsp")
    print(ibsp.Name)
    print(ibsp.Entities[0])
except Exception as e:
    print(e)

# xmodel = assets.XModel()
# try:
#     xmodel.Load("E:/MOVIEMAKING/CALL OF DUTY/3D STUFF/CODASSETS/COD2ASSETS/xmodel/character_german_camo_fat")
#     print(xmodel.Name)
#     print(xmodel.Lods[0].Name)
# except Exception as e:
#     print(e)


