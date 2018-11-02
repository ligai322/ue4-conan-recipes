from conans import ConanFile, CMake, tools
from grpc_helper import Utility
import json, os

class GrpcUe4Conan(ConanFile):
    name = "grpc-ue4"
    version = "1.16.0"
    license = "Apache-2.0"
    url = "https://github.com/adamrehn/ue4-conan/recipes/grpc-ue4"
    description = "gRPC custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = "*"
    requires = (
        "libcxx/ue4@adamrehn/generated",
        "OpenSSL/ue4@adamrehn/generated",
        "zlib/ue4@adamrehn/generated"
    )
    
    def requirements(self):
        self.requires("cares-ue4/1.13.0@{}/{}".format(self.user, self.channel))
        self.requires("protobuf-ue4/3.6.1@{}/{}".format(self.user, self.channel))
    
    def cmake_flags(self):
        
        # Retrieve the absolute paths to libprotobuf, libprotoc, and protoc
        protobuf = self.deps_cpp_info["protobuf-ue4"]
        libprotobuf = Utility.resolve_file(protobuf.lib_paths[0], "protobuf")
        libprotoc = Utility.resolve_file(protobuf.lib_paths[0], "protoc")
        protoc = Utility.resolve_file(protobuf.bin_paths[0], "protoc")
        
        # Generate the CMake flags to use our custom dependencies
        cares = self.deps_cpp_info["cares-ue4"]
        openssl = self.deps_cpp_info["OpenSSL"]
        zlib = self.deps_cpp_info["zlib"]
        return [
            "-DgRPC_BUILD_TESTS=OFF",
            "-DgRPC_CARES_PROVIDER=package",
            "-DgRPC_PROTOBUF_PROVIDER=package",
            "-DgRPC_SSL_PROVIDER=package",
            "-DgRPC_ZLIB_PROVIDER=package",
            "-Dc-ares_DIR=" + os.path.join(cares.lib_paths[0], "cmake", "c-ares"),
            "-DOPENSSL_USE_STATIC_LIBS=ON",
            "-D_OPENSSL_INCLUDEDIR=" + openssl.include_paths[0],
            "-D_OPENSSL_LIBDIR=" + openssl.lib_paths[0],
            "-DProtobuf_INCLUDE_DIR=" + protobuf.include_paths[0],
            "-DProtobuf_LIBRARY=" + libprotobuf,
            "-DProtobuf_PROTOC_LIBRARY=" + libprotoc,
            "-DProtobuf_PROTOC_EXECUTABLE=" + protoc,
            "-DZLIB_INCLUDE_DIR=" + zlib.include_paths[0],
            "-DZLIB_LIBRARY=" + zlib.libs[0],
        ]
    
    def source(self):
        
        # Clone the gRPC repo and the submodules that we need
        self.run(" ".join([
            "git", "clone",
            "--progress", "--recursive", "--depth=1",
            "https://github.com/grpc/grpc.git", "-b", "v{}".format(self.version),
            "--recurse-submodules=\".\"",
            "--recurse-submodules=\":(exclude)third_party/benchmark\"",
            "--recurse-submodules=\":(exclude)third_party/bloaty\"",
            "--recurse-submodules=\":(exclude)third_party/boringssl\"",
            "--recurse-submodules=\":(exclude)third_party/boringssl-with-bazel\"",
            "--recurse-submodules=\":(exclude)third_party/cares\"",
            "--recurse-submodules=\":(exclude)third_party/googletest\"",
            "--recurse-submodules=\":(exclude)third_party/libcxx\"",
            "--recurse-submodules=\":(exclude)third_party/libcxxabi\"",
            "--recurse-submodules=\":(exclude)third_party/protobuf\"",
            "--recurse-submodules=\":(exclude)third_party/zlib\""
        ]))
        
        # Disable the dependency on the Google benchmarking library
        tools.replace_in_file(
            "grpc/CMakeLists.txt",
            "include(cmake/benchmark.cmake)",
            "#include(cmake/benchmark.cmake)"
        )
    
    def build(self):
        
        # Under Linux, restore CC and CXX if the current Conan profile has overridden them
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Build grpc
        cmake = CMake(self)
        cmake.configure(source_folder="grpc", args=self.cmake_flags())
        cmake.build(target="grpc++")
        cmake.install()
    
    def package(self):
        self.copy("__init__.py")
        self.copy("grpc_helper.py")
    
    def package_info(self):
        
        # Filter out any extensions when listing our exported libraries
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs = list([lib for lib in self.cpp_info.libs if "_ext" not in lib])
        
        # Provide the necessary data so that consumers can instantiate a `ProtoCompiler` object
        self.env_info.PYTHONPATH.append(self.package_folder)
        self.user_info.build_data = json.dumps([self.deps_cpp_info["protobuf-ue4"].bin_paths[0], self.cpp_info.bin_paths[0]])
