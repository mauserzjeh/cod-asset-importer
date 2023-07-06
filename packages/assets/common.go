package assets

import (
	"encoding/binary"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

type (
	vec3 struct {
		X float32
		Y float32
		Z float32
	}

	quat struct {
		X float32
		Y float32
		Z float32
		W float32
	}

	color struct {
		R float32
		G float32
		B float32
		A float32
	}

	uv struct {
		U float32
		V float32
	}

	triangle struct {
		V1 uint16
		V2 uint16
		V3 uint16
	}
)

const (
	VERSION_COD1 = 0x0E
	VERSION_COD2 = 0x14
	VERSION_COD4 = 0x19
)

// add
func (v vec3) add(o vec3) vec3 {
	return vec3{
		X: v.X + o.X,
		Y: v.Y + o.Y,
		Z: v.Z + o.Z,
	}
}

// div
func (v vec3) div(d float32) vec3 {
	return vec3{
		X: v.X / d,
		Y: v.Y / d,
		Z: v.Z / d,
	}
}

// transformVec
func (q quat) transformVec(v vec3) vec3 {
	a := vec3{
		X: q.Y*v.Z - q.Z*v.Y + v.X*q.W,
		Y: q.Z*v.X - q.X*v.Z + v.Y*q.W,
		Z: q.X*v.Y - q.Y*v.X + v.Z*q.W,
	}
	b := vec3{
		q.Y*a.Z - q.Z*a.Y,
		q.Z*a.X - q.X*a.Z,
		q.X*a.Y - q.Y*a.X,
	}
	return vec3{
		X: v.X + b.X + b.X,
		Y: v.Y + b.Y + b.Y,
		Z: v.Z + b.Z + b.Z,
	}
}

// multiply
func (q quat) multiply(o quat) quat {
	return quat{
		X: q.W*o.W - q.X*o.X - q.Y*o.Y - q.Z*o.Z,
		Y: q.W*o.X + q.X*o.W + q.Y*o.Z - q.Z*o.Y,
		Z: q.W*o.Y - q.X*o.Z + q.Y*o.W + q.Z*o.X,
		W: q.W*o.Z + q.X*o.Y - q.Y*o.X + q.Z*o.W,
	}
}

// parseFloat
func parseFloat[T float32 | float64](s string) T {
	var def T

	switch any(def).(type) {
	case float32:
		f, err := strconv.ParseFloat(s, 32)
		if err != nil {
			return def
		}

		return T(f)
	case float64:
		f, err := strconv.ParseFloat(s, 64)
		if err != nil {
			return def
		}

		return T(f)
	default:
		return def
	}
}

// fileNameWithoutExt
func fileNameWithoutExt(fileName string) string {
	base := path.Base(fileName)
	return strings.TrimSuffix(base, filepath.Ext(fileName))
}

// logMsg
func logMsg(label, format string, args ...any) {
	_, file, line, _ := runtime.Caller(2)
	fileBasePath := path.Base(file)
	msg := fmt.Sprintf(format, args...)
	log.Printf("[%v] %v:%v - %v", label, fileBasePath, line, msg)
}

// errorLog
func errorLog(err error) {
	logMsg("ERROR", fmt.Sprint(err))
}

// errorLogAndReturn
func errorLogAndReturn(err error) error {
	logMsg("ERROR", fmt.Sprint(err))
	return err
}

// infoLog
func infoLog(msg string, args ...any) {
	logMsg("INFO", msg, args...)
}

// debugLog
func debugLog(msg string, args ...any) {
	logMsg("DEBUG", msg, args...)
}

// readString
func readString(f *os.File) (string, error) {
	str := []byte{}

	for {
		var b byte
		err := binary.Read(f, binary.LittleEndian, &b)
		if err != nil && err != io.EOF {
			return "", err
		}

		if b == 0 {
			break
		}

		str = append(str, b)
	}

	return string(str), nil
}

// readPadding
func readPadding(f *os.File, amount int) error {
	pad := make([]byte, amount)
	_, err := f.Read(pad)
	if err != nil {
		return err
	}

	return nil
}

// unpack_565 unpacks a 565 color to RGB
func unpack_565(color uint32) (uint32, uint32, uint32) {
	r := (color & 0xF800) >> 8
	g := (color & 0x07E0) >> 3
	b := (color & 0x001F) << 3
	r |= r >> 5
	g |= g >> 6
	b |= b >> 5

	return r, g, b
}

// pack_rgba packs an RGBA color to a single 32 bit unsigned integer
func pack_rgba(r, g, b, a uint32) uint32 {
	return (r << 16) | (g << 8) | b | (a << 24)
}

// unpack_rgba unpacks a single 32 bit unsigned integer to RGBA
func unpack_rgba(c uint32) (uint32, uint32, uint32, uint32) {
	b := c & 0xFF
	g := (c >> 8) & 0xFF
	r := (c >> 16) & 0xFF
	a := (c >> 24) & 0xFF

	return r, g, b, a
}

// c2 creates a enw color
func c2(c0, c1, color0, color1 uint32) uint32 {
	if color0 > color1 {
		return (2*c0 + c1) / 3
	} else {
		return (c0 + c1) / 2
	}
}

// c3 creates a new color
func c3(c0, c1 uint32) uint32 {
	return (c0 + 2*c1) / 3
}

// decodeDXT1 decodes a DXT1 encoded byte slice to a RGBA byte slice
func decodeDXT1(input []byte, width, height uint) (output []byte, err error) {
	offset := uint(0)
	block_count_x := (width + 3) / 4
	block_count_y := (height + 3) / 4
	length_last := (width+3)%4 + 1
	buffer := make([]byte, 64)
	colors := make([]uint32, 4)
	output = make([]byte, width*height*4)

	defer func() {
		if r := recover(); r != nil {
			output = nil
			err = fmt.Errorf("%s", r)
		}
	}()

	for y := uint(0); y < block_count_y; y++ {
		for x := uint(0); x < block_count_x; x++ {
			c0 := uint32(input[offset+0]) | uint32(input[offset+1])<<8
			c1 := uint32(input[offset+2]) | uint32(input[offset+3])<<8

			r0, g0, b0 := unpack_565(c0)
			r1, g1, b1 := unpack_565(c1)

			colors[0] = pack_rgba(r0, g0, b0, 255)
			colors[1] = pack_rgba(r1, g1, b1, 255)
			colors[2] = pack_rgba(c2(r0, r1, c0, c1), c2(g0, g1, c0, c1), c2(b0, b1, c0, c1), 255)
			colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 255)

			bitcode := uint32(input[offset+4]) | uint32(input[offset+5])<<8 | uint32(input[offset+6])<<16 | uint32(input[offset+7])<<24
			for i := 0; i < 16; i++ {
				idx := i * 4
				r, g, b, a := unpack_rgba(colors[bitcode&0x3])
				buffer[idx+0] = byte(r)
				buffer[idx+1] = byte(g)
				buffer[idx+2] = byte(b)
				buffer[idx+3] = byte(a)

				bitcode >>= 2
			}

			length := length_last * 4
			if x < block_count_x-1 {
				length = 4 * 4
			}

			i := uint(0)
			j := y * 4
			for i < 4 && j < height {
				bidx := (i * 4 * 4)
				oidx := (j*width + x*4) * 4

				for k := uint(0); k < length; k++ {
					output[oidx+k] = buffer[bidx+k]
				}

				i++
				j++
			}

			offset += 8
		}
	}

	return output, nil
}

