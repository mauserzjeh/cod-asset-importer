use super::xmodel::{XModelType, XModelVersion};
use crate::utils::{
    binary,
    error::Error,
    math::{quat_multiply, vec3_add, vec3_div, vec3_from_vec, vec3_rotate, Quat, Vec3},
    path::file_name_without_ext,
    Result,
};
use std::{fs::File, path::PathBuf};

pub const ASSETPATH: &str = "xmodelparts";
const ROTATION_DIVISOR: f32 = 32768.0;
const INCH_TO_CM: f32 = 2.54;

#[derive(Clone)]
pub struct XModelPart {
    pub name: String,
    pub version: u16,
    pub model_type: u8,
    pub bones: Vec<XModelPartBone>,
}

#[derive(Clone)]
pub struct XModelPartBone {
    pub name: String,
    pub parent: i8,
    pub local_transform: XModelPartBoneTransform,
    pub world_transform: XModelPartBoneTransform,
}

#[derive(Clone, Copy)]
pub struct XModelPartBoneTransform {
    pub position: Vec3,
    pub rotation: Quat,
}

impl XModelPart {
    fn viewhand_table_cod1(bone_name: &str) -> Option<Vec3> {
        match bone_name {
            "tag_view" => Some([0.0, 0.0, 0.0]),
            "tag_torso" => Some([0.0, 0.0, 0.0]),
            "tag_weapon" => Some([0.0, 0.0, 0.0]),
            "bip01 l upperarm" => Some([0.0, 0.0, 0.0]),
            "bip01 l forearm" => Some([0.0, 0.0, 0.0]),
            "bip01 l hand" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger0" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger01" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger02" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger0nub" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger1" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger11" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger12" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger1nub" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger2" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger21" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger22" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger2nub" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger3" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger31" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger32" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger3nub" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger4" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger41" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger42" => Some([0.0, 0.0, 0.0]),
            "bip01 l finger4nub" => Some([0.0, 0.0, 0.0]),
            "bip01 r upperarm" => Some([0.0, 0.0, 0.0]),
            "bip01 r forearm" => Some([0.0, 0.0, 0.0]),
            "bip01 r hand" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger0" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger01" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger02" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger0nub" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger1" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger11" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger12" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger1nub" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger2" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger21" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger22" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger2nub" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger3" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger31" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger32" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger3nub" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger4" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger41" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger42" => Some([0.0, 0.0, 0.0]),
            "bip01 r finger4nub" => Some([0.0, 0.0, 0.0]),
            "l hand webbing" => Some([0.0, 0.0, 0.0]),
            "r hand webbing" => Some([0.0, 0.0, 0.0]),
            "r cuff" => Some([0.0, 0.0, 0.0]),
            "r cuff01" => Some([0.0, 0.0, 0.0]),
            "r wrist" => Some([0.0, 0.0, 0.0]),
            "r wrist01" => Some([0.0, 0.0, 0.0]),
            _ => None,
        }
    }

