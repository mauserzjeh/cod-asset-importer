package assets

import (
	"encoding/binary"
	"errors"
	"fmt"
	"math"
	"os"
)

type (
	XModelPart struct {
		Name    string
		Version uint16
		Type    byte
		Bones   []xmodelPartBone
	}

	xmodelPartBone struct {
		Name           string
		Parent         int32
		LocalTransform xmodelPartBoneTransform
		WorldTransform xmodelPartBoneTransform
	}

	xmodelPartBoneTransform struct {
		Positon  Vec3
		Rotation Quat
	}
)

const (
	ROTATION_DIVISOR = 32768.0
	INCH_TO_CM       = 2.54
)

var (
	VIEWHAND_TABLE_COD1 = map[string]Vec3{
		"tag_view":           {X: 0.0, Y: 0.0, Z: 0.0},
		"tag_torso":          {X: 0.0, Y: 0.0, Z: 0.0},
		"tag_weapon":         {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l upperarm":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l forearm":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l hand":       {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger0":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger01":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger02":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger0nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger1":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger11":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger12":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger1nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger2":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger21":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger22":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger2nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger3":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger31":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger32":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger3nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger4":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger41":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger42":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 l finger4nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r upperarm":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r forearm":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r hand":       {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger0":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger01":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger02":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger0nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger1":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger11":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger12":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger1nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger2":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger21":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger22":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger2nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger3":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger31":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger32":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger3nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger4":    {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger41":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger42":   {X: 0.0, Y: 0.0, Z: 0.0},
		"bip01 r finger4nub": {X: 0.0, Y: 0.0, Z: 0.0},
		"l hand webbing":     {X: 0.0, Y: 0.0, Z: 0.0},
		"r hand webbing":     {X: 0.0, Y: 0.0, Z: 0.0},
		"r cuff":             {X: 0.0, Y: 0.0, Z: 0.0},
		"r cuff01":           {X: 0.0, Y: 0.0, Z: 0.0},
		"r wrist":            {X: 0.0, Y: 0.0, Z: 0.0},
		"r wrist01":          {X: 0.0, Y: 0.0, Z: 0.0},
	}

	VIEWHAND_TABLE_COD2 = map[string]Vec3{
		"tag_view":        {X: 0.0, Y: 0.0, Z: 0.0},
		"tag_torso":       {X: -11.76486, Y: 0.0, Z: -3.497466},
		"j_shoulder_le":   {X: 2.859542, Y: 20.16072, Z: -4.597286},
		"j_elbow_le":      {X: 30.7185, Y: -8e-06, Z: 3e-06},
		"j_wrist_le":      {X: 29.3906, Y: 1.9e-05, Z: -3e-06},
		"j_thumb_le_0":    {X: 2.786345, Y: 2.245192, Z: 0.85161},
		"j_thumb_le_1":    {X: 4.806596, Y: -1e-06, Z: 3e-06},
		"j_thumb_le_2":    {X: 2.433519, Y: -2e-06, Z: 1e-06},
		"j_thumb_le_3":    {X: 3.0, Y: -1e-06, Z: -1e-06},
		"j_flesh_le":      {X: 4.822557, Y: 1.176307, Z: -0.110341},
		"j_index_le_0":    {X: 10.53435, Y: 2.786251, Z: -3e-06},
		"j_index_le_1":    {X: 4.563, Y: -3e-06, Z: 1e-06},
		"j_index_le_2":    {X: 2.870304, Y: 3e-06, Z: -2e-06},
		"j_index_le_3":    {X: 2.999999, Y: 4e-06, Z: 1e-06},
		"j_mid_le_0":      {X: 10.71768, Y: 0.362385, Z: -0.38647},
		"j_mid_le_1":      {X: 4.842623, Y: -1e-06, Z: -1e-06},
		"j_mid_le_2":      {X: 2.957112, Y: -1e-06, Z: -1e-06},
		"j_mid_le_3":      {X: 3.000005, Y: 4e-06, Z: 0.0},
		"j_ring_le_0":     {X: 9.843364, Y: -1.747671, Z: -0.401116},
		"j_ring_le_1":     {X: 4.842618, Y: 4e-06, Z: -3e-06},
		"j_ring_le_2":     {X: 2.755294, Y: -2e-06, Z: 5e-06},
		"j_ring_le_3":     {X: 2.999998, Y: -2e-06, Z: -4e-06},
		"j_pinky_le_0":    {X: 8.613766, Y: -3.707476, Z: 0.16818},
		"j_pinky_le_1":    {X: 3.942609, Y: 1e-06, Z: 1e-06},
		"j_pinky_le_2":    {X: 1.794117, Y: 3e-06, Z: -3e-06},
		"j_pinky_le_3":    {X: 2.83939, Y: -1e-06, Z: 4e-06},
		"j_wristtwist_le": {X: 21.60379, Y: 1.2e-05, Z: -3e-06},
		"j_shoulder_ri":   {X: 2.859542, Y: -20.16072, Z: -4.597286},
		"j_elbow_ri":      {X: -30.71852, Y: 4e-06, Z: -2.4e-05},
		"j_wrist_ri":      {X: -29.39067, Y: 4.4e-05, Z: 2.2e-05},
		"j_thumb_ri_0":    {X: -2.786155, Y: -2.245166, Z: -0.851634},
		"j_thumb_ri_1":    {X: -4.806832, Y: -6.6e-05, Z: 0.000141},
		"j_thumb_ri_2":    {X: -2.433458, Y: -3.8e-05, Z: -5.3e-05},
		"j_thumb_ri_3":    {X: -3.000123, Y: 0.00016, Z: 2.5e-05},
		"j_flesh_ri":      {X: -4.822577, Y: -1.176315, Z: 0.110318},
		"j_index_ri_0":    {X: -10.53432, Y: -2.786281, Z: -7e-06},
		"j_index_ri_1":    {X: -4.562927, Y: -5.8e-05, Z: 5.4e-05},
		"j_index_ri_2":    {X: -2.870313, Y: -6.5e-05, Z: 0.0001},
		"j_index_ri_3":    {X: -2.999938, Y: 0.000165, Z: -6.5e-05},
		"j_mid_ri_0":      {X: -10.71752, Y: -0.362501, Z: 0.386463},
		"j_mid_ri_1":      {X: -4.842728, Y: 0.000151, Z: 2.8e-05},
		"j_mid_ri_2":      {X: -2.957152, Y: -8.7e-05, Z: -2.2e-05},
		"j_mid_ri_3":      {X: -3.00006, Y: -6.8e-05, Z: -1.9e-05},
		"j_ring_ri_0":     {X: -9.843175, Y: 1.747613, Z: 0.401109},
		"j_ring_ri_1":     {X: -4.842774, Y: 0.000176, Z: -6.3e-05},
		"j_ring_ri_2":     {X: -2.755269, Y: -1.1e-05, Z: 0.000149},
		"j_ring_ri_3":     {X: -3.000048, Y: -4.1e-05, Z: -4.9e-05},
		"j_pinky_ri_0":    {X: -8.613756, Y: 3.707438, Z: -0.168202},
		"j_pinky_ri_1":    {X: -3.942537, Y: -0.000117, Z: -6.5e-05},
		"j_pinky_ri_2":    {X: -1.794038, Y: 0.000134, Z: 0.000215},
		"j_pinky_ri_3":    {X: -2.839375, Y: 5.6e-05, Z: -0.000115},
		"j_wristtwist_ri": {X: -21.60388, Y: 9.7e-05, Z: 8e-06},
		"tag_weapon":      {X: 38.5059, Y: 0.0, Z: -17.15191},
		"tag_cambone":     {X: 0.0, Y: 0.0, Z: 0.0},
		"tag_camera":      {X: 0.0, Y: 0.0, Z: 0.0},
	}
)

// genWorlTransformByParent
func (s *xmodelPartBone) genWorlTransformByParent(parent xmodelPartBone) {
	s.WorldTransform.Positon = parent.WorldTransform.Positon.add(parent.WorldTransform.Rotation.transformVec(s.LocalTransform.Positon))
	s.WorldTransform.Rotation = parent.WorldTransform.Rotation.multiply(s.LocalTransform.Rotation)
}

// Load
func (s *XModelPart) Load(filePath string) error {
	f, err := os.Open(filePath)
	if err != nil {
		return errorLogAndReturn(err)
	}
	defer f.Close()

	s.Name = fileNameWithoutExt(filePath)
	l := len(s.Name)
	if l == 0 {
		return errors.New("empty xmodelpart name")
	}
	s.Type = s.Name[l-1]

	err = binary.Read(f, binary.LittleEndian, &s.Version)
	if err != nil {
		return errorLogAndReturn(err)
	}

	switch s.Version {
	case VERSION_COD1:
		err := s.loadV14(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD2:
		err := s.loadV20(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	case VERSION_COD4:
		err := s.loadV25(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		return nil
	default:
		return fmt.Errorf("invalid xmodelpart version: %v", s.Version)
	}
}

// loadV14
func (s *XModelPart) loadV14(f *os.File) error {
	var boneHeader struct {
		BoneCount     uint16
		RootBoneCount uint16
	}
	err := binary.Read(f, binary.LittleEndian, &boneHeader)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(boneHeader.RootBoneCount); i++ {
		s.Bones = append(s.Bones, xmodelPartBone{
			Parent: -1,
		})
	}

	for i := 0; i < int(boneHeader.BoneCount); i++ {
		var rawBoneData struct {
			Parent int8
			Px     float32
			Py     float32
			Pz     float32
			Rx     uint16
			Ry     uint16
			Rz     uint16
		}

		err = binary.Read(f, binary.LittleEndian, &rawBoneData)
		if err != nil {
			return errorLogAndReturn(err)
		}

		qx := float32(rawBoneData.Rx) / ROTATION_DIVISOR
		qy := float32(rawBoneData.Ry) / ROTATION_DIVISOR
		qz := float32(rawBoneData.Rz) / ROTATION_DIVISOR
		qw := float32(math.Sqrt((1 - float64(qx*qx) - float64(qy*qy) - float64(qz*qz))))

		boneTransform := xmodelPartBoneTransform{
			Rotation: Quat{
				X: qx,
				Y: qy,
				Z: qz,
				W: qw,
			},
			Positon: Vec3{
				X: rawBoneData.Px,
				Y: rawBoneData.Py,
				Z: rawBoneData.Pz,
			},
		}

		s.Bones = append(s.Bones, xmodelPartBone{
			Name:           "",
			Parent:         int32(rawBoneData.Parent),
			LocalTransform: boneTransform,
			WorldTransform: boneTransform,
		})
	}

	for i := 0; i < int(boneHeader.RootBoneCount+boneHeader.BoneCount); i++ {
		currentBone := s.Bones[i]

		boneName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		currentBone.Name = boneName

		err = readPadding(f, 24)
		if err != nil {
			return errorLogAndReturn(err)
		}

		if localViewModelPos, ok := VIEWHAND_TABLE_COD1[boneName]; s.Type == XMODEL_TYPE_VIEWHANDS && ok {
			currentBone.LocalTransform.Positon = localViewModelPos.div(INCH_TO_CM)
			currentBone.WorldTransform.Positon = localViewModelPos.div(INCH_TO_CM)
		}

		if currentBone.Parent > -1 {
			parentBone := s.Bones[currentBone.Parent]
			currentBone.genWorlTransformByParent(parentBone)
		}
	}

	return nil
}

// loadV20
func (s *XModelPart) loadV20(f *os.File) error {
	var boneHeader struct {
		BoneCount     uint16
		RootBoneCount uint16
	}
	err := binary.Read(f, binary.LittleEndian, &boneHeader)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(boneHeader.RootBoneCount); i++ {
		s.Bones = append(s.Bones, xmodelPartBone{
			Parent: -1,
		})
	}

	for i := 0; i < int(boneHeader.BoneCount); i++ {
		var rawBoneData struct {
			Parent int8
			Px     float32
			Py     float32
			Pz     float32
			Rx     uint16
			Ry     uint16
			Rz     uint16
		}

		err = binary.Read(f, binary.LittleEndian, &rawBoneData)
		if err != nil {
			return errorLogAndReturn(err)
		}

		qx := float32(rawBoneData.Rx) / ROTATION_DIVISOR
		qy := float32(rawBoneData.Ry) / ROTATION_DIVISOR
		qz := float32(rawBoneData.Rz) / ROTATION_DIVISOR
		qw := float32(math.Sqrt((1 - float64(qx*qx) - float64(qy*qy) - float64(qz*qz))))

		boneTransform := xmodelPartBoneTransform{
			Rotation: Quat{
				X: qx,
				Y: qy,
				Z: qz,
				W: qw,
			},
			Positon: Vec3{
				X: rawBoneData.Px,
				Y: rawBoneData.Py,
				Z: rawBoneData.Pz,
			},
		}

		s.Bones = append(s.Bones, xmodelPartBone{
			Name:           "",
			Parent:         int32(rawBoneData.Parent),
			LocalTransform: boneTransform,
			WorldTransform: boneTransform,
		})
	}

	for i := 0; i < int(boneHeader.RootBoneCount+boneHeader.BoneCount); i++ {
		currentBone := s.Bones[i]

		boneName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		currentBone.Name = boneName

		if localViewModelPos, ok := VIEWHAND_TABLE_COD2[boneName]; s.Type == XMODEL_TYPE_VIEWHANDS && ok {
			currentBone.LocalTransform.Positon = localViewModelPos.div(INCH_TO_CM)
			currentBone.WorldTransform.Positon = localViewModelPos.div(INCH_TO_CM)
		}

		if currentBone.Parent > -1 {
			parentBone := s.Bones[currentBone.Parent]
			currentBone.genWorlTransformByParent(parentBone)
		}
	}

	return nil
}

// loadV25
func (s *XModelPart) loadV25(f *os.File) error {
	var boneHeader struct {
		BoneCount     uint16
		RootBoneCount uint16
	}
	err := binary.Read(f, binary.LittleEndian, &boneHeader)
	if err != nil {
		return errorLogAndReturn(err)
	}

	for i := 0; i < int(boneHeader.RootBoneCount); i++ {
		s.Bones = append(s.Bones, xmodelPartBone{
			Parent: -1,
		})
	}

	for i := 0; i < int(boneHeader.BoneCount); i++ {
		var rawBoneData struct {
			Parent int8
			Px     float32
			Py     float32
			Pz     float32
			Rx     uint16
			Ry     uint16
			Rz     uint16
		}

		err = binary.Read(f, binary.LittleEndian, &rawBoneData)
		if err != nil {
			return errorLogAndReturn(err)
		}

		qx := float32(rawBoneData.Rx) / ROTATION_DIVISOR
		qy := float32(rawBoneData.Ry) / ROTATION_DIVISOR
		qz := float32(rawBoneData.Rz) / ROTATION_DIVISOR
		qw := float32(math.Sqrt((1 - float64(qx*qx) - float64(qy*qy) - float64(qz*qz))))

		boneTransform := xmodelPartBoneTransform{
			Rotation: Quat{
				X: qx,
				Y: qy,
				Z: qz,
				W: qw,
			},
			Positon: Vec3{
				X: rawBoneData.Px,
				Y: rawBoneData.Py,
				Z: rawBoneData.Pz,
			},
		}

		s.Bones = append(s.Bones, xmodelPartBone{
			Name:           "",
			Parent:         int32(rawBoneData.Parent),
			LocalTransform: boneTransform,
			WorldTransform: boneTransform,
		})
	}

	for i := 0; i < int(boneHeader.RootBoneCount+boneHeader.BoneCount); i++ {
		currentBone := s.Bones[i]

		boneName, err := readString(f)
		if err != nil {
			return errorLogAndReturn(err)
		}

		currentBone.Name = boneName

		if currentBone.Parent > -1 {
			parentBone := s.Bones[currentBone.Parent]
			currentBone.genWorlTransformByParent(parentBone)
		}
	}

	return nil
}
