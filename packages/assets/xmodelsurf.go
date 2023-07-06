package assets

import (
	"encoding/binary"
	"fmt"
	"os"
)

type (
	XModelSurf struct {
		Name     string
		Version  uint16
		Surfaces []xmodelSurfSurface
	}

	xmodelSurfVertex struct {
		Normal   vec3
		Color    color
		UV       uv
		Bone     uint16
		Position vec3
		Weights  []xmodelSurfWeight
	}

	xmodelSurfWeight struct {
		Bone      uint16
		Influence float32
	}

	xmodelSurfSurface struct {
		Vertices  []xmodelSurfVertex
		Triangles []triangle
	}
)

const (
	RIGGED = 65535
)

// Load
func (self *XModelSurf) Load(filePath string, xmodelPart *XModelPart) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	self.Name = fileNameWithoutExt(filePath)

	err = binary.Read(f, binary.LittleEndian, &self.Version)
	if err != nil {
		return errorLogAndReturn(err)
	}

	switch self.Version {
	case VERSION_COD1:
		err := self.loadV14(f, xmodelPart)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD2:
		err := self.loadV20(f, xmodelPart)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD4:
		err := self.loadV25(f, xmodelPart)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	default:
		return fmt.Errorf("invalid xmodelsurf version: %v", self.Version)
	}
}

