![GitHub release (latest by date)](https://img.shields.io/github/v/release/mauserzjeh/cod-asset-importer?style=flat-square) 
![GitHub all releases](https://img.shields.io/github/downloads/mauserzjeh/cod-asset-importer/total?color=green&style=flat-square)

# Call of Duty asset importer
Blender add-on for importing various Call of Duty assets via the game files.

## Supported assets & features
- Call of Duty & Call of Duty United Offensive
    - BSP - Compiled map files
    - XModel - Compiled models
- Call of Duty 2
    - D3DBSP - Compiled map files
    - XModel - Compiled models
- Call of Duty 4 Modern Warfare
    - XModel - Compiled models

## Installation & setup
First of all, extract all the necessary game specific contents. Make sure to have the exact same folder structure as they have originally.

### Call of Duty & Call of Duty United Offensive
Files can be found inside the .pk3 files.
```
  .
  ├── maps/
  ├── skins/
  ├── textures/
  ├── xanim/
  ├── xmodel/
  ├── xmodelalias/
  ├── xmodelparts/
  └── xmodelsurfs/
```

### Call of Duty 2
Files can be found inside the .iwd files.
```
  .
  ├── images/
  ├── maps/
  ├── materials/
  ├── xanim/
  ├── xmodel/
  ├── xmodelalias/
  ├── xmodelparts/
  └── xmodelsurfs/
```
### Call of Duty 4 Modern Warfare
Images can be found inside the .iwd files. The rest of the assets can be acquired by installing modtools.
```
  .
  ├── images/
  ├── materials/
  ├── xanim/
  ├── xmodel/
  ├── xmodelalias/
  ├── xmodelparts/
  └── xmodelsurfs/
```

- [Download the latest release](https://github.com/mauserzjeh/cod-asset-importer/releases/latest)
- Launch Blender
- `Edit > Preferences > Add-ons > Install`
- Browse to the downloaded .zip file
- Enable the addon by ticking the checkbox in front of its name

## Usage
- Launch Blender
- To see import progress, information and errors
    - `Window > Toggle System Console`
- To import a map
    - `File > Import > CoD Asset Importer > Import map`
    - Browse to the map inside the maps folder
- To import a model
    - `File > Import > CoD Asset Importer > Import model`
    - Browse to the xmodel inside the xmodel folder

## Installation from source

### Requirements
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/)
- [Rust](https://www.rust-lang.org/)

### Installation
- Open Git Bash in the folder where you would like to clone the repository
- Clone the repository
```
$ git clone git@github.com:mauserzjeh/cod-asset-importer.git
```

- Install dependencies
```
$ pip install -r requirements.txt
```

- Run the build script which will create a `.zip` file in the `release` folder. Alternatively the `Build & Package` task can be run from VS Code
```sh
$ python setup.py build_rust --inplace --release --create-release-package
```

- Launch Blender
- `Edit > Preferences > Add-ons > Install`
- Browse to the generated .zip file in the release folder
- Enable the addon by ticking the checkbox in front of its name




