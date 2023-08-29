pub type Vec3 = [f32; 3]; // x, y, z
pub type UV = [f32; 2]; // u, v
pub type Quat = [f32; 4]; // x, y, z, w
pub type Color = [f32; 4]; // r, g, b, a
pub type Triangle = [u16; 3]; // v1, v2, v3

pub fn vec3_from_vec(v: Vec<f32>) -> Option<Vec3> {
    if v.len() != 3 {
        return None;
    }

    Some([v[0], v[1], v[2]])
}

pub fn uv_from_vec(v: Vec<f32>) -> Option<UV> {
    if v.len() != 2 {
        return None;
    }

    Some([v[0], 1.0 - v[1]])
}

pub fn quat_from_vec(v: Vec<f32>) -> Option<Quat> {
    if v.len() != 4 {
        return None;
    }

    Some([v[0], v[1], v[2], v[3]])
}

pub fn color_from_vec(v: Vec<u8>) -> Option<Color> {
    if v.len() != 4 {
        return None;
    }

    Some([
        v[0] as f32 / 255.0,
        v[1] as f32 / 255.0,
        v[2] as f32 / 255.0,
        v[3] as f32 / 255.0,
    ])
}

pub fn triangle_from_vec(v: Vec<u16>) -> Option<Triangle> {
    if v.len() != 3 {
        return None;
    }

    Some([v[0], v[1], v[2]])
}

pub fn vec3_add(v1: Vec3, v2: Vec3) -> Vec3 {
    return [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]];
}

pub fn vec3_div(v: Vec3, d: f32) -> Vec3 {
    return [v[0] / d, v[1] / d, v[2] / d];
}

pub fn vec3_rotate(v: Vec3, q: Quat) -> Vec3 {
    let a = [
        q[1] * v[2] - q[2] * v[1] + v[0] * q[3],
        q[2] * v[0] - q[0] * v[2] + v[1] * q[3],
        q[0] * v[1] - q[1] * v[0] + v[2] * q[3],
    ];

    let b = [
        q[1] * a[2] - q[2] * a[1],
        q[2] * a[0] - q[0] * a[2],
        q[0] * a[1] - q[1] * a[0],
    ];

    return [v[0] + b[0] + b[0], v[1] + b[1] + b[1], v[2] + b[2] + b[2]];
}

pub fn quat_multiply(q1: Quat, q2: Quat) -> Quat {
    return [
        q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[3] * q2[2],
        q1[3] * q2[0] - q1[0] * q2[3] - q1[1] * q2[2] - q1[3] * q2[1],
        q1[3] * q2[1] - q1[0] * q2[2] - q1[1] * q2[3] - q1[3] * q2[0],
        q1[3] * q2[2] - q1[0] * q2[1] - q1[1] * q2[0] - q1[3] * q2[3],
    ];
}
