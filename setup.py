from setuptools import setup, find_packages, sic
from setuptools_rust import Binding, RustExtension

import sys
from zipfile import ZipFile
import glob
import os
from python.cod_asset_importer import version

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

version_str = ".".join(map(str, version))

setup(
    name="cod-asset-importer",
    version=sic(version_str),
    rust_extensions=[rust_extension],
    package_dir={"": "python"},
    packages=find_packages(where="python"),
    zip_safe=False,
)

if package:
    cod_asset_importer = "cod_asset_importer"
    package_name = f"{cod_asset_importer}_v{version_str}"
    src = os.path.join(os.curdir, "python", cod_asset_importer)
    zip_file_path = os.path.join(os.curdir, "release", f"{package_name}.zip")
    with ZipFile(zip_file_path, "w") as zip_file:
        for ext in ("*.py", "*.pyd"):
            for file in glob.iglob(os.path.join(src, ext)):
                zip_file.write(
                    file, os.path.join(cod_asset_importer, os.path.basename(file))
                )

        zip_file.write(
            os.path.join(os.curdir, "LICENSE"),
            os.path.join(cod_asset_importer, "LICENSE"),
        )
