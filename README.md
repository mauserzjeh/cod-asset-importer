# Call of Duty asset importer

Blender add-on for importing various Call of Duty assets via the game files.

## Examples
### D3DBSP
<img src="./examples/d3dbsp1.png?raw=true" width="500" height="auto"></img>
<br/>
(overlapping faces and some of the materials need fixes)
<br/>
<br/>

### XModel
<img src="./examples/xmodel1.png?raw=true" width="500" height="auto"></img>
<br/>
<br/>

### IWi
<img src="./examples/iwi1.png?raw=true" width="250" height="auto"></img>
<img src="./examples/iwi2.png?raw=true" width="250" height="auto"></img>
<br/>
<br/>

## Supported assets & features
- Call of Duty 2
    - D3DBSP - Compiled map files
        - Geometry
        - Materials and textures
        - Props
    - XModel - Compiled models
        - Geometry
        - Materials and textures
        - Skeleton & weights
    - Texture - IWi texture
        - Texture import
        - DXT1, DXT3, DXT5 decoding
        - Normal map generation from bump map

<br/>
<br/>

# How to use
## Installation and setup
- Extract the contents of all the .iwd files into a folder
    - The folder structure  of the extracted assets should look the same as below and mainly these are the most  important folders which are required for the add-on to work properly

    - ```
        .
        ├── images
        ├── maps
        ├── materials
        ├── xanim
        ├── xmodel
        ├── xmodelalias
        ├── xmodelparts
        └── xmodelsurfs
        ```
- Install the add-on for Blender
    - Click on Edit and select Preferences
    - Click on the Add-ons tab and click on the Install button
    - Browse to the .zip file containing the add-on and then click on the Install Add-on button
- If everything is done right, import options should be available in File > Import menu

<br/>
<br/>

## Importing assets
- Click on File menu point and go to the Import menu
- Select Call of Duty map if you would like to import a map
    - Browse to the map in the maps folder
- Select Call of Duty xmodel if you would like to import any model
    - Browse to the model in the xmodel folder
- Select Call of Duty texture if you would like to import any texture
    - Browse to the texture in the images folder
    - Set the "Normal map" checkbox to true if you are importing a normal map


