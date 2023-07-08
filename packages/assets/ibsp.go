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
		Vertices      []IbspVertex
		Triangles     []Triangle
		TriangleSoups []ibspTriangleSoup
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
func (s *ibspMaterial) getName() string {
	return string(bytes.Trim(s.Name[:], "\x00"))
}

// valid
func (s *ibspRawEntity) valid() (bool, string) {
	matches := validEntityModel.FindStringSubmatch(s.Model)
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
func (s *IBSP) Load(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	s.Name = fileNameWithoutExt(filePath)

	err = s.readHeader(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readLumps(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readMaterials(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readTriangleSoups(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readVertices(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readTriangles(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readEntities(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	s.loadSurfaces()

	return nil
}

// readHeader
func (s *IBSP) readHeader(f *os.File) error {
	err := binary.Read(f, binary.LittleEndian, &s.Header)
	if err != nil {
		return errorLogAndReturn(err)
	}

	if s.Header.Magic != [4]byte{'I', 'B', 'S', 'P'} {
		return fmt.Errorf("invalid magic: %s", string(s.Header.Magic[:]))
	}

	if s.Header.Version != IBSP_VER_v59 && s.Header.Version != IBSP_VER_v4 {
		return fmt.Errorf("invalid IBSP version: %v", s.Header.Version)
	}

	return nil
}

// readLumps
func (s *IBSP) readLumps(f *os.File) error {
	return binary.Read(f, binary.LittleEndian, &s.Lumps)
}

// readMaterials
func (s *IBSP) readMaterials(f *os.File) error {
	matLumpIdx := LUMP_v59_MATERIALS
	if s.Header.Version == IBSP_VER_v4 {
		matLumpIdx = LUMP_v4_MATERIALS
	}

	matLump := s.Lumps[matLumpIdx]
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

		s.Materials = append(s.Materials, material)
	}

	return nil
}

// readTriangleSoups
func (s *IBSP) readTriangleSoups(f *os.File) error {
	tsLumpIdx := LUMP_v59_TRIANGLESOUPS
	if s.Header.Version == IBSP_VER_v4 {
		tsLumpIdx = LUMP_v4_TRIANGLESOUPS
	}

	tsLump := s.Lumps[tsLumpIdx]
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

		s.TriangleSoups = append(s.TriangleSoups, triangleSoup)
	}

	return nil
}

// readVertices
func (s *IBSP) readVertices(f *os.File) error {
	vertLumpIdx := LUMP_v59_VERTICES
	var rawVertex struct {
		Position Vec3
		UV       UV
		_        [8]byte
		Normal   Vec3
		Color    [4]byte
	}
	vertSize := uint32(unsafe.Sizeof(rawVertex))

	if s.Header.Version == IBSP_VER_v4 {
		vertLumpIdx = LUMP_v4_VERTICES
		var rawVertex struct {
			Position Vec3
			Normal   Vec3
			Color    [4]byte
			UV       UV
			_        [32]byte
		}
		vertSize = uint32(unsafe.Sizeof(rawVertex))
	}

	vertLump := s.Lumps[vertLumpIdx]

	_, err := f.Seek(int64(vertLump.Offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	for i := uint32(0); i < vertLump.Length; i += vertSize {
		err = binary.Read(f, binary.LittleEndian, &rawVertex)
		if err != nil {
			return errorLogAndReturn(err)
		}

		s.Vertices = append(s.Vertices, IbspVertex{
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
func (s *IBSP) readTriangles(f *os.File) error {
	triLumpIdx := LUMP_v59_TRIANGLES
	if s.Header.Version == IBSP_VER_v4 {
		triLumpIdx = LUMP_v4_TRIANGLES
	}

	triLump := s.Lumps[triLumpIdx]
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

		s.Triangles = append(s.Triangles, tri)
	}

	return nil
}

// readEntities
func (s *IBSP) readEntities(f *os.File) error {
	entLumpIdx := LUMP_v59_ENTITIES
	if s.Header.Version == IBSP_VER_v4 {
		entLumpIdx = LUMP_v4_ENTITIES
	}

	entLump := s.Lumps[entLumpIdx]

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

		s.Entities = append(s.Entities, IbspEntity{
			Name:   name,
			Angles: parseTransform(ent.Angles, 0),
			Origin: parseTransform(ent.Origin, 0),
			Scale:  parseTransform(ent.ModelScale, 1),
		})
	}

	return nil
}

// loadSurfaces
func (s *IBSP) loadSurfaces() {
	for _, ts := range s.TriangleSoups {
		surface := IbspSurface{
			Material: s.Materials[ts.MaterialIdx].getName(),
			Vertices: make(map[uint16]IbspVertex),
		}

		triCount := ts.TrianglesLength / 3
		for i := 0; i < int(triCount); i++ {
			triIdx := int(ts.TrianglesOffset)/3 + i
			tri := s.Triangles[triIdx]

			vertIdx1 := uint16(ts.VerticesOffset + uint32(tri.V1))
			vertIdx2 := uint16(ts.VerticesOffset + uint32(tri.V2))
			vertIdx3 := uint16(ts.VerticesOffset + uint32(tri.V3))

			surface.Triangles = append(surface.Triangles, Triangle{
				V1: vertIdx1,
				V2: vertIdx2,
				V3: vertIdx3,
			})

			surface.Vertices[vertIdx1] = s.Vertices[vertIdx1]
			surface.Vertices[vertIdx2] = s.Vertices[vertIdx2]
			surface.Vertices[vertIdx3] = s.Vertices[vertIdx3]

		}

		s.Surfaces = append(s.Surfaces, surface)
	}

}
