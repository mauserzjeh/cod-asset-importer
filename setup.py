from setuptools import setup, find_packages, sic
from setuptools_rust import Binding, RustExtension

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
