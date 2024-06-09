#!/bin/bash
set -e

apt-get update
apt-get install -y git cmake g++ libinih-dev

git clone https://github.com/LeoHsiao1/pyexiv2.git
git clone https://github.com/Exiv2/exiv2.git

# build exiv2
cd exiv2
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
cmake --install build 

cd ..
cp exiv2/build/lib/libexiv2.so pyexiv2/pyexiv2/lib/libexiv2.so

# build pyexiv2
cd pyexiv2/pyexiv2/lib
python3.12 -m pip install pybind11
mkdir -p py3.12-linux
g++ exiv2api.cpp -o py3.12-linux/exiv2api.so \
	-std=c++11 -O3 -Wall -shared -fPIC \
	`python3.12 -m pybind11 --includes` \
	-l exiv2

cd ../../
python3.12 -m pip install .