// decodeDXT3 decodes a DXT3 encoded byte slice to a RGBA byte slice
func decodeDXT3(input []byte, width, height uint) (output []byte, err error) {
	offset := uint(0)
	block_count_x := (width + 3) / 4
	block_count_y := (height + 3) / 4
	length_last := (width+3)%4 + 1
	buffer := make([]byte, 64)
	colors := make([]uint32, 4)
	alphas := make([]uint32, 16)
	output = make([]byte, width*height*4)

	defer func() {
		if r := recover(); r != nil {
			output = nil
			err = fmt.Errorf("%s", r)
		}
	}()

	for y := uint(0); y < block_count_y; y++ {
		for x := uint(0); x < block_count_x; x++ {
			for i := uint(0); i < 4; i++ {
				alpha := uint32(uint16(input[offset+i*2]) | uint16(input[offset+i*2+1])<<8)
				alphas[i*4+0] = (((alpha >> 0) & 0xF) * 0x11) << 24
				alphas[i*4+1] = (((alpha >> 4) & 0xF) * 0x11) << 24
				alphas[i*4+2] = (((alpha >> 8) & 0xF) * 0x11) << 24
				alphas[i*4+3] = (((alpha >> 12) & 0xF) * 0x11) << 24
			}

			c0 := uint32(uint16(input[offset+8]) | uint16(input[offset+9])<<8)
			c1 := uint32(uint16(input[offset+10]) | uint16(input[offset+11])<<8)

			r0, g0, b0 := unpack_565(c0)
			r1, g1, b1 := unpack_565(c1)

			colors[0] = pack_rgba(r0, g0, b0, 0)
			colors[1] = pack_rgba(r1, g1, b1, 0)
			colors[2] = pack_rgba(c2(r0, r1, c0, c1), c2(g0, g1, c0, c1), c2(b0, b1, c0, c1), 0)
			colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 0)

			bitcode := uint32(input[offset+12]) | uint32(input[offset+13])<<8 | uint32(input[offset+14])<<16 | uint32(input[offset+15])<<24
			for i := 0; i < 16; i++ {
				idx := i * 4
				r, g, b, a := unpack_rgba(colors[bitcode&0x3] | alphas[i])
				buffer[idx+0] = byte(r)
				buffer[idx+1] = byte(g)
				buffer[idx+2] = byte(b)
				buffer[idx+3] = byte(a)

				bitcode >>= 2
			}

			length := length_last * 4
			if x < block_count_x-1 {
				length = 4 * 4
			}

			i := uint(0)
			j := y * 4
			for i < 4 && j < height {
				bidx := (i * 4 * 4)
				oidx := (j*width + x*4) * 4

				for k := uint(0); k < length; k++ {
					output[oidx+k] = buffer[bidx+k]
				}

				i++
				j++
			}

			offset += 16
		}
	}

	return output, nil
}

