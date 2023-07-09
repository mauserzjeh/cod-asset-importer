package importer

import (
	"assets"
	"path"
	"sync"
)

type (
	ImportStatus int

	Importer struct {
		Models    map[string]LoadedModel
		Textures  map[string]LoadedTexture
		Materials map[string]LoadedMaterial
	}
)

const (
	ImportStatusInProgress ImportStatus = 0
	ImportStatusFinished   ImportStatus = 1
)

// NewImporter
func NewImporter() Importer {
	return Importer{
		Models:    map[string]LoadedModel{},
		Textures:  map[string]LoadedTexture{},
		Materials: map[string]LoadedMaterial{},
	}
}

// ImportBSP
func (imp *Importer) ImportIBSP(assetPath, filePath string, poolSize uint, callbackIbsp func(LoadedIBSP), callbackMaterial func(LoadedMaterial), callbackXmodel func(LoadedModel)) error {
	ibsp := assets.IBSP{}
	err := ibsp.Load(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}

	wp := newWorkerPool(poolSize)

	wg := sync.WaitGroup{}
	for _, mat := range ibsp.Materials {
		wg.Add(1)

		wp.addTask(func() {
			defer wg.Done()

			version := assets.VERSION_COD1
			if ibsp.Header.Version == assets.IBSP_VER_v4 {
				version = assets.VERSION_COD2
			}
			loadedMaterial, err := imp.loadMaterial(assetPath, mat.GetName(), version)
			if err != nil {
				errorLog(err)
				return
			}

			callbackMaterial(loadedMaterial)
		})

	}

	wg.Wait()

	callbackIbsp(LoadedIBSP{
		IBSP: ibsp,
	})

	for _, ent := range ibsp.Entities {
		wg.Add(1)

		wp.addTask(func() {
			defer wg.Done()

			xmodelFilePath := path.Join(assetPath, assets.ASSETPATH_XMODEL, ent.Name)
			loadedModel, err := imp.ImportXModel(assetPath, xmodelFilePath)
			if err != nil {
				errorLog(err)
				return
			}

			loadedModel.Angles = ent.Angles
			loadedModel.Origin = ent.Origin
			loadedModel.Scale = ent.Scale

			callbackXmodel(loadedModel)
		})
	}

	wg.Wait()
	return nil
}

// ImportXModel
func (imp *Importer) ImportXModel(assetPath, filePath string) (LoadedModel, error) {
	xmodel := assets.XModel{}
	err := xmodel.Load(filePath)
	if err != nil {
		return LoadedModel{}, errorLogAndReturn(err)
	}

	lod0 := xmodel.Lods[0]
	xmodelPartFilePath := path.Join(assetPath, assets.ASSETPATH_XMODELPARTS, lod0.Name)
	xmodelPart := &assets.XModelPart{}
	err = xmodelPart.Load(xmodelPartFilePath)
	if err != nil {
		errorLog(err)
		xmodelPart = nil
	}

	xmodelSurfFilePath := path.Join(assetPath, assets.ASSETPATH_XMODELSURFS, lod0.Name)
	xmodelSurf := assets.XModelSurf{}
	err = xmodelSurf.Load(xmodelSurfFilePath, xmodelPart)
	if err != nil {
		return LoadedModel{}, errorLogAndReturn(err)
	}

	loadedMaterials := []LoadedMaterial{}
	if xmodel.Version == assets.VERSION_COD2 || xmodel.Version == assets.VERSION_COD4 {
		for _, mat := range lod0.Materials {
			loadedMaterial, err := imp.loadMaterial(assetPath, mat, int(xmodel.Version))
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
		Angles:     assets.Vec3{},
		Origin:     assets.Vec3{},
		Scale: assets.Vec3{
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
	materialFilePath := path.Join(assetPath, assets.ASSETPATH_MATERIALS, materialName)
	material := assets.Material{}
	err := material.Load(materialFilePath, version)
	if err != nil {
		return LoadedMaterial{}, errorLogAndReturn(err)
	}

	loadedTextures := map[string]assets.IWI{}
	for _, tex := range material.Textures {
		if _, ok := loadedTextures[tex.Name]; ok {
			continue
		}

		textFilePath := path.Join(assetPath, assets.ASSETPATH_TEXTURES, tex.Name)
		texture := assets.IWI{}
		err := texture.Load(textFilePath)
		if err != nil {
			errorLog(err)
			continue
		}

		loadedTextures[tex.Name] = texture
	}

	return LoadedMaterial{
		Material: material,
		Textures: loadedTextures,
	}, nil
}
