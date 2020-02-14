from setuptools import setup, find_packages
import osmiter

# new release walkthrough:
# python3 -m pytest
# bump __version__
# python3 setup.py sdist
# python3 -m twine upload dist/*filename*

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
  name = "osmiter",
  py_modules = ["osmiter"],
  license = osmiter.__license__,
  version = osmiter.__version__,
  description = osmiter.__description__,
  long_description = readme,
  long_description_content_type = "text/markdown",
  author = osmiter.__author__,
  author_email = osmiter.__email__,
  url = osmiter.__url__,
  keywords = "osm xml gz pz2 pbf openstreetmap parser",
  classifiers = [
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