// decodeDXT5 decodes a DXT5 encoded byte slice to a RGBA byte slice
func decodeDXT5(input []byte, width, height uint) (output []byte, err error) {
	offset := uint(0)
	block_count_x := (width + 3) / 4
	block_count_y := (height + 3) / 4
	length_last := (width+3)%4 + 1
	buffer := make([]byte, 64)
	colors := make([]uint32, 4)
	alphas := make([]uint32, 8)
	output = make([]byte, width*height*4)

	defer func() {
		if r := recover(); r != nil {
			output = nil
			err = fmt.Errorf("%s", r)
		}
	}()

	for y := uint(0); y < block_count_y; y++ {
		for x := uint(0); x < block_count_x; x++ {
			alphas[0] = uint32(input[offset+0])
			alphas[1] = uint32(input[offset+1])

			if alphas[0] > alphas[1] {
				alphas[2] = (alphas[0]*6 + alphas[1]) / 7
				alphas[3] = (alphas[0]*5 + alphas[1]*2) / 7
				alphas[4] = (alphas[0]*4 + alphas[1]*3) / 7
				alphas[5] = (alphas[0]*3 + alphas[1]*4) / 7
				alphas[6] = (alphas[0]*2 + alphas[1]*5) / 7
				alphas[7] = (alphas[0] + alphas[1]*6) / 7
			} else {
				alphas[2] = (alphas[0]*4 + alphas[1]) / 5
				alphas[3] = (alphas[0]*3 + alphas[1]*2) / 5
				alphas[4] = (alphas[0]*2 + alphas[1]*3) / 5
				alphas[5] = (alphas[0] + alphas[1]*4) / 5
				alphas[7] = 255
			}

			for i := 0; i < 8; i++ {
				alphas[i] <<= 24
			}

			c0 := uint32(uint16(input[offset+8]) | uint16(input[offset+9])<<8)
			c1 := uint32(uint16(input[offset+10]) | uint16(input[offset+11])<<8)

			r0, g0, b0 := unpack_565(c0)
			r1, g1, b1 := unpack_565(c1)

			colors[0] = pack_rgba(r0, g0, b0, 0)
			colors[1] = pack_rgba(r1, g1, b1, 0)
			colors[2] = pack_rgba(c2(r0, r1, c0, c1), c2(g0, g1, c0, c1), c2(b0, b1, c0, c1), 0)
			colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 0)

			bitcode_a := uint64(input[offset]) | uint64(input[offset+1])<<8 | uint64(input[offset+2])<<16 | uint64(input[offset+3])<<24 | uint64(input[offset+4])<<32 | uint64(input[offset+5])<<40 | uint64(input[offset+6])<<48 | uint64(input[offset+7])<<56
			bitcode_c := uint32(input[offset+12]) | uint32(input[offset+13])<<8 | uint32(input[offset+14])<<16 | uint32(input[offset+15])<<24

			for i := 0; i < 16; i++ {
				idx := i * 4
				r, g, b, a := unpack_rgba(alphas[bitcode_a&0x07] | colors[bitcode_c&0x03])
				buffer[idx+0] = byte(r)
				buffer[idx+1] = byte(g)
				buffer[idx+2] = byte(b)
				buffer[idx+3] = byte(a)

				bitcode_a >>= 3
				bitcode_c >>= 2
			}

			length := length_last * 4
			if x < block_count_x-1 {
				length = 4 * 4
			}

			i := uint(0)
			j := y * 4
			for i < 4 && j < height {
				bidx := (i * 4 * 4)
				oidx := (j*width + x*4) * 4

				for k := uint(0); k < length; k++ {
					output[oidx+k] = buffer[bidx+k]
				}

				i++
				j++
			}

			offset += 16
		}
	}

	return output, nil
}