    fn viewhand_table_cod2(bone_name: &str) -> Option<Vec3> {
        match bone_name {
            "tag_view" => Some([0.0, 0.0, 0.0]),
            "tag_torso" => Some([-11.76486, 0.0, -3.497466]),
            "j_shoulder_le" => Some([2.859542, 20.16072, -4.597286]),
            "j_elbow_le" => Some([30.7185, -8E-06, 3E-06]),
            "j_wrist_le" => Some([29.3906, 1.9E-05, -3E-06]),
            "j_thumb_le_0" => Some([2.786345, 2.245192, 0.85161]),
            "j_thumb_le_1" => Some([4.806596, -1E-06, 3E-06]),
            "j_thumb_le_2" => Some([2.433519, -2E-06, 1E-06]),
            "j_thumb_le_3" => Some([3.0, -1E-06, -1E-06]),
            "j_flesh_le" => Some([4.822557, 1.176307, -0.110341]),
            "j_index_le_0" => Some([10.53435, 2.786251, -3E-06]),
            "j_index_le_1" => Some([4.563, -3E-06, 1E-06]),
            "j_index_le_2" => Some([2.870304, 3E-06, -2E-06]),
            "j_index_le_3" => Some([2.999999, 4E-06, 1E-06]),
            "j_mid_le_0" => Some([10.71768, 0.362385, -0.38647]),
            "j_mid_le_1" => Some([4.842623, -1E-06, -1E-06]),
            "j_mid_le_2" => Some([2.957112, -1E-06, -1E-06]),
            "j_mid_le_3" => Some([3.000005, 4E-06, 0.0]),
            "j_ring_le_0" => Some([9.843364, -1.747671, -0.401116]),
            "j_ring_le_1" => Some([4.842618, 4E-06, -3E-06]),
            "j_ring_le_2" => Some([2.755294, -2E-06, 5E-06]),
            "j_ring_le_3" => Some([2.999998, -2E-06, -4E-06]),
            "j_pinky_le_0" => Some([8.613766, -3.707476, 0.16818]),
            "j_pinky_le_1" => Some([3.942609, 1E-06, 1E-06]),
            "j_pinky_le_2" => Some([1.794117, 3E-06, -3E-06]),
            "j_pinky_le_3" => Some([2.83939, -1E-06, 4E-06]),
            "j_wristtwist_le" => Some([21.60379, 1.2E-05, -3E-06]),
            "j_shoulder_ri" => Some([2.859542, -20.16072, -4.597286]),
            "j_elbow_ri" => Some([-30.71852, 4E-06, -2.4E-05]),
            "j_wrist_ri" => Some([-29.39067, 4.4E-05, 2.2E-05]),
            "j_thumb_ri_0" => Some([-2.786155, -2.245166, -0.851634]),
            "j_thumb_ri_1" => Some([-4.806832, -6.6E-05, 0.000141]),
            "j_thumb_ri_2" => Some([-2.433458, -3.8E-05, -5.3E-05]),
            "j_thumb_ri_3" => Some([-3.000123, 0.00016, 2.5E-05]),
            "j_flesh_ri" => Some([-4.822577, -1.176315, 0.110318]),
            "j_index_ri_0" => Some([-10.53432, -2.786281, -7E-06]),
            "j_index_ri_1" => Some([-4.562927, -5.8E-05, 5.4E-05]),
            "j_index_ri_2" => Some([-2.870313, -6.5E-05, 0.0001]),
            "j_index_ri_3" => Some([-2.999938, 0.000165, -6.5E-05]),
            "j_mid_ri_0" => Some([-10.71752, -0.362501, 0.386463]),
            "j_mid_ri_1" => Some([-4.842728, 0.000151, 2.8E-05]),
            "j_mid_ri_2" => Some([-2.957152, -8.7E-05, -2.2E-05]),
            "j_mid_ri_3" => Some([-3.00006, -6.8E-05, -1.9E-05]),
            "j_ring_ri_0" => Some([-9.843175, 1.747613, 0.401109]),
            "j_ring_ri_1" => Some([-4.842774, 0.000176, -6.3E-05]),
            "j_ring_ri_2" => Some([-2.755269, -1.1E-05, 0.000149]),
            "j_ring_ri_3" => Some([-3.000048, -4.1E-05, -4.9E-05]),
            "j_pinky_ri_0" => Some([-8.613756, 3.707438, -0.168202]),
            "j_pinky_ri_1" => Some([-3.942537, -0.000117, -6.5E-05]),
            "j_pinky_ri_2" => Some([-1.794038, 0.000134, 0.000215]),
            "j_pinky_ri_3" => Some([-2.839375, 5.6E-05, -0.000115]),
            "j_wristtwist_ri" => Some([-21.60388, 9.7E-05, 8E-06]),
            "tag_weapon" => Some([38.5059, 0.0, -17.15191]),
            "tag_cambone" => Some([0.0, 0.0, 0.0]),
            "tag_camera" => Some([0.0, 0.0, 0.0]),
            _ => None,
        }
    }

