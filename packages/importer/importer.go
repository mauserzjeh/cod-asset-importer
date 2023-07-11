package importer

import (
	"path"
	"sync"
)

type (
	Importer struct {
		CallbackObj Callbacks
		Poolsize    uint
	}
)

// NewImporter
func NewImporter(poolSize uint, callbackObj Callbacks) Importer {
	return Importer{
		CallbackObj: callbackObj,
		Poolsize:    poolSize,
	}
}

// ImportBSP
func (imp *Importer) ImportIBSP(assetPath, filePath string) error {
	ibsp := IBSP{}
	err := ibsp.load(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}

	wp := newWorkerPool(imp.Poolsize)

	wg := sync.WaitGroup{}
	for _, mat := range ibsp.materials {
		wg.Add(1)
		wp.addTask(func() {
			defer wg.Done()

			version := VERSION_COD1
			if ibsp.header.Version == iBSP_VER_v4 {
				version = VERSION_COD2
			}
			loadedMaterial, err := imp.loadMaterial(assetPath, mat.getName(), version)
			if err != nil {
				errorLog(err)
				return
			}

			imp.CallbackObj.CallbackMaterial(loadedMaterial)
		})

	}

	wg.Wait()

	imp.CallbackObj.CallbackIBSP(LoadedIBSP{
		IBSP: ibsp,
	})

	for _, ent := range ibsp.Entities {
		wg.Add(1)

		wp.addTask(func() {
			defer wg.Done()

			xmodelFilePath := path.Join(assetPath, ASSETPATH_XMODEL, ent.Name)
			loadedModel, err := imp.ImportXModel(assetPath, xmodelFilePath)
			if err != nil {
				errorLog(err)
				return
			}

			loadedModel.Angles = ent.Angles
			loadedModel.Origin = ent.Origin
			loadedModel.Scale = ent.Scale

			imp.CallbackObj.CallbackModel(loadedModel)
		})
	}

	wg.Wait()

	wp.stop()
	return nil
}

// ImportXModel
func (imp *Importer) ImportXModel(assetPath, filePath string) (LoadedModel, error) {
	xmodel := XModel{}
	err := xmodel.load(filePath)
	if err != nil {
		return LoadedModel{}, errorLogAndReturn(err)
	}

	lod0 := xmodel.lods[0]
	xmodelPartFilePath := path.Join(assetPath, ASSETPATH_XMODELPARTS, lod0.Name)
	xmodelPart := &XModelPart{}
	err = xmodelPart.load(xmodelPartFilePath)
	if err != nil {
		errorLog(err)
		xmodelPart = nil
	}

	xmodelSurfFilePath := path.Join(assetPath, ASSETPATH_XMODELSURFS, lod0.Name)
	xmodelSurf := XModelSurf{}
	err = xmodelSurf.load(xmodelSurfFilePath, xmodelPart)
	if err != nil {
		return LoadedModel{}, errorLogAndReturn(err)
	}

	loadedMaterials := []LoadedMaterial{}
	if xmodel.version == VERSION_COD2 || xmodel.version == VERSION_COD4 {
		for _, mat := range lod0.Materials {
			loadedMaterial, err := imp.loadMaterial(assetPath, mat, int(xmodel.version))
			if err != nil {
				errorLog(err)
				continue
			}

			loadedMaterials = append(loadedMaterials, loadedMaterial)
		}
	}

	loadedModel := LoadedModel{
		XModel:     xmodel,
		XModelSurf: xmodelSurf,
		Materials:  loadedMaterials,
		Angles:     Vec3{},
		Origin:     Vec3{},
		Scale: Vec3{
			X: 1,
			Y: 1,
			Z: 1,
		},
	}

	if xmodelPart != nil {
		loadedModel.XModelPart = *xmodelPart
	}

	return loadedModel, nil
}

// loadMaterial
func (imp *Importer) loadMaterial(assetPath, materialName string, version int) (LoadedMaterial, error) {
	materialFilePath := path.Join(assetPath, ASSETPATH_MATERIALS, materialName)
	material := Material{}
	err := material.Load(materialFilePath, version)
	if err != nil {
		return LoadedMaterial{}, errorLogAndReturn(err)
	}

	loadedTextures := map[string]LoadedTexture{}
	for _, tex := range material.textures {
		if _, ok := loadedTextures[tex.Name]; ok {
			continue
		}

		textFilePath := path.Join(assetPath, ASSETPATH_TEXTURES, tex.Name+".iwi")
		texture := IWI{}
		err := texture.Load(textFilePath)
		if err != nil {
			errorLog(err)
			continue
		}

		loadedTextures[tex.Name] = LoadedTexture{
			Texture: texture,
		}
	}

	return LoadedMaterial{
		Material: material,
		Textures: loadedTextures,
	}, nil
}