// loadV14
func (self *XModelSurf) loadV14(f *os.File, xmodelPart *XModelPart) error {
	var surfaceCount uint16
	err := binary.Read(f, binary.LittleEndian, &surfaceCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(surfaceCount); i++ {
		var surfaceHeader struct {
			_              byte
			VertexCount    uint16
			_              [2]byte
			TriangleCount  uint16
			DefaultBoneIdx uint16
		}

		err := binary.Read(f, binary.LittleEndian, &surfaceHeader)
		if err != nil {
			return errorLogAndReturn(err)
		}

		defaultBoneIdx := uint16(0)
		if surfaceHeader.DefaultBoneIdx == RIGGED {
			err := readPadding(f, 4)
			if err != nil {
				return errorLogAndReturn(err)
			}
		} else {
			defaultBoneIdx = surfaceHeader.DefaultBoneIdx
		}

		triangles := []triangle{}
		for {
			var idxCount byte
			err := binary.Read(f, binary.LittleEndian, &idxCount)
			if err != nil {
				return errorLogAndReturn(err)
			}

			var idx1 uint16
			var idx2 uint16
			var idx3 uint16

			err = binary.Read(f, binary.LittleEndian, &idx1)
			if err != nil {
				return errorLogAndReturn(err)
			}
			err = binary.Read(f, binary.LittleEndian, &idx2)
			if err != nil {
				return errorLogAndReturn(err)
			}
			err = binary.Read(f, binary.LittleEndian, &idx3)
			if err != nil {
				return errorLogAndReturn(err)
			}

			if idx1 != idx2 && idx1 != idx3 && idx2 != idx3 {
				triangles = append(triangles, triangle{
					V1: idx1,
					V2: idx2,
					V3: idx3,
				})
			}

			v := 0
			j := 3
			for j < int(idxCount) {
				idx4 := idx3
				var idx5 uint16
				err = binary.Read(f, binary.LittleEndian, &idx5)
				if err != nil {
					return errorLogAndReturn(err)
				}

				if idx4 != idx2 && idx4 != idx5 && idx2 != idx5 {
					triangles = append(triangles, triangle{
						V1: idx4,
						V2: idx2,
						V3: idx5,
					})
				}

				v = j + 1
				if v >= int(idxCount) {
					break
				}

				idx2 := idx5
				err = binary.Read(f, binary.LittleEndian, &idx3)
				if err != nil {
					return errorLogAndReturn(err)
				}

				if idx4 != idx2 && idx4 != idx3 && idx2 != idx3 {
					triangles = append(triangles, triangle{
						V1: idx4,
						V2: idx2,
						V3: idx3,
					})
				}

				j = v + 1
			}

			if len(triangles) >= int(surfaceHeader.TriangleCount) {
				break
			}
		}

		boneWeightCounts := make([]uint16, surfaceHeader.VertexCount)
		vertices := []xmodelSurfVertex{}
		for k := 0; k < int(surfaceHeader.VertexCount); k++ {
			vertex := xmodelSurfVertex{}
			err := binary.Read(f, binary.LittleEndian, &vertex.Normal)
			if err != nil {
				return errorLogAndReturn(err)
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.UV)
			if err != nil {
				return errorLogAndReturn(err)
			}
			// flip UV
			vertex.UV.V = 1 - vertex.UV.V

			weightCount := uint16(0)
			vertexBoneIdx := defaultBoneIdx

			if surfaceHeader.DefaultBoneIdx == RIGGED {
				err = binary.Read(f, binary.LittleEndian, &weightCount)
				if err != nil {
					return errorLogAndReturn(err)
				}
				err = binary.Read(f, binary.LittleEndian, &vertexBoneIdx)
				if err != nil {
					return errorLogAndReturn(err)
				}
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.Position)
			if err != nil {
				return errorLogAndReturn(err)
			}

			if weightCount != 0 {
				err = readPadding(f, 4)
				if err != nil {
					return errorLogAndReturn(err)
				}
			}

			boneWeightCounts[k] = weightCount

			if xmodelPart != nil {
				xmodelPartBone := xmodelPart.Bones[vertexBoneIdx]

				vertex.Position = xmodelPartBone.WorldTransform.Rotation.transformVec(vertex.Position)
				vertex.Position = vertex.Position.add(xmodelPartBone.WorldTransform.Positon)

				vertex.Normal = xmodelPartBone.WorldTransform.Rotation.transformVec(vertex.Normal)
			}

			vertex.Color = color{
				R: 1,
				G: 1,
				B: 1,
				A: 1,
			}
			vertex.Bone = vertexBoneIdx
			vertex.Weights = append(vertex.Weights, xmodelSurfWeight{
				Bone:      vertexBoneIdx,
				Influence: 1,
			})

			vertices = append(vertices, vertex)
		}

		for m := 0; m < int(surfaceHeader.VertexCount); m++ {
			for n := 0; n < int(boneWeightCounts[m]); n++ {
				var weightBoneIdx uint16
				err := binary.Read(f, binary.LittleEndian, &weightBoneIdx)
				if err != nil {
					return errorLogAndReturn(err)
				}

				err = readPadding(f, 12)
				if err != nil {
					return errorLogAndReturn(err)
				}

				var weightInfluence float32
				err = binary.Read(f, binary.LittleEndian, &weightInfluence)
				if err != nil {
					return errorLogAndReturn(err)
				}

				weightInfluence = weightInfluence / RIGGED

				vertices[m].Weights[0].Influence -= weightInfluence
				vertices[m].Weights = append(vertices[m].Weights, xmodelSurfWeight{
					Bone:      weightBoneIdx,
					Influence: weightInfluence,
				})
			}
		}

		self.Surfaces = append(self.Surfaces, xmodelSurfSurface{
			Vertices:  vertices,
			Triangles: triangles,
		})
	}

	return nil
}

// loadV20
func (self *XModelSurf) loadV20(f *os.File, xmodelPart *XModelPart) error {
	var surfaceCount uint16
	err := binary.Read(f, binary.LittleEndian, &surfaceCount)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := 0; i < int(surfaceCount); i++ {
		var surfaceHeader struct {
			_              byte
			VertexCount    uint16
			TriangleCount  uint16
			DefaultBoneIdx uint16
		}

		err := binary.Read(f, binary.LittleEndian, &surfaceHeader)
		if err != nil {
			return errorLogAndReturn(err)
		}

		defaultBoneIdx := uint16(0)
		if surfaceHeader.DefaultBoneIdx == RIGGED {
			err := readPadding(f, 2)
			if err != nil {
				return errorLogAndReturn(err)
			}
		} else {
			defaultBoneIdx = surfaceHeader.DefaultBoneIdx
		}

		vertices := []xmodelSurfVertex{}
		for j := 0; j < int(surfaceHeader.VertexCount); j++ {
			vertex := xmodelSurfVertex{}
			err := binary.Read(f, binary.LittleEndian, &vertex.Normal)
			if err != nil {
				return errorLogAndReturn(err)
			}

			var vertexColor [4]byte
			err = binary.Read(f, binary.LittleEndian, &vertexColor)
			if err != nil {
				return errorLogAndReturn(err)
			}

			vertex.Color = color{
				R: float32(vertexColor[0]) / 255,
				G: float32(vertexColor[1]) / 255,
				B: float32(vertexColor[2]) / 255,
				A: float32(vertexColor[3]) / 255,
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.UV)
			if err != nil {
				return errorLogAndReturn(err)
			}
			vertex.UV.V = 1 - vertex.UV.V

			err = readPadding(f, 24)
			if err != nil {
				return errorLogAndReturn(err)
			}

			weightCount := uint8(0)
			vertexBoneIdx := defaultBoneIdx

			if surfaceHeader.DefaultBoneIdx == RIGGED {
				err := binary.Read(f, binary.LittleEndian, &weightCount)
				if err != nil {
					return errorLogAndReturn(err)
				}

				err = binary.Read(f, binary.LittleEndian, &vertexBoneIdx)
				if err != nil {
					return errorLogAndReturn(err)
				}
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.Position)
			if err != nil {
				return errorLogAndReturn(err)
			}

			vertex.Weights = append(vertex.Weights, xmodelSurfWeight{
				Bone:      vertexBoneIdx,
				Influence: 1,
			})

			if weightCount > 0 {
				err := readPadding(f, 1)
				if err != nil {
					return errorLogAndReturn(err)
				}

				for k := 0; k < int(weightCount); k++ {
					var weightBoneIdx uint16
					err := binary.Read(f, binary.LittleEndian, &weightBoneIdx)
					if err != nil {
						return errorLogAndReturn(err)
					}

					err = readPadding(f, 12)
					if err != nil {
						return errorLogAndReturn(err)
					}

					var weightInfluence uint16
					err = binary.Read(f, binary.LittleEndian, &weightInfluence)
					if err != nil {
						return errorLogAndReturn(err)
					}

					weightInfluenceFloat := float32(weightInfluence) / RIGGED

					vertex.Weights[0].Influence -= weightInfluenceFloat
					vertex.Weights = append(vertex.Weights, xmodelSurfWeight{
						Bone:      weightBoneIdx,
						Influence: weightInfluenceFloat,
					})
				}
			}

			if xmodelPart != nil {
				xmodelPartBone := xmodelPart.Bones[vertexBoneIdx]

				vertex.Position = xmodelPartBone.WorldTransform.Rotation.transformVec(vertex.Position)
				vertex.Position = vertex.Position.add(xmodelPartBone.WorldTransform.Positon)

				vertex.Normal = xmodelPartBone.WorldTransform.Rotation.transformVec(vertex.Normal)
			}

			vertex.Bone = vertexBoneIdx

			vertices = append(vertices, vertex)
		}

		triangles := []triangle{}
		for l := 0; l < int(surfaceHeader.TriangleCount); l++ {
			var tri triangle
			err := binary.Read(f, binary.LittleEndian, &tri)
			if err != nil {
				return errorLogAndReturn(err)
			}

			triangles = append(triangles, tri)
		}

		self.Surfaces = append(self.Surfaces, xmodelSurfSurface{
			Vertices:  vertices,
			Triangles: triangles,
		})
	}

	return nil
}

// loadV25
func (self *XModelSurf) loadV25(f *os.File, xmodelPart *XModelPart) error {
	var surfaceCount uint16
	err := binary.Read(f, binary.LittleEndian, &surfaceCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(surfaceCount); i++ {
		var surfaceHeader struct {
			_             [3]byte
			VertexCount   uint16
			TriangleCount uint16
			VertexCount2  uint16
		}

		err := binary.Read(f, binary.LittleEndian, &surfaceHeader)
		if err != nil {
			return errorLogAndReturn(err)
		}

		if surfaceHeader.VertexCount != surfaceHeader.VertexCount2 {
			for {
				var p uint16
				err := binary.Read(f, binary.LittleEndian, &p)
				if err != nil {
					return errorLogAndReturn(err)
				}

				if p == 0 {
					break
				}
			}

			err := readPadding(f, 2)
			if err != nil {
				return errorLogAndReturn(err)
			}
		} else {
			err := readPadding(f, 4)
			if err != nil {
				return errorLogAndReturn(err)
			}
		}

		vertices := []xmodelSurfVertex{}
		for j := 0; j < int(surfaceHeader.VertexCount); j++ {
			vertex := xmodelSurfVertex{}

			err := binary.Read(f, binary.LittleEndian, &vertex.Normal)
			if err != nil {
				return errorLogAndReturn(err)
			}

			var clr [4]byte
			err = binary.Read(f, binary.LittleEndian, &clr)
			if err != nil {
				return errorLogAndReturn(err)
			}

			vertex.Color = color{
				R: float32(clr[0]) / 255,
				G: float32(clr[1]) / 255,
				B: float32(clr[2]) / 255,
				A: float32(clr[3]) / 255,
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.UV)
			if err != nil {
				return errorLogAndReturn(err)
			}

			vertex.UV.V = 1 - vertex.UV.V

			err = readPadding(f, 24)
			if err != nil {
				return errorLogAndReturn(err)
			}

			weightCount := uint8(0)
			vertexBoneIdx := uint16(0)
			if surfaceHeader.VertexCount != surfaceHeader.VertexCount2 {
				err := binary.Read(f, binary.LittleEndian, &weightCount)
				if err != nil {
					return errorLogAndReturn(err)
				}

				err = binary.Read(f, binary.LittleEndian, &vertexBoneIdx)
				if err != nil {
					return errorLogAndReturn(err)
				}
			}

			err = binary.Read(f, binary.LittleEndian, &vertex.Position)
			if err != nil {
				return errorLogAndReturn(err)
			}

			vertex.Weights = append(vertex.Weights, xmodelSurfWeight{
				Bone:      vertexBoneIdx,
				Influence: 1,
			})

			if weightCount > 0 {
				for k := 0; k < int(weightCount); k++ {
					var weightBoneIdx uint16
					err := binary.Read(f, binary.LittleEndian, &weightBoneIdx)
					if err != nil {
						return errorLogAndReturn(err)
					}

					var weightInfluence uint16
					err = binary.Read(f, binary.LittleEndian, &weightInfluence)
					if err != nil {
						return errorLogAndReturn(err)
					}

					weightInfluenceFloat := float32(weightInfluence) / RIGGED
					vertex.Weights[0].Influence -= weightInfluenceFloat
					vertex.Weights = append(vertex.Weights, xmodelSurfWeight{
						Bone:      weightBoneIdx,
						Influence: weightInfluenceFloat,
					})
				}
			}

			vertex.Bone = vertexBoneIdx
			vertices = append(vertices, vertex)
		}

		triangles := []triangle{}
		for l := 0; l < int(surfaceHeader.TriangleCount); l++ {
			var tri triangle
			err := binary.Read(f, binary.LittleEndian, &tri)
			if err != nil {
				return errorLogAndReturn(err)
			}
		}

		self.Surfaces = append(self.Surfaces, xmodelSurfSurface{
			Vertices:  vertices,
			Triangles: triangles,
		})
	}

	return nil
}
