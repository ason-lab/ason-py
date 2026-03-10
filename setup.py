"""Build script for ason C++ pybind11 extension (PEP 517 / setuptools)."""
import sys
import subprocess
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        build_tmp = Path(self.build_temp) / ext.name
        build_tmp.mkdir(parents=True, exist_ok=True)
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.resolve()

        cfg = "Debug" if self.debug else "Release"
        cmake_args = [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={ext_dir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
        ]
        build_args = ["--config", cfg, "--parallel"]

        subprocess.check_call(
            ["cmake", str(Path(__file__).parent)] + cmake_args,
            cwd=build_tmp,
        )
        subprocess.check_call(
            ["cmake", "--build", str(build_tmp)] + build_args,
        )


setup(
    name="ason",
    version="0.1.0",
    author="ason contributors",
    description="High-performance ASON (Array-Schema Object Notation) Python extension",
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension("ason")],
    cmdclass={"build_ext": CMakeBuild},
    python_requires=">=3.8",
    license="MIT",
    url="https://github.com/ason-lab/ason-py",
    project_urls={
        "Repository": "https://github.com/ason-lab/ason-py",
        "Issues": "https://github.com/ason-lab/ason-py/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    data_files=[("", ["ason.pyi", "py.typed"])],
    zip_safe=False,
)
