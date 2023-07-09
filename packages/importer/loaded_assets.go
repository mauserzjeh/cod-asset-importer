package importer

import "assets"

type (
	LoadedIBSP struct {
		IBSP assets.IBSP
	}

	LoadedModel struct {
		XModel     assets.XModel
		XModelPart assets.XModelPart
		XModelSurf assets.XModelSurf
		Materials  []LoadedMaterial
		Angles     assets.Vec3
		Origin     assets.Vec3
		Scale      assets.Vec3
	}

	LoadedMaterial struct {
		Material assets.Material
		Textures map[string]assets.IWI
	}

	LoadedTexture struct {
		Texture assets.IWI
	}
)