    pub fn load(file_path: PathBuf) -> Result<XModelPart> {
        let mut file = File::open(&file_path)?;
        let name = file_name_without_ext(file_path);
        let version = binary::read::<u16>(&mut file)?;
        let model_type = match name.chars().last() {
            Some(model_type) => model_type as u8,
            None => return Err(Error::new("empty xmodelpart name".to_string())),
        };
        let mut xmodel_part = XModelPart {
            name,
            version,
            model_type,
            bones: Vec::new(),
        };

        match XModelVersion::valid(version) {
            Some(XModelVersion::V14) => {
                xmodel_part.load_v14(&mut file)?;
                Ok(xmodel_part)
            }
            Some(XModelVersion::V20) => {
                xmodel_part.load_v20(&mut file)?;
                Ok(xmodel_part)
            }
            Some(XModelVersion::V25) => {
                xmodel_part.load_v25(&mut file)?;
                Ok(xmodel_part)
            }
            Some(XModelVersion::V62) => {
                xmodel_part.load_v62(&mut file)?;
                Ok(xmodel_part)
            }
            None => Err(Error::new(format!(
                "invalid xmodelpart version {}",
                version
            ))),
        }
    }

    fn load_v14(&mut self, file: &mut File) -> Result<()> {
        let bone_header = binary::read_vec::<u16>(file, 2)?;
        let bone_count = bone_header[0];
        let root_bone_count = bone_header[1];

        for _ in 0..root_bone_count {
            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent: -1,
                local_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
                world_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
            });
        }

        for _ in 0..bone_count {
            let parent = binary::read::<i8>(file)?;
            let position = binary::read_vec::<f32>(file, 3)?;
            let rotation = binary::read_vec::<i16>(file, 3)?;

            let qx = (rotation[0] as f32) / ROTATION_DIVISOR;
            let qy = (rotation[1] as f32) / ROTATION_DIVISOR;
            let qz = (rotation[2] as f32) / ROTATION_DIVISOR;
            let qw = f32::sqrt((1.0 - (qx * qx) - (qy * qy) - (qz * qz)).max(0.0));

            let bone_transform = XModelPartBoneTransform {
                position: vec3_from_vec(position).unwrap(),
                rotation: [qw, qx, qy, qz],
            };

            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent,
                local_transform: bone_transform,
                world_transform: bone_transform,
            })
        }

        for i in 0..root_bone_count + bone_count {
            let mut current_bone = self.bones[i as usize].to_owned();
            let bone_name = binary::read_string(file)?;
            current_bone.name = bone_name.clone();

            binary::skip(file, 24)?;

            if self.model_type == XModelType::Viewhands as u8 {
                if let Some(viewmodel_pos) = Self::viewhand_table_cod1(bone_name.as_str()) {
                    current_bone.local_transform.position = vec3_div(viewmodel_pos, INCH_TO_CM);
                    current_bone.world_transform.position = vec3_div(viewmodel_pos, INCH_TO_CM);
                }
            }

            if current_bone.parent > -1 {
                let parent_bone = self.bones[current_bone.parent as usize].to_owned();
                current_bone.generate_world_transform_by_parent(parent_bone);
            }

            self.bones[i as usize] = current_bone;
        }

        Ok(())
    }
    fn load_v20(&mut self, file: &mut File) -> Result<()> {
        let bone_header = binary::read_vec::<u16>(file, 2)?;
        let bone_count = bone_header[0];
        let root_bone_count = bone_header[1];

        for _ in 0..root_bone_count {
            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent: -1,
                local_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
                world_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
            });
        }

        for _ in 0..bone_count {
            let parent = binary::read::<i8>(file)?;
            let position = binary::read_vec::<f32>(file, 3)?;
            let rotation = binary::read_vec::<i16>(file, 3)?;

            let qx = (rotation[0] as f32) / ROTATION_DIVISOR;
            let qy = (rotation[1] as f32) / ROTATION_DIVISOR;
            let qz = (rotation[2] as f32) / ROTATION_DIVISOR;
            let qw = f32::sqrt((1.0 - (qx * qx) - (qy * qy) - (qz * qz)).max(0.0));

            let bone_transform = XModelPartBoneTransform {
                position: vec3_from_vec(position).unwrap(),
                rotation: [qw, qx, qy, qz],
            };

            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent,
                local_transform: bone_transform,
                world_transform: bone_transform,
            })
        }

        for i in 0..root_bone_count + bone_count {
            let mut current_bone = self.bones[i as usize].to_owned();
            let bone_name = binary::read_string(file)?;
            current_bone.name = bone_name.clone();

            if self.model_type == XModelType::Viewhands as u8 {
                if let Some(viewmodel_pos) = Self::viewhand_table_cod2(bone_name.as_str()) {
                    current_bone.local_transform.position = vec3_div(viewmodel_pos, INCH_TO_CM);
                    current_bone.world_transform.position = vec3_div(viewmodel_pos, INCH_TO_CM);
                }
            }

            if current_bone.parent > -1 {
                let parent_bone = self.bones[current_bone.parent as usize].to_owned();
                current_bone.generate_world_transform_by_parent(parent_bone);
            }

            self.bones[i as usize] = current_bone;
        }

        Ok(())
    }
    fn load_v25(&mut self, file: &mut File) -> Result<()> {
        let bone_header = binary::read_vec::<u16>(file, 2)?;
        let bone_count = bone_header[0];
        let root_bone_count = bone_header[1];

        for _ in 0..root_bone_count {
            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent: -1,
                local_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
                world_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
            });
        }

        for _ in 0..bone_count {
            let parent = binary::read::<i8>(file)?;
            let position = binary::read_vec::<f32>(file, 3)?;
            let rotation = binary::read_vec::<i16>(file, 3)?;

            let qx = (rotation[0] as f32) / ROTATION_DIVISOR;
            let qy = (rotation[1] as f32) / ROTATION_DIVISOR;
            let qz = (rotation[2] as f32) / ROTATION_DIVISOR;
            let qw = f32::sqrt((1.0 - (qx * qx) - (qy * qy) - (qz * qz)).max(0.0));

            let bone_transform = XModelPartBoneTransform {
                position: vec3_from_vec(position).unwrap(),
                rotation: [qw, qx, qy, qz],
            };

            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent,
                local_transform: bone_transform,
                world_transform: bone_transform,
            })
        }

        for i in 0..root_bone_count + bone_count {
            let mut current_bone = self.bones[i as usize].to_owned();
            let bone_name = binary::read_string(file)?;
            current_bone.name = bone_name.clone();

            if current_bone.parent > -1 {
                let parent_bone = self.bones[current_bone.parent as usize].to_owned();
                current_bone.generate_world_transform_by_parent(parent_bone);
            }

            self.bones[i as usize] = current_bone;
        }

        Ok(())
    }
    fn load_v62(&mut self, file: &mut File) -> Result<()> {
        let bone_header = binary::read_vec::<u16>(file, 2)?;
        let bone_count = bone_header[0];
        let root_bone_count = bone_header[1];

        for _ in 0..root_bone_count {
            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent: -1,
                local_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
                world_transform: XModelPartBoneTransform {
                    position: [0.0, 0.0, 0.0],
                    rotation: [1.0, 0.0, 0.0, 0.0],
                },
            });
        }

        for _ in 0..bone_count {
            let parent = binary::read::<i8>(file)?;
            let position = binary::read_vec::<f32>(file, 3)?;
            let rotation = binary::read_vec::<i16>(file, 3)?;

            let qx = (rotation[0] as f32) / ROTATION_DIVISOR;
            let qy = (rotation[1] as f32) / ROTATION_DIVISOR;
            let qz = (rotation[2] as f32) / ROTATION_DIVISOR;
            let qw = f32::sqrt((1.0 - (qx * qx) - (qy * qy) - (qz * qz)).max(0.0));

            let bone_transform = XModelPartBoneTransform {
                position: vec3_from_vec(position).unwrap(),
                rotation: [qw, qx, qy, qz],
            };

            self.bones.push(XModelPartBone {
                name: String::from(""),
                parent,
                local_transform: bone_transform,
                world_transform: bone_transform,
            })
        }

        for i in 0..root_bone_count + bone_count {
            let mut current_bone = self.bones[i as usize].to_owned();
            let bone_name = binary::read_string(file)?;
            current_bone.name = bone_name.clone();

            if current_bone.parent > -1 {
                let parent_bone = self.bones[current_bone.parent as usize].to_owned();
                current_bone.generate_world_transform_by_parent(parent_bone);
            }

            self.bones[i as usize] = current_bone;
        }

        Ok(())
    }
}

impl XModelPartBone {
    fn generate_world_transform_by_parent(&mut self, parent: XModelPartBone) {
        self.world_transform.position = vec3_add(
            parent.world_transform.position,
            vec3_rotate(
                self.local_transform.position,
                parent.world_transform.rotation,
            ),
        );
        self.world_transform.rotation = quat_multiply(
            parent.world_transform.rotation,
            self.local_transform.rotation,
        );
    }
}
