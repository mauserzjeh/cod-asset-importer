package importer

type (
	LoadedIBSP struct {
		IBSP IBSP
	}

	LoadedModel struct {
		XModel     XModel
		XModelPart XModelPart
		XModelSurf XModelSurf
		Materials  []LoadedMaterial
		Angles     Vec3
		Origin     Vec3
		Scale      Vec3
	}

	LoadedMaterial struct {
		Material Material
		Textures map[string]LoadedTexture
	}

	LoadedTexture struct {
		Texture IWI
	}

	Callbacks struct {
		CallbackIBSP     func(LoadedIBSP)
		CallbackModel    func(LoadedModel)
		CallbackMaterial func(LoadedMaterial)
	}
)

// SetCallbackIBSP
func (c *Callbacks) SetCallbackIBSP(f func(LoadedIBSP)) {
	c.CallbackIBSP = f
}

// SetCallbackModel
func (c *Callbacks) SetCallbackModel(f func(LoadedModel)) {
	c.CallbackModel = f
}

// CallbackMaterial
func (c *Callbacks) SetCallbackMaterial(f func(LoadedMaterial)) {
	c.CallbackMaterial = f
}
