package importer

import (
	"assets"
	"path"
	"sync"
)

type (
	importStatus int

	Importer struct {
		Models    map[string]LoadedModel
		Textures  map[string]LoadedTexture
		Materials map[string]LoadedMaterial
		mux       sync.Mutex
	}

	LoadedIBSP struct {
		IBSP   assets.IBSP
		Status importStatus
	}

	LoadedModel struct {
		XModel     assets.XModel
		XModelPart assets.XModelPart
		XModelSurf assets.XModelSurf
		Materials  []assets.Material
		Textures   map[string]assets.IWI

		Status importStatus
	}

	LoadedMaterial struct {
		Material assets.Material
		Status   importStatus
	}

	LoadedTexture struct {
		Texture assets.IWI
		Status  importStatus
	}
)

const (
	importStatusInProgress importStatus = 0
	importStatusFinished   importStatus = 1
)

// ImportBSP
func (imp *Importer) ImportIBSP(assetPath, filePath string) error {
	return nil
}

// ImportXModel
func (imp *Importer) ImportXModel(assetPath, filePath string, callback func(LoadedModel)) error {
	xmodel := assets.XModel{}
	err := xmodel.Load(filePath)
	if err != nil {
		return errorLogAndReturn(err)
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
		return errorLogAndReturn(err)
	}

	loadedMaterials := []assets.Material{}
	if xmodel.Version == assets.VERSION_COD2 || xmodel.Version == assets.VERSION_COD4 {
		for _, t := range lod0.Textures {
			materialFilePath := path.Join(assetPath, assets.ASSETPATH_MATERIALS, t)
			material := assets.Material{}
			err := material.Load(materialFilePath, int(xmodel.Version))
			if err != nil {
				errorLog(err)
				continue
			}

			// TODO load textures

			loadedMaterials = append(loadedMaterials, material)
		}
	}

	// TODO
	loadedModel := LoadedModel{}

	callback(loadedModel)
	return nil
}
