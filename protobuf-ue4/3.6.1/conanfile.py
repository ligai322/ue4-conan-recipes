from conans import ConanFile, CMake, tools

class ProtobufUe4Conan(ConanFile):
    name = "protobuf-ue4"
    version = "3.6.1"
    license = "BSD-3-Clause"
    url = "https://github.com/adamrehn/ue4-conan/recipes/protobuf-ue4"
    description = "Protocol Buffers custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = (
        "libcxx/ue4@adamrehn/generated",
        "zlib/ue4@adamrehn/generated"
    )
    
    def cmake_flags(self):
        
        # Generate the CMake flags to ensure the UE4-bundled version of zlib is used
        zlib = self.deps_cpp_info["zlib"]
        return [
            "-Dprotobuf_BUILD_TESTS=OFF",
            "-DBUILD_SHARED_LIBS=OFF",
            "-DZLIB_INCLUDE_DIR=" + zlib.includedirs[0],
            "-DZLIB_LIBRARY=" + zlib.libs[0]
        ]
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/protocolbuffers/protobuf.git -b v{}".format(self.version))
        
        # Prevent libprotobuf-lite from being included in our built package
        tools.replace_in_file(
            "protobuf/cmake/install.cmake",
            "set(_protobuf_libraries libprotobuf-lite libprotobuf)",
            "set(_protobuf_libraries libprotobuf)"
        )
    
    def build(self):
        
        # Under Linux, restore CC and CXX if the current Conan profile has overridden them
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build libprotobuf
        cmake = CMake(self)
        cmake.configure(source_folder="protobuf/cmake", args=self.cmake_flags())
        cmake.build()
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
