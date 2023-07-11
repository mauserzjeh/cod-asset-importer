package importer

import (
	"encoding/binary"
	"fmt"
	"os"
)

type (
	XModel struct {
		Name    string
		version uint16
		lods    []XModelLod
	}

	XModelLod struct {
		Name      string
		Distance  float32
		Materials []string
	}
)

const (
	xMODEL_TYPE_RIGID      = 0
	xMODEL_TYPE_ANIMATED   = 1
	xMODEL_TYPE_VIEWMODEL  = 2
	xMODEL_TYPE_PLAYERBODY = 3
	xMODEL_TYPE_VIEWHANDS  = 4
)

// load
func (xm *XModel) load(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	xm.Name = fileNameWithoutExt(filePath)

	err = binary.Read(f, binary.LittleEndian, &xm.version)
	if err != nil {
		return errorLogAndReturn(err)
	}

	switch xm.version {
	case VERSION_COD1:
		err := xm.loadV14(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD2:
		err := xm.loadV20(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD4:
		err := xm.loadV25(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	default:
		return fmt.Errorf("invalid xmodel version: %v", xm.version)
	}
}

// loadV14
func (xm *XModel) loadV14(f *os.File) error {
	err := readPadding(f, 24)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < 3; i++ {
		var lodDistance float32
		err := binary.Read(f, binary.LittleEndian, &lodDistance)
		if err != nil {
			return errorLogAndReturn(err)
		}

		lodName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		if len(lodName) == 0 {
			continue
		}

		xm.lods = append(xm.lods, XModelLod{
			Name:     lodName,
			Distance: lodDistance,
		})
	}

	err = readPadding(f, 4)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var padCount uint32
	err = binary.Read(f, binary.LittleEndian, &padCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(padCount); i++ {
		var subPaddingCount uint32
		err = binary.Read(f, binary.LittleEndian, &subPaddingCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		err = readPadding(f, int((subPaddingCount*48)+36))
		if err != nil {
			return errorLogAndReturn(err)
		}
	}

	for i := 0; i < len(xm.lods); i++ {
		var textureCount uint16
		err = binary.Read(f, binary.LittleEndian, &textureCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(textureCount); j++ {
			texture, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			xm.lods[i].Materials = append(xm.lods[i].Materials, texture)
		}
	}

	return nil
}

// loadV20
func (xm *XModel) loadV20(f *os.File) error {
	err := readPadding(f, 25)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < 4; i++ {
		var lodDistance float32
		err := binary.Read(f, binary.LittleEndian, &lodDistance)
		if err != nil {
			return errorLogAndReturn(err)
		}

		lodName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		if len(lodName) == 0 {
			continue
		}

		xm.lods = append(xm.lods, XModelLod{
			Name:     lodName,
			Distance: lodDistance,
		})
	}

	err = readPadding(f, 4)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var padCount uint32
	err = binary.Read(f, binary.LittleEndian, &padCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(padCount); i++ {
		var subPaddingCount uint32
		err = binary.Read(f, binary.LittleEndian, &subPaddingCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		err = readPadding(f, int((subPaddingCount*48)+36))
		if err != nil {
			return errorLogAndReturn(err)
		}
	}

	for i := 0; i < len(xm.lods); i++ {
		var materialCount uint16
		err = binary.Read(f, binary.LittleEndian, &materialCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(materialCount); j++ {
			material, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			xm.lods[i].Materials = append(xm.lods[i].Materials, material)
		}
	}

	return nil
}

// loadV25
func (xm *XModel) loadV25(f *os.File) error {
	err := readPadding(f, 26)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < 4; i++ {
		var lodDistance float32
		err := binary.Read(f, binary.LittleEndian, &lodDistance)
		if err != nil {
			return errorLogAndReturn(err)
		}

		lodName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		if len(lodName) == 0 {
			continue
		}

		xm.lods = append(xm.lods, XModelLod{
			Name:     lodName,
			Distance: lodDistance,
		})
	}

	err = readPadding(f, 4)
	if err != nil {
		return errorLogAndReturn(err)
	}

	var padCount uint32
	err = binary.Read(f, binary.LittleEndian, &padCount)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(padCount); i++ {
		var subPaddingCount uint32
		err = binary.Read(f, binary.LittleEndian, &subPaddingCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		err = readPadding(f, int((subPaddingCount*48)+36))
		if err != nil {
			return errorLogAndReturn(err)
		}
	}

	for i := 0; i < len(xm.lods); i++ {
		var materialCount uint16
		err = binary.Read(f, binary.LittleEndian, &materialCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(materialCount); j++ {
			material, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			xm.lods[i].Materials = append(xm.lods[i].Materials, material)
		}
	}

	return nil
}
