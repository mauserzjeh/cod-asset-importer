package assets

import (
	"encoding/binary"
	"fmt"
	"os"
)

type (
	XModel struct {
		Name    string
		Version uint16
		Lods    []XModelLod
	}

	XModelLod struct {
		Name     string
		Distance float32
		Textures []string
	}
)

const (
	XMODEL_TYPE_RIGID      = 0
	XMODEL_TYPE_ANIMATED   = 1
	XMODEL_TYPE_VIEWMODEL  = 2
	XMODEL_TYPE_PLAYERBODY = 3
	XMODEL_TYPE_VIEWHANDS  = 4
)

// Load
func (self *XModel) Load(filePath string) error {
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
		err := self.loadV14(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD2:
		err := self.loadV20(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD4:
		err := self.loadV25(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	default:
		return fmt.Errorf("invalid xmodel version: %v", self.Version)
	}
}

// loadV14
func (self *XModel) loadV14(f *os.File) error {
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

		self.Lods = append(self.Lods, XModelLod{
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

	for i := 0; i < len(self.Lods); i++ {
		var materialCount uint16
		err = binary.Read(f, binary.LittleEndian, &materialCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(materialCount); j++ {
			texture, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			self.Lods[i].Textures = append(self.Lods[i].Textures, texture)
		}
	}

	return nil
}

// loadV20
func (self *XModel) loadV20(f *os.File) error {
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

		self.Lods = append(self.Lods, XModelLod{
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

	for i := 0; i < len(self.Lods); i++ {
		var materialCount uint16
		err = binary.Read(f, binary.LittleEndian, &materialCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(materialCount); j++ {
			texture, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			self.Lods[i].Textures = append(self.Lods[i].Textures, texture)
		}
	}

	return nil
}

// loadV25
func (self *XModel) loadV25(f *os.File) error {
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

		self.Lods = append(self.Lods, XModelLod{
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

	for i := 0; i < len(self.Lods); i++ {
		var materialCount uint16
		err = binary.Read(f, binary.LittleEndian, &materialCount)
		if err != nil {
			return errorLogAndReturn(err)
		}

		for j := 0; j < int(materialCount); j++ {
			texture, err := readString(f)
			if err != nil {
				return errorLogAndReturn(err)
			}

			self.Lods[i].Textures = append(self.Lods[i].Textures, texture)
		}
	}

	return nil
}
