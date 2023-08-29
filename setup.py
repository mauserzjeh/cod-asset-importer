from setuptools import setup, find_packages, sic
from setuptools_rust import Binding, RustExtension

from python.cod_asset_importer import version_str

rust_extension = RustExtension(
    target="cod_asset_importer.cod_asset_importer",
    path="./rust/cod_asset_importer/Cargo.toml",
    binding=Binding.PyO3,
    py_limited_api=True
)

setup(
    name="cod-asset-importer",
    version=sic(version_str),
    rust_extensions=[rust_extension],
    package_dir={"": "python"},
    packages=find_packages(where="python"),
    zip_safe=False,
)