package importer

import (
	"encoding/binary"
	"io"
	"os"
)

type (
	Material struct {
		techset  string
		Name     string
		textures []materialTexture
	}

	materialTexture struct {
		Type  string
		Flags uint32
		Name  string
	}
)

const (
	TEXTURE_TYPE_COLORMAP    = "colorMap"
	TEXTURE_TYPE_DETAILMAP   = "detailMap"
	TEXTURE_TYPE_NORMALMAP   = "normalMap"
	TEXTURE_TYPE_SPECULARMAP = "specularMap"
)

// Load
func (mat *Material) Load(filePath string, version int) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	mat.Name = fileNameWithoutExt(filePath)

	var nameOffset uint32
	err = binary.Read(f, binary.LittleEndian, &nameOffset)
	if err != nil {
		return errorLogAndReturn(err)
	}

	currentOffset, err := f.Seek(0, io.SeekCurrent)
	if err != nil {
		return errorLogAndReturn(err)
	}

	_, err = f.Seek(int64(nameOffset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}
	mat.Name, err = readString(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	_, err = f.Seek(currentOffset, io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}

	pad := 44
	if version == VERSION_COD2 {
		pad = 48
	}

	err = readPadding(f, pad)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var textureCount uint16
	err = binary.Read(f, binary.LittleEndian, &textureCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = readPadding(f, 2)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var techsetOffset uint32
	err = binary.Read(f, binary.LittleEndian, &techsetOffset)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var texturesOffset uint32
	err = binary.Read(f, binary.LittleEndian, &texturesOffset)
	if err != nil {
		return errorLogAndReturn(err)
	}

	_, err = f.Seek(int64(techsetOffset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}

	mat.techset, err = readString(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	_, err = f.Seek(int64(texturesOffset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(textureCount); i++ {
		t := materialTexture{}

		var textureTypeOffset uint32
		err = binary.Read(f, binary.LittleEndian, &textureTypeOffset)
		if err != nil {
			return errorLogAndReturn(err)
		}

		err = binary.Read(f, binary.LittleEndian, &t.Flags)
		if err != nil {
			return errorLogAndReturn(err)
		}

		var textureNameOffset uint32
		err = binary.Read(f, binary.LittleEndian, &textureNameOffset)
		if err != nil {
			return errorLogAndReturn(err)
		}

		currentOffset, err := f.Seek(0, io.SeekCurrent)
		if err != nil {
			return errorLogAndReturn(err)
		}

		_, err = f.Seek(int64(textureTypeOffset), io.SeekStart)
		if err != nil {
			return errorLogAndReturn(err)
		}

		t.Type, err = readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		_, err = f.Seek(int64(textureNameOffset), io.SeekStart)
		if err != nil {
			return errorLogAndReturn(err)
		}
		t.Name, err = readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		mat.textures = append(mat.textures, t)
		_, err = f.Seek(currentOffset, io.SeekStart)
		if err != nil {
			return errorLogAndReturn(err)
		}
	}

	return nil
}
