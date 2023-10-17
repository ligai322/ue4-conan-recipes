from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
import os

class GdalUe4Conan(ConanFile):
    name = "gdal-ue4"
    version = "2.4.0"
    license = "MIT"
    url = "https://github.com/adamrehn/ue4-conan-recipes/gdal-ue4"
    description = "GDAL custom build for Unreal Engine 4"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True
    requires = (
        "libcxx/ue4@adamrehn/profile",
        "ue4util/ue4@adamrehn/profile"
    )
    
    def _replace_multiple(self, filename, pairs):
        for pair in pairs:
            search, replace = pair
            tools.replace_in_file(filename, search, replace)
    
    def requirements(self):
        self.requires("geos-ue4/3.6.3@adamrehn/{}".format(self.channel))
        self.requires("proj-ue4/4.9.3@adamrehn/{}".format(self.channel))
        self.requires("libcurl/ue4@adamrehn/{}".format(self.channel))
        self.requires("OpenSSL/ue4@adamrehn/{}".format(self.channel))
        self.requires("nghttp2/ue4@adamrehn/{}".format(self.channel))
        self.requires("UElibPNG/ue4@adamrehn/{}".format(self.channel))
        self.requires("zlib/ue4@adamrehn/{}".format(self.channel))
        self.requires("LibJpegTurbo/ue4@adamrehn/{}".format(self.channel))
    
    def configure_flags(self):
        
        # Determine the absolute path to `geos-config`
        from ue4util import Utility
        geos = self.deps_cpp_info["geos-ue4"]
        geosConfig = Utility.resolve_file(geos.bin_paths[0], "geos-config")
        
        return [
            "--prefix=" + self.package_folder,
            "--datarootdir={}/data".format(self.package_folder),
            "--enable-static",
            "--disable-shared",
            "--without-libtool",
            "--enable-pdf-plugin=no",
            "--without-ld-shared",
            "--with-threads=yes",
            "--with-libz={}".format(self.deps_cpp_info["zlib"].rootpath),
            "--without-liblzma",
            "--without-libiconv-prefix",
            "--without-pg",
            "--without-grass",
            "--without-libgrass",
            "--without-cfitsio",
            "--without-pcraster",
            "--with-png={}".format(self.deps_cpp_info["UElibPNG"].rootpath),
            "--without-mrf",
            "--without-dds",
            "--without-gta",
            "--with-libtiff=internal",
            "--with-geotiff=internal",
            "--with-jpeg=internal",
            "--with-rename_internal_libtiff_symbols",
            "--with-rename_internal_libgeotiff_symbols",
            "--without-jpeg12",
            "--without-gif",
            "--without-ogdi",
            "--without-fme",
            "--without-sosi",
            "--without-mongocxx",
            "--without-hdf4",
            "--without-hdf5",
            "--without-kea",
            "--without-netcdf",
            "--without-jasper",
            "--without-openjpeg",
            "--without-fgdb",
            "--without-ecw",
            "--without-kakadu",
            "--without-mrsid",
            "--without-jp2mrsid",
            "--without-mrsid_lidar",
            "--without-msg",
            "--without-bsb",
            "--without-oci",
            "--without-oci-include",
            "--without-oci-lib",
            "--without-grib",
            "--without-mysql",
            "--without-ingres",
            "--without-xerces",
            "--without-expat",
            "--without-libkml",
            "--without-odbc",
            "--with-dods-root=no",
            "--without-curl",
            "--without-xml2",
            "--without-spatialite",
            "--without-sqlite3",
            "--without-pcre",
            "--without-idb",
            "--without-sde",
            "--without-epsilon",
            "--without-webp",
            "--without-qhull",
            "--with-freexl=no",
            "--with-libjson-c=internal",
            "--without-pam",
            "--without-poppler",
            "--without-podofo",
            "--without-pdfium",
            "--without-perl",
            "--without-python",
            "--without-java",
            "--without-mdb",
            "--without-rasdaman",
            "--without-armadillo",
            "--without-cryptopp",
            "--with-zstd=no",
            "--with-proj={}".format(self.deps_cpp_info["proj-ue4"].rootpath),
            "--with-geos={}".format(geosConfig)
        ]
    
    def source(self):
        self.run("git clone --progress --depth=1 https://github.com/OSGeo/gdal.git -b v{}".format(self.version))
    
    def build(self):
        
        # Build GDAL using Visual Studio under Windows and autotools under other platforms
        with tools.chdir("./gdal/gdal"):
            if self.settings.os == "Windows":
                self.build_windows()
            else:
                self.build_unix()
    
    def build_windows(self):
        
        # Retrieve the path details for PROJ, GEOS, curl, libpng and zlib
        from ue4util import Utility
        curl = self.deps_cpp_info["libcurl"]
        geos = self.deps_cpp_info["geos-ue4"]
        png = self.deps_cpp_info["UElibPNG"]
        jpeg = self.deps_cpp_info["LibJpegTurbo"]
        proj = self.deps_cpp_info["proj-ue4"]
        zlib = self.deps_cpp_info["zlib"]
        
        # Disable unsupported external dependencies and point GDAL to the include directories and library locations of our libraries
        self._replace_multiple("nmake.opt", [
            
            # Set the installation path to our package folder
            ["\nGDAL_HOME = \"C:\\warmerda\\bld\"", "\nGDAL_HOME = \"{}\"".format(self.package_folder)],
            
            # Disable building GDAL as a shared library
            ["\nDLLBUILD=1", "\n#DLLBUILD=1"],
            
            # Disable formats for which we lack external dependencies
            ["\nPAM_SETTING=-DPAM_ENABLED", "\n#PAM_SETTING=-DPAM_ENABLED"],
            ["\nBSB_SUPPORTED = 1", "\n#BSB_SUPPORTED = 1"],
            ["\nODBC_SUPPORTED = 1", "\n#ODBC_SUPPORTED = 1"],
            ["\nGRIB_SETTING=yes", "\n#GRIB_SETTING=yes"],
            ["\nMRF_SETTING=yes", "\n#MRF_SETTING=yes"],
            
            # PROJ
            ["\n#PROJ_FLAGS = -DPROJ_STATIC -DPROJ_VERSION=4", "\nPROJ_FLAGS = -DPROJ_STATIC -DPROJ_VERSION=4"],
            ["\n#PROJ_INCLUDE = -Id:\projects\proj.4\src", "\nPROJ_INCLUDE=-I{}".format(proj.include_paths[0])],
            ["\n#PROJ_LIBRARY = d:\projects\proj.4\src\proj_i.lib", "\nPROJ_LIBRARY={}".format(Utility.resolve_file(proj.lib_paths[0], proj.libs[0]))],
            
            # GEOS
            ["\n#GEOS_DIR=C:/warmerda/geos", "\nGEOS_DIR={}".format(geos.rootpath)],
            ["\n#GEOS_CFLAGS = -I$(GEOS_DIR)/capi -I$(GEOS_DIR)/source/headers -DHAVE_GEOS", "\nGEOS_CFLAGS=-I{} -DHAVE_GEOS".format(geos.include_paths[0])],
            ["\n#GEOS_LIB     = $(GEOS_DIR)/source/geos_c_i.lib", "\nGEOS_LIB={}".format(" ".join([Utility.resolve_file(geos.lib_paths[0], lib) for lib in geos.libs]))],
            
            # curl
            ["\n#CURL_DIR=C:\curl-7.15.0", "\nCURL_DIR={}".format(curl.rootpath)],
            ["\n#CURL_INC = -I$(CURL_DIR)/include", "\nCURL_INC = -I{}".format(curl.include_paths[0])],
            ["\n#CURL_LIB = $(CURL_DIR)/libcurl.lib", "\nCURL_LIB = {}".format(Utility.resolve_file(curl.lib_paths[0], curl.libs[0]))],
            ["\n#CURL_CFLAGS = -DCURL_STATICLIB", "\nCURL_CFLAGS = -DCURL_STATICLIB"],
            
             # libjpeg
            ["\n#JPEG_EXTERNAL_LIB = 1", "\nJPEG12_SUPPORTED = 0 \nJPEG_SUPPORTED = 0\nJPEG_EXTERNAL_LIB = 1"],
            ["\n#JPEGDIR = c:/projects/jpeg-6b", "\nJPEGDIR = {}".format(jpeg.include_paths[0])],    
            ["\n#JPEG_LIB = $(JPEGDIR)/libjpeg.lib", "\nJPEG_LIB = {}".format(Utility.resolve_file(jpeg.lib_paths[0], jpeg.libs[0]))],
            
            # libpng
            ["\n#PNG_EXTERNAL_LIB = 1", "\nPNG_EXTERNAL_LIB = 1"],
            ["\n#PNGDIR = c:/projects/libpng-1.0.8", "\nPNGDIR = {}".format(png.include_paths[0])],
            ["\n#PNG_LIB = $(PNGDIR)/libpng.lib", "\nPNG_LIB = {}".format(Utility.resolve_file(png.lib_paths[0], png.libs[0]))],
            
            
         #   ["\n#if using an external jpeg library uncomment the following lines", "\nJPEG_SUPPORTED = 0\nJPEG12_SUPPORTED = 0\n#if using an external jpeg library uncomment the following lines"],
                   
            
            # zlib
            ["\n#ZLIB_EXTERNAL_LIB = 1", "\nZLIB_EXTERNAL_LIB = 1"],
            ["\n#ZLIB_INC = -IC:\projects\zlib", "\nZLIB_INC = -I{}".format(zlib.include_paths[0])],
            ["\n#ZLIB_LIB = C:\projects\lib\Release\zlib.lib", "\nZLIB_LIB = {}".format(Utility.resolve_file(zlib.lib_paths[0], zlib.libs[0]))]
            
        ])
        
        # Prevent the GDAL command-line tools from being built (since they don't work nicely with a static build) but ensure their library functions are still built
        self._replace_multiple("makefile.vc", [
            
            # Change the call to build the default target in the apps subdirectory to build just the libraries without the associated executables
            ["\n\tcd apps\r\n\t$(MAKE) /f makefile.vc\r\n", "\n\tcd apps\r\n\t$(MAKE) /f makefile.vc appslib\r\n"],
            
            # Comment out the call to build the install target in the apps subdirectory
            ["\n\tcd ..\\apps\r\n\t$(MAKE) /f makefile.vc install", "\n\tcd ..\\apps\r\n\techo $(MAKE) /f makefile.vc install"],
            
            # Prevent our external dependencies from being bundled into the GDAL static library
            ["lib /nologo /out:gdal.lib $(LIBOBJ) $(EXTERNAL_LIBS)", "lib /nologo /out:gdal.lib $(LIBOBJ)"]
            
        ])
        
        # Patch the Visual Studio project file generation script to call the installation target when building the project
        tools.replace_in_file("generate_vcxproj.bat", "^</NMakeBuildCommandLine^>", " devinstall^</NMakeBuildCommandLine^>")
        
        # Generate the Visual Studio project file
        msvcVersion = int(str(self.settings.compiler.version))
        self.run("generate_vcxproj.bat {:.1f} {} gdal".format(
            15 if msvcVersion > 15 else msvcVersion,
            '64' if self.settings.arch == 'x86_64' else '32'
        ))
        
        # Build the project and install the built files in our package folder
        msbuild = MSBuild(self)
        msbuild.build("gdal.vcxproj")
    
    def build_unix(self):
        
        # Enable compiler interposition under Linux to enforce the correct flags for libc++
        from libcxx import LibCxx
        LibCxx.set_vars(self)
        
        # Run autogen.sh
        self.run("./autogen.sh")

        # Patch out iconv support under Mac OS X and patch GDAL v2.4.0 for XCode 12.x
        if self.settings.os == "Macos":
            self.run("sed -i '' 's/-D_XOPEN_SOURCE=500 //g' ogr/ogrsf_frmts/geojson/libjson/GNUmakefile")
            tools.replace_in_file("./configure", "iconv.h", "iconv_h")
        
        # Patch out iconv support under Linux, since the UE4 bundled toolchain doesn't include it
        if self.settings.os == "Linux":
            tools.replace_in_file("./configure", "iconv.h", "iconv_h")
        
        # Under Linux, the UE4-bundled version of zlib is typically named libz_fPIC.a, but GDAL expects libz.a
        zlibName = self.deps_cpp_info["zlib"].libs[0]
        if zlibName != "z":
            tools.replace_in_file("./configure", "-lz", "-l{}".format(zlibName))
        
        # Prepare the autotools build environment
        autotools = AutoToolsBuildEnvironment(self)
        LibCxx.fix_autotools(autotools)
        
        # Ensure the configure script can load the GEOS shared library when running tests
        geosPaths = self.deps_cpp_info["geos-ue4"].lib_paths
        ldPath = ":".join([os.environ.get("LD_LIBRARY_PATH", "")] + geosPaths)
        
        # Build using autotools
        with tools.environment_append({"LD_LIBRARY_PATH": ldPath}):
            autotools.configure(args=self.configure_flags())
            autotools.make(args=["-j{}".format(tools.cpu_count())])
            autotools.make(target="install")
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.resdirs = ["data"]
