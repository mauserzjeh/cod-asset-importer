from zipfile import ZipFile
import glob
import os


src = os.path.join(os.pardir, 'src')
cod_asset_importer = 'cod_asset_importer'

with ZipFile('cod_asset_importer.zip', 'w') as zip:
    for file in glob.iglob(os.path.join(src, '*.py')):
        zip.write(file, os.path.join(cod_asset_importer, os.path.basename(file)))

    folders = ['addon', 'assets', 'utils']
    for folder in folders:
        for file in glob.iglob(os.path.join(src, folder, '*.py')):
            zip.write(file, os.path.join(cod_asset_importer, folder, os.path.basename(file)))

    zip.write(os.path.join(src, 'bin', 'iwi2dds.exe'), os.path.join(cod_asset_importer, 'bin', 'iwi2dds.exe'))
    zip.write(os.path.join(os.pardir, 'LICENSE'), os.path.join(cod_asset_importer, 'LICENSE'))
