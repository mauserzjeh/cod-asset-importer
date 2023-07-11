package importer

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
	iBSP_VER_v59           = 0x3B
	lUMP_v59_MATERIALS     = 0
	lUMP_v59_TRIANGLESOUPS = 6
	lUMP_v59_VERTICES      = 7
	lUMP_v59_TRIANGLES     = 8
	lUMP_v59_ENTITIES      = 29

	// CoD2
	iBSP_VER_v4           = 0x4
	lUMP_v4_MATERIALS     = 0
	lUMP_v4_TRIANGLESOUPS = 7
	lUMP_v4_VERTICES      = 8
	lUMP_v4_TRIANGLES     = 9
	lUMP_v4_ENTITIES      = 37
)

type (
	IBSP struct {
		Name          string
		header        ibspHeader
		lumps         [39]ibspLump
		materials     []ibspMaterial
		vertices      []IbspVertex
		triangles     []Triangle
		triangleSoups []ibspTriangleSoup
		Entities      []IbspEntity
		Surfaces      []IbspSurface
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
		TrianglesLength uint16
		TrianglesOffset uint32
	}

	IbspVertex struct {
		Position Vec3
		Normal   Vec3
		Color    Color
		UV       UV
	}

	IbspEntity struct {
		Name   string
		Angles Vec3
		Origin Vec3
		Scale  Vec3
	}

	ibspRawEntity struct {
		Model      string `json:"model"`
		Angles     string `json:"angles"`
		Origin     string `json:"origin"`
		ModelScale string `json:"modelscale"`
	}

	IbspSurface struct {
		Material  string
		Vertices  map[uint16]IbspVertex
		Triangles []Triangle
	}
)

var (
	validEntityModel = regexp.MustCompile(`(?i)^xmodel\/(?P<name>.*)`)
)

// getName
func (mat *ibspMaterial) getName() string {
	return string(bytes.Trim(mat.Name[:], "\x00"))
}

