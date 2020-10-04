from setuptools import setup, find_packages

# new release walkthrough:
# python3 -m pytest
# bump __version__
# python3 setup.py sdist
# python3 -m twine upload dist/*filename*

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="osmiter",
    py_modules=["osmiter"],
    license="MIT",
    version="1.1.0",
    description="Library for reading OSM XML/GZ/BZ2/PBF files",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Mikołaj Kuranowski",
    author_email="".join(chr(i) for i in [
        109, 107, 117, 114, 97, 110, 111, 119, 115, 107, 105, 64,
        103, 109, 97, 105, 108, 46, 99, 111, 109]),
    url="https://github.com/MKuranowski/osmiter",
    keywords="osm xml gz pz2 pbf openstreetmap parser",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=["iso8601", "protobuf"],
)
