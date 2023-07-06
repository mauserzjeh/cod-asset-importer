package assets

import (
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"sort"
)

type (
	IWI struct {
		Header  iwiHeader
		Info    iwiInfo
		Data    []byte
		RawData []byte
	}

	iwiHeader struct {
		Magic   [3]byte
		Version byte
	}

	iwiInfo struct {
		Format byte
		Usage  byte
		Width  uint16
		Height uint16
		Depth  uint16
	}

	iwiMipmapOffsets []int32
	iwiMipmap        struct {
		offset int32
		size   int32
	}
	iwiMipmaps []iwiMipmap
)

const (
	// IWI Versions
	IWI_VERSION_COD2 = 0x05 // CoD2
	IWI_VERSION_COD4 = 0x06 // CoD4
	IWI_VERSION_COD5 = 0x06 // CoD5

	// IWI Format
	IWI_FORMAT_ARGB32 = 0x01 // ARGB32
	IWI_FORMAT_RGB24  = 0x02 // RGB24
	IWI_FORMAT_GA16   = 0x03 // GA16
	IWI_FORMAT_A8     = 0x04 // A8
	IWI_FORMAT_DXT1   = 0x0B // DXT1
	IWI_FORMAT_DXT3   = 0x0C // DXT3
	IWI_FORMAT_DXT5   = 0x0D // DXT5
)

// mipMaps calculate mipmap offsets and sizes from the given offsets
func (s iwiMipmapOffsets) mipMaps(first int32, size int32) iwiMipmaps {
	m := make(iwiMipmaps, len(s))

	for i := 0; i < len(s); i++ {
		switch i {
		case 0:
			m[i] = iwiMipmap{
				offset: s[i],
				size:   size - s[i],
			}

		case len(s) - 1:
			m[i] = iwiMipmap{
				offset: first,
				size:   s[i] - first,
			}

		default:
			m[i] = iwiMipmap{
				offset: s[i],
				size:   s[i-1] - s[i],
			}
		}
	}

	return m
}

func (s iwiMipmaps) Len() int           { return len(s) }                // Sort interface - Len
func (s iwiMipmaps) Less(i, j int) bool { return s[i].size < s[j].size } // Sort interface-  Less
func (s iwiMipmaps) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }      // Sort interface - Swap

// Load
func (s *IWI) Load(filepath string) error {
	f, err := os.Open(filepath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	err = s.readHeader(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	err = s.readInfo(f)
	if err != nil {
		return errorLogAndReturn(err)
	}

	ofs := make(iwiMipmapOffsets, 4)
	err = binary.Read(f, binary.LittleEndian, &ofs)
	if err != nil {
		return errorLogAndReturn(err)
	}

	curr, err := f.Seek(0, io.SeekCurrent)
	if err != nil {
		return errorLogAndReturn(err)
	}

	stat, err := f.Stat()
	if err != nil {
		return errorLogAndReturn(err)
	}

	size := stat.Size()
	mms := ofs.mipMaps(int32(curr), int32(size))
	sort.Sort(sort.Reverse(mms))
	mm := mms[0]

	_, err = f.Seek(int64(mm.offset), io.SeekStart)
	if err != nil {
		return errorLogAndReturn(err)
	}

	data := make([]byte, mm.size)
	err = binary.Read(f, binary.LittleEndian, &data)
	if err != nil {
		return errorLogAndReturn(err)
	}

	s.Data = data
	err = s.decodeData()
	if err != nil {
		return errorLogAndReturn(err)
	}
	return nil
}

// readHeader
func (s *IWI) readHeader(f *os.File) error {
	err := binary.Read(f, binary.LittleEndian, &s.Header)
	if err != nil {
		return errorLogAndReturn(err)
	}

	if s.Header.Magic != [3]byte{'I', 'W', 'i'} {
		return fmt.Errorf("invalid magic: %s", string(s.Header.Magic[:]))
	}

	supportedVersions := []uint8{
		IWI_VERSION_COD2,
		IWI_VERSION_COD4,
		IWI_VERSION_COD5,
	}

	supported := false
	for _, sv := range supportedVersions {
		if sv == s.Header.Version {
			supported = true
			break
		}
	}

	if !supported {
		return fmt.Errorf("invalid IWi version: %v", s.Header.Version)
	}

	return nil
}

// readInfo
func (s *IWI) readInfo(f *os.File) error {
	err := binary.Read(f, binary.LittleEndian, &s.Info)
	if err != nil {
		return errorLogAndReturn(err)
	}
	return nil
}

// decodeData
func (s *IWI) decodeData() error {
	var err error
	switch s.Info.Format {
	case IWI_FORMAT_DXT1:
		s.RawData, err = decodeDXT1(s.Data, uint(s.Info.Width), uint(s.Info.Height))
		if err != nil {
			return errorLogAndReturn(err)
		}
		return nil
	case IWI_FORMAT_DXT3:
		s.RawData, err = decodeDXT3(s.Data, uint(s.Info.Width), uint(s.Info.Height))
		if err != nil {
			return errorLogAndReturn(err)
		}
		return nil
	case IWI_FORMAT_DXT5:
		s.RawData, err = decodeDXT5(s.Data, uint(s.Info.Width), uint(s.Info.Height))
		if err != nil {
			return errorLogAndReturn(err)
		}
		return nil
	default:
		return fmt.Errorf("unsupported decode format: %v", s.Info.Format)
	}
}
