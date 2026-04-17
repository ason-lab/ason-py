"""Build script for asun C++ pybind11 extension (PEP 517 / setuptools)."""
import sys
import sysconfig
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
        ext_path = Path(self.get_ext_fullpath(ext.name)).resolve()
        ext_dir = ext_path.parent

        cfg = "Debug" if self.debug else "Release"
        cmake_args = [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={ext_dir}",
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DASUN_EXTENSION_SUFFIX={sysconfig.get_config_var('EXT_SUFFIX') or ''}",
        ]
        build_args = ["--config", cfg, "--parallel"]

        subprocess.check_call(
            ["cmake", str(Path(__file__).parent)] + cmake_args,
            cwd=build_tmp,
        )
        subprocess.check_call(
            ["cmake", "--build", str(build_tmp)] + build_args,
        )

        # Ship typing metadata alongside the extension module so type checkers
        # can discover it from the installed wheel (PEP 561, top-level module).
        for filename in ("asun.pyi", "py.typed"):
            src = Path(__file__).parent / filename
            dst = ext_dir / filename
            dst.write_bytes(src.read_bytes())


setup(
    name="asun",
    version="1.0.1",
    author="asun contributors",
    description="High-performance ASUN (Array-Schema Unified Notation) Python extension",
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension("asun")],
    cmdclass={"build_ext": CMakeBuild},
    python_requires=">=3.8",
    url="https://github.com/asunLab/asun-py",
    project_urls={
        "Repository": "https://github.com/asunLab/asun-py",
        "Issues": "https://github.com/asunLab/asun-py/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    zip_safe=False,
)
