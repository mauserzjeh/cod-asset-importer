pub type Vec3 = [f32; 3]; // x, y, z
pub type UV = [f32; 2]; // u, v
pub type Quat = [f32; 4]; // w, x, y, z
pub type Color = [f32; 4]; // r, g, b, a
pub type Triangle = [u16; 3]; // v1, v2, v3

pub fn vec3_from_vec(v: Vec<f32>) -> Option<Vec3> {
    if v.len() != 3 {
        return None;
    }

    Some([v[0], v[1], v[2]])
}

pub fn uv_from_vec(v: Vec<f32>, flip_uv: bool) -> Option<UV> {
    if v.len() != 2 {
        return None;
    }

    if flip_uv {
        Some([v[0], 1.0 - v[1]])
    } else {
        Some([v[0], v[1]])
    }
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
    let x = v1[0] + v2[0];
    let y = v1[1] + v2[1];
    let z = v1[2] + v2[2];

    [x, y, z]
}

pub fn vec3_div(v: Vec3, d: f32) -> Vec3 {
    let x = v[0] / d;
    let y = v[1] / d;
    let z = v[2] / d;

    [x, y, z]
}

pub fn vec3_rotate(v: Vec3, q: Quat) -> Vec3 {
    let a = [
        q[2] * v[2] - q[3] * v[1] + v[0] * q[0],
        q[3] * v[0] - q[1] * v[2] + v[1] * q[0],
        q[1] * v[1] - q[2] * v[0] + v[2] * q[0],
    ];

    let b = [
        q[2] * a[2] - q[3] * a[1],
        q[3] * a[0] - q[1] * a[2],
        q[1] * a[1] - q[2] * a[0],
    ];

    let x = v[0] + b[0] + b[0];
    let y = v[1] + b[1] + b[1];
    let z = v[2] + b[2] + b[2];

    [x, y, z]
}

pub fn quat_multiply(q1: Quat, q2: Quat) -> Quat {
    let w = q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3];
    let x = q1[0] * q2[1] + q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2];
    let y = q1[0] * q2[2] - q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1];
    let z = q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0];

    [w, x, y, z]
}
