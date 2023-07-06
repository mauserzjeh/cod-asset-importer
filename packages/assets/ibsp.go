package assets

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"
	"unsafe"
)

const (

	// CoD1 & CoD:UO
	IBSP_VER_v59           = 0x3B
	LUMP_v59_MATERIALS     = 0
	LUMP_v59_TRIANGLESOUPS = 6
	LUMP_v59_VERTICES      = 7
	LUMP_v59_TRIANGLES     = 8
	LUMP_v59_ENTITIES      = 29

	// CoD2
	IBSP_VER_v4           = 0x4
	LUMP_v4_MATERIALS     = 0
	LUMP_v4_TRIANGLESOUPS = 7
	LUMP_v4_VERTICES      = 8
	LUMP_v4_TRIANGLES     = 9
	LUMP_v4_ENTITIES      = 37
)

type (
	IBSP struct {
		Name          string
		Header        ibspHeader
		Lumps         [39]ibspLump
		Materials     []ibspMaterial
		Vertices      []ibspVertex
		Triangles     []triangle
		TriangleSoups []ibspTriangleSoup
		Entities      []ibspEntity
		Surfaces      []ibspSurface
	}

	ibspHeader struct {
		Magic   [4]byte
		Version int32
	}

	ibspLump struct {
		Length uint32
		Offset uint32
	}

	ibspMaterial struct {
		Name [64]byte
		Flag uint64
	}

	ibspTriangleSoup struct {
		MaterialIdx     uint16
		DrawOrder       uint16
		VerticesOffset  uint32
		VerticesLength  uint16
		TrianglesOffset uint16
		TrianglesLength uint32
	}

	ibspVertexV4 struct {
		Position vec3
		Normal   vec3
		Color    color
		UV       uv
		_        [32]byte
	}

	ibspVertexV59 struct {
		Position vec3
		UV       uv
		_        [8]byte
		Normal   vec3
		Color    color
	}

	ibspVertex interface {
		getPosition() vec3
		getNormal() vec3
		getColor() color
		getUV() uv
	}

	ibspEntity struct {
		Name   string
		Angles vec3
		Origin vec3
		Scale  vec3
	}

	ibspRawEntity struct {
		Model      string `json:"model"`
		Angles     string `json:"angles"`
		Origin     string `json:"origin"`
		ModelScale string `json:"modelscale"`
	}

	ibspSurface struct {
		Material  string
		Vertices  map[uint16]ibspVertex
		Triangles []triangle
	}
)

var (
	validEntityModel = regexp.MustCompile(`(?i)^xmodel\/(?P<name>.*)`)
)

// newIBSPVertex
func newIBSPVertex(version int32) (ibspVertex, error) {
	switch version {
	case IBSP_VER_v4:
		return &ibspVertexV4{}, nil
	case IBSP_VER_v59:
		return &ibspVertexV59{}, nil
	default:
		return nil, fmt.Errorf("invalid version: %v", version)
	}
}

// GetPosition
func (self *ibspVertexV4) getPosition() vec3 {
	return self.Position
}

// GetPosition
func (self *ibspVertexV4) getNormal() vec3 {
	return self.Normal
}

// GetPosition
func (self *ibspVertexV4) getColor() color {
	return self.Color
}

// GetPosition
func (self *ibspVertexV4) getUV() uv {
	return self.UV
}

// GetPosition
func (self *ibspVertexV59) getPosition() vec3 {
	return self.Position
}

// GetPosition
func (self *ibspVertexV59) getNormal() vec3 {
	return self.Normal
}

// GetPosition
func (self *ibspVertexV59) getColor() color {
	return self.Color
}

// GetPosition
func (self *ibspVertexV59) getUV() uv {
	return self.UV
}

// getName
func (self *ibspMaterial) getName() string {
	return string(bytes.Trim(self.Name[:], "\x00"))
}

// valid
func (self *ibspRawEntity) valid() (bool, string) {
	matches := validEntityModel.FindStringSubmatch(self.Model)
	l := len(matches)
	if l == 0 {
		return false, ""
	}

	idx := validEntityModel.SubexpIndex("name")
	if idx > l-1 {
		return false, ""
	}

	return true, matches[idx]
}

