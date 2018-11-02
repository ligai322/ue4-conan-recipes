Conan recipes for UE4-compatible library packages
=================================================

This repository contains Conan recipes for a variety of libraries to facilitate their use with Unreal Engine 4. The recipes make use of the infrastructure from [conan-ue4cli](https://github.com/adamrehn/conan-ue4cli) to provide compatibility with UE4-bundled third-party libraries and avoid symbol interposition issues, as well as ensuring everything is built against the UE4-bundled version of libc++ under Linux.

To build the packages, you will need the following:

- Unreal Engine 4.19.0 or newer
- Python 3.5 or newer, along with the dependencies specified in `requirements.txt`
- [ue4cli](https://github.com/adamrehn/ue4cli) and [conan-ue4cli](https://github.com/adamrehn/conan-ue4cli)

To install the Python dependencies and build all of the packages, run:

```
pip3 install -r requirements.txt
python3 build.py all
```

Alternatively, you can specify a list of individual packages (with optional version numbers), like so:

```
python3 build.py PACKAGE1 PACKAGE2==1.2.3 PACKAGE3
```

See the output of `python3 build.py --help` for full usage details.

It is recommended that you build the packages from this repository inside the `ue4-full` Docker image from [ue4-docker](https://github.com/adamrehn/ue4-docker) and then upload the built packages to a Conan remote so that they can be pulled from there for further use.

All of the recipe code and associated build infrastructure in this repository is licensed under the MIT License, see the file [LICENSE](./LICENSE) for details. See the individual Conan recipes for the license details of the libraries that they build.
