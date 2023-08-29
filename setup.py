from setuptools import setup, find_packages, sic
from setuptools_rust import Binding, RustExtension

from cod_asset_importer import version_str

rust_extension = RustExtension(
    target="cod_asset_importer.cod_asset_importer",
    binding=Binding.PyO3,
    py_limited_api=True
)

setup(
    name="cod-asset-importer",
    version=sic(version_str),
    rust_extensions=[rust_extension],
    packages=find_packages(),
    zip_safe=False,
)