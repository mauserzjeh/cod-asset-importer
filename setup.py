from setuptools import setup, find_packages, sic
from setuptools_rust import Binding, RustExtension

import sys
from zipfile import ZipFile
import glob
import os


package = False
package_argv = "--create-release-package"
if package_argv in sys.argv:
    package = True
    sys.argv.remove(package_argv)

rust_extension = RustExtension(
    target="cod_asset_importer.cod_asset_importer",
    path="./rust/cod_asset_importer/Cargo.toml",
    binding=Binding.PyO3,
    py_limited_api=True,
)

setup(
    name="cod-asset-importer",
    rust_extensions=[rust_extension],
    package_dir={"": "python"},
    packages=find_packages(where="python"),
    zip_safe=False,
)

if package:
    cod_asset_importer = "cod_asset_importer"
    src = os.path.join(os.curdir, "python", cod_asset_importer)
    zip_file_path = os.path.join(os.curdir, "release", "cod_asset_importer.zip")
    with ZipFile(zip_file_path, "w") as zip_file:
        for ext in ('*.py', '*.pyd'):
            for file in glob.iglob(os.path.join(src, ext)):
                zip_file.write(file, os.path.join(cod_asset_importer, os.path.basename(file)))
        
        zip_file.write(os.path.join(os.curdir, 'LICENSE'), os.path.join(cod_asset_importer, 'LICENSE'))