// Load
func (self *IBSP) Load(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	self.Name = fileNameWithoutExt(filePath)

	err = self.readHeader(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readLumps(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readMaterials(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readTriangleSoups(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readVertices(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readTriangles(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = self.readEntities(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	// self.loadSurfaces()

	return nil
}

// readHeader
func (self *IBSP) readHeader(f *os.File) error {
	err := binary.Read(f, binary.LittleEndian, &self.Header)
	if err != nil {
		return errorLogAndReturn(err)
	}

	if self.Header.Magic != [4]byte{'I', 'B', 'S', 'P'} {
		return fmt.Errorf("invalid magic: %s", string(self.Header.Magic[:]))
	}

	if self.Header.Version != IBSP_VER_v59 && self.Header.Version != IBSP_VER_v4 {
		return fmt.Errorf("invalid IBSP version: %v", self.Header.Version)
	}

	return nil
}

// readLumps
func (self *IBSP) readLumps(f *os.File) error {
	return binary.Read(f, binary.LittleEndian, &self.Lumps)
}

// readMaterials
func (self *IBSP) readMaterials(f *os.File) error {
	matLumpIdx := LUMP_v59_MATERIALS
	if self.Header.Version == IBSP_VER_v4 {
		matLumpIdx = LUMP_v4_MATERIALS
	}

	matLump := self.Lumps[matLumpIdx]
	matSize := uint32(unsafe.Sizeof(ibspMaterial{}))

	_, err := f.Seek(int64(matLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < matLump.Length; i += matSize {
		material := ibspMaterial{}
		err := binary.Read(f, binary.LittleEndian, &material)
		if err != nil {
			errorLog(err)
			return err
		}

		self.Materials = append(self.Materials, material)
	}

	return nil
}

// readTriangleSoups
func (self *IBSP) readTriangleSoups(f *os.File) error {
	tsLumpIdx := LUMP_v59_TRIANGLESOUPS
	if self.Header.Version == IBSP_VER_v4 {
		tsLumpIdx = LUMP_v4_TRIANGLESOUPS
	}

	tsLump := self.Lumps[tsLumpIdx]
	tsSize := uint32(unsafe.Sizeof(ibspTriangleSoup{}))

	_, err := f.Seek(int64(tsLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < tsLump.Length; i += tsSize {
		triangleSoup := ibspTriangleSoup{}
		err := binary.Read(f, binary.LittleEndian, &triangleSoup)
		if err != nil {
			errorLog(err)
			return err
		}

		self.TriangleSoups = append(self.TriangleSoups, triangleSoup)
	}

	return nil
}

// readVertices
func (self *IBSP) readVertices(f *os.File) error {
	vertLumpIdx := LUMP_v59_VERTICES
	vertSize := uint32(unsafe.Sizeof(ibspVertexV59{}))
	if self.Header.Version == IBSP_VER_v4 {
		vertLumpIdx = LUMP_v4_VERTICES
		vertSize = uint32(unsafe.Sizeof(ibspVertexV4{}))
	}

	vertLump := self.Lumps[vertLumpIdx]

	_, err := f.Seek(int64(vertLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < vertLump.Length; i += vertSize {
		vertex, err := newIBSPVertex(self.Header.Version)
		if err != nil {
			errorLog(err)
			return err
		}
		err = binary.Read(f, binary.LittleEndian, vertex)
		if err != nil {
			errorLog(err)
			return err
		}

		self.Vertices = append(self.Vertices, vertex)
	}

	return nil
}

// readTriangles
func (self *IBSP) readTriangles(f *os.File) error {
	triLumpIdx := LUMP_v59_TRIANGLES
	if self.Header.Version == IBSP_VER_v4 {
		triLumpIdx = LUMP_v4_TRIANGLES
	}

	triLump := self.Lumps[triLumpIdx]
	triSize := uint32(unsafe.Sizeof(triangle{}))

	_, err := f.Seek(int64(triLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < triLump.Length; i += triSize {
		tri := triangle{}
		err := binary.Read(f, binary.LittleEndian, &tri)
		if err != nil {
			errorLog(err)
			return err
		}

		self.Triangles = append(self.Triangles, tri)
	}

	return nil
}

// readEntities
func (self *IBSP) readEntities(f *os.File) error {
	entLumpIdx := LUMP_v59_ENTITIES
	if self.Header.Version == IBSP_VER_v4 {
		entLumpIdx = LUMP_v4_ENTITIES
	}

	entLump := self.Lumps[entLumpIdx]

	_, err := f.Seek(int64(entLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	entitiesData := make([]byte, entLump.Offset)
	_, err = f.Read(entitiesData)
	if err != nil && err != io.EOF {
		return errorLogAndReturn(err)
	}

	entitiesStr := string(bytes.Trim(entitiesData, "\x00"))
	entitiesStr = "[" + entitiesStr + "]"
	entitiesStr = strings.ReplaceAll(entitiesStr, "}\n{\n", "},\n{\n")
	entitiesStr = strings.ReplaceAll(entitiesStr, "\"\n\"", "\",\n\"")
	entitiesStr = strings.ReplaceAll(entitiesStr, "\" \"", "\":\"")
	entitiesStr = strings.ReplaceAll(entitiesStr, "\\", "/")

	entities := []ibspRawEntity{}
	err = json.Unmarshal([]byte(entitiesStr), &entities)
	if err != nil {
		return errorLogAndReturn(err)
	}

	parseTransform := func(transform string, defaultValue float32) vec3 {
		t := strings.Split(transform, " ")
		l := len(t)
		if l == 3 {
			return vec3{
				X: parseFloat[float32](t[0]),
				Y: parseFloat[float32](t[1]),
				Z: parseFloat[float32](t[2]),
			}
		} else if l == 1 {
			if t[0] == "" {
				return vec3{
					X: defaultValue,
					Y: defaultValue,
					Z: defaultValue,
				}
			}

			return vec3{
				X: parseFloat[float32](t[0]),
				Y: parseFloat[float32](t[0]),
				Z: parseFloat[float32](t[0]),
			}
		}

		return vec3{
			X: defaultValue,
			Y: defaultValue,
			Z: defaultValue,
		}
	}

	for _, ent := range entities {
		if ent.Model == "" {
			continue
		}

		valid, name := ent.valid()
		if !valid {
			continue
		}

		self.Entities = append(self.Entities, ibspEntity{
			Name:   name,
			Angles: parseTransform(ent.Angles, 0),
			Origin: parseTransform(ent.Origin, 0),
			Scale:  parseTransform(ent.ModelScale, 1),
		})
	}

	return nil
}

// TODO fix -> panic: runtime error: index out of range [28123] with length 27656 / mp_decoy.d3dbsp
// loadSurfaces
func (self *IBSP) loadSurfaces() {
	for _, ts := range self.TriangleSoups {
		surface := ibspSurface{
			Material: self.Materials[ts.MaterialIdx].getName(),
			Vertices: make(map[uint16]ibspVertex),
		}

		triCount := ts.TrianglesLength / 3
		for i := 0; i < int(triCount); i++ {
			triIdx := int(ts.TrianglesOffset)/3 + i

			tri := self.Triangles[triIdx]

			vertIdx1 := uint16(ts.VerticesOffset) + tri.V1
			vertIdx2 := uint16(ts.VerticesOffset) + tri.V2
			vertIdx3 := uint16(ts.VerticesOffset) + tri.V3

			surface.Triangles = append(surface.Triangles, triangle{
				V1: vertIdx1,
				V2: vertIdx2,
				V3: vertIdx3,
			})

			surface.Vertices[vertIdx1] = self.Vertices[vertIdx1]
			surface.Vertices[vertIdx2] = self.Vertices[vertIdx2]
			surface.Vertices[vertIdx3] = self.Vertices[vertIdx3]
		}

		self.Surfaces = append(self.Surfaces, surface)
	}

}
