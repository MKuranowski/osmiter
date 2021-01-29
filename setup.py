from setuptools import setup

# new release walkthrough:
# python3 -m pytest
# bump __version__
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*filename*

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="osmiter",
    py_modules=["osmiter"],
    license="MIT",
    version="1.1.1",
    description="Library for reading OSM XML/GZ/BZ2/PBF files",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Mikołaj Kuranowski",
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
    packages=["osmiter", "osmiter.pbf"],
    install_requires=["iso8601", "protobuf", "typing_extensions"],
    python_requires=">=3.6, <4",
    data_files=["README.md", "license.md"],
)