// valid
func (ent *ibspRawEntity) valid() (bool, string) {
	matches := validEntityModel.FindStringSubmatch(ent.Model)
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

// load
func (ibsp *IBSP) load(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	ibsp.Name = fileNameWithoutExt(filePath)

	err = ibsp.readHeader(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readLumps(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readMaterials(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readTriangleSoups(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readVertices(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readTriangles(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = ibsp.readEntities(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	ibsp.loadSurfaces()

	return nil
}

// readHeader
func (ibsp *IBSP) readHeader(f *os.File) error {
	err := binary.Read(f, binary.LittleEndian, &ibsp.header)
	if err != nil {
		return errorLogAndReturn(err)
	}

	if ibsp.header.Magic != [4]byte{'I', 'B', 'S', 'P'} {
		return fmt.Errorf("invalid magic: %s", string(ibsp.header.Magic[:]))
	}

	if ibsp.header.Version != iBSP_VER_v59 && ibsp.header.Version != iBSP_VER_v4 {
		return fmt.Errorf("invalid IBSP version: %v", ibsp.header.Version)
	}

	return nil
}

// readLumps
func (ibsp *IBSP) readLumps(f *os.File) error {
	return binary.Read(f, binary.LittleEndian, &ibsp.lumps)
}

// readMaterials
func (ibsp *IBSP) readMaterials(f *os.File) error {
	matLumpIdx := lUMP_v59_MATERIALS
	if ibsp.header.Version == iBSP_VER_v4 {
		matLumpIdx = lUMP_v4_MATERIALS
	}

	matLump := ibsp.lumps[matLumpIdx]
	matSize := uint32(unsafe.Sizeof(ibspMaterial{}))

	_, err := f.Seek(int64(matLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < matLump.Length; i += matSize {
		material := ibspMaterial{}
		err := binary.Read(f, binary.LittleEndian, &material)
		if err != nil {
			return errorLogAndReturn(err)
		}

		ibsp.materials = append(ibsp.materials, material)
	}

	return nil
}

// readTriangleSoups
func (ibsp *IBSP) readTriangleSoups(f *os.File) error {
	tsLumpIdx := lUMP_v59_TRIANGLESOUPS
	if ibsp.header.Version == iBSP_VER_v4 {
		tsLumpIdx = lUMP_v4_TRIANGLESOUPS
	}

	tsLump := ibsp.lumps[tsLumpIdx]
	tsSize := uint32(unsafe.Sizeof(ibspTriangleSoup{}))

	_, err := f.Seek(int64(tsLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < tsLump.Length; i += tsSize {
		triangleSoup := ibspTriangleSoup{}
		err := binary.Read(f, binary.LittleEndian, &triangleSoup)
		if err != nil {
			return errorLogAndReturn(err)
		}

		ibsp.triangleSoups = append(ibsp.triangleSoups, triangleSoup)
	}

	return nil
}

// readVertices
func (ibsp *IBSP) readVertices(f *os.File) error {
	vertLumpIdx := lUMP_v59_VERTICES
	var rawVertex struct {
		Position Vec3
		UV       UV
		_        [8]byte
		Normal   Vec3
		Color    [4]byte
	}
	vertSize := uint32(unsafe.Sizeof(rawVertex))

	if ibsp.header.Version == iBSP_VER_v4 {
		vertLumpIdx = lUMP_v4_VERTICES
		var rawVertex struct {
			Position Vec3
			Normal   Vec3
			Color    [4]byte
			UV       UV
			_        [32]byte
		}
		vertSize = uint32(unsafe.Sizeof(rawVertex))
	}

	vertLump := ibsp.lumps[vertLumpIdx]

	_, err := f.Seek(int64(vertLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < vertLump.Length; i += vertSize {
		err = binary.Read(f, binary.LittleEndian, &rawVertex)
		if err != nil {
			return errorLogAndReturn(err)
		}

		ibsp.vertices = append(ibsp.vertices, IbspVertex{
			Position: rawVertex.Position,
			Normal:   rawVertex.Position,
			Color: Color{
				R: float32(rawVertex.Color[0]) / 255,
				G: float32(rawVertex.Color[1]) / 255,
				B: float32(rawVertex.Color[2]) / 255,
				A: float32(rawVertex.Color[3]) / 255,
			},
			UV: rawVertex.UV,
		})
	}

	return nil
}

// readTriangles
func (ibsp *IBSP) readTriangles(f *os.File) error {
	triLumpIdx := lUMP_v59_TRIANGLES
	if ibsp.header.Version == iBSP_VER_v4 {
		triLumpIdx = lUMP_v4_TRIANGLES
	}

	triLump := ibsp.lumps[triLumpIdx]
	triSize := uint32(unsafe.Sizeof(Triangle{}))

	_, err := f.Seek(int64(triLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < triLump.Length; i += triSize {
		tri := Triangle{}
		err := binary.Read(f, binary.LittleEndian, &tri)
		if err != nil {
			return errorLogAndReturn(err)
		}

		ibsp.triangles = append(ibsp.triangles, tri)
	}

	return nil
}

// readEntities
func (ibsp *IBSP) readEntities(f *os.File) error {
	entLumpIdx := lUMP_v59_ENTITIES
	if ibsp.header.Version == iBSP_VER_v4 {
		entLumpIdx = lUMP_v4_ENTITIES
	}

	entLump := ibsp.lumps[entLumpIdx]

	_, err := f.Seek(int64(entLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	entitiesData := make([]byte, entLump.Length)
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

	parseTransform := func(transform string, defaultValue float32) Vec3 {
		t := strings.Split(transform, " ")
		l := len(t)
		if l == 3 {
			return Vec3{
				X: parseFloat[float32](t[0]),
				Y: parseFloat[float32](t[1]),
				Z: parseFloat[float32](t[2]),
			}
		} else if l == 1 {
			if t[0] == "" {
				return Vec3{
					X: defaultValue,
					Y: defaultValue,
					Z: defaultValue,
				}
			}

			return Vec3{
				X: parseFloat[float32](t[0]),
				Y: parseFloat[float32](t[0]),
				Z: parseFloat[float32](t[0]),
			}
		}

		return Vec3{
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

		ibsp.Entities = append(ibsp.Entities, IbspEntity{
			Name:   name,
			Angles: parseTransform(ent.Angles, 0),
			Origin: parseTransform(ent.Origin, 0),
			Scale:  parseTransform(ent.ModelScale, 1),
		})
	}

	return nil
}

// loadSurfaces
func (ibsp *IBSP) loadSurfaces() {
	for _, ts := range ibsp.triangleSoups {
		surface := IbspSurface{
			Material: ibsp.materials[ts.MaterialIdx].getName(),
			Vertices: make(map[uint16]IbspVertex),
		}

		triCount := ts.TrianglesLength / 3
		for i := 0; i < int(triCount); i++ {
			triIdx := int(ts.TrianglesOffset)/3 + i
			tri := ibsp.triangles[triIdx]

			vertIdx1 := uint16(ts.VerticesOffset + uint32(tri.V1))
			vertIdx2 := uint16(ts.VerticesOffset + uint32(tri.V2))
			vertIdx3 := uint16(ts.VerticesOffset + uint32(tri.V3))

			surface.Triangles = append(surface.Triangles, Triangle{
				V1: vertIdx1,
				V2: vertIdx2,
				V3: vertIdx3,
			})

			surface.Vertices[vertIdx1] = ibsp.vertices[vertIdx1]
			surface.Vertices[vertIdx2] = ibsp.vertices[vertIdx2]
			surface.Vertices[vertIdx3] = ibsp.vertices[vertIdx3]

		}

		ibsp.Surfaces = append(ibsp.Surfaces, surface)
	}

}
