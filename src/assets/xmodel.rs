pub struct XModel {
    name: String,
    version: u16,
    lods: Vec<XModelLod>
}

pub struct XModelLod {
    name: String,
    distance: f32,
    materials: Vec<String>
}

enum XModelType {
    Rigid,
    Animated,
    Viewmodel,
    Playerbody,
    Viewhands,
}
