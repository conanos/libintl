#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment,CMake
import os


class LibiconvConan(ConanFile):
    name = "libintl"
    version = "0.19.8"
    description = "Convert text to and from Unicode"
    url = "https://github.com/conanos/libintl"
    homepage = "https://www.gnu.org/software/gettext/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "LGPL-2.1"
    exports = ["LICENSE.md",'CMakeLists.txt','msvc/*']
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=True", "fPIC=True"
    
    archive_name = "{0}-{1}".format(name, version)
    short_paths = True
    generators = "cmake"

    @property
    def is_mingw(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'gcc'

    @property
    def is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    def configure(self):
        del self.settings.compiler.libcxx

    #def build_requirements(self):
    #    if self.is_msvc:
    #        self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://ftp.gnu.org/gnu/gettext"

        if os.environ.get('FUNCKING_CFW') and os.environ.get('GNU_MIRROR_URL'):
            source_url = '%s/%s'%(os.environ['GNU_MIRROR_URL'],'gettext')
        
        tools.get("{0}/gettext-{1}.tar.gz".format(source_url, self.version))

    def build_autotools(self):
        prefix = os.path.abspath(self.package_folder)
        win_bash = False
        rc = None
        host = None
        build = None
        if self.is_mingw or self.is_msvc:
            prefix = prefix.replace('\\', '/')
            win_bash = True
            build = False
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
                rc = "windres --target=pe-i386"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
                rc = "windres --target=pe-x86-64"

        #
        # If you pass --build when building for iPhoneSimulator, the configure script halts.
        # So, disable passing --build by setting it to False.
        #
        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            build = False

        env_build = AutoToolsBuildEnvironment(self, win_bash=win_bash)

        if self.settings.os != "Windows":
            env_build.fpic = self.options.fPIC

        configure_args = ['--prefix=%s' % prefix]
        if self.options.shared:
            configure_args.extend(['--disable-static', '--enable-shared'])
        else:
            configure_args.extend(['--enable-static', '--disable-shared'])

        env_vars = {}

        if self.is_mingw:
            configure_args.extend(['CPPFLAGS=-I%s/include' % prefix,
                                   'LDFLAGS=-L%s/lib' % prefix,
                                   'RANLIB=:'])
        if self.is_msvc:
            runtime = str(self.settings.compiler.runtime)
            configure_args.extend(['CC=$PWD/build-aux/compile cl -nologo',
                                   'CFLAGS=-%s' % runtime,
                                   'CXX=$PWD/build-aux/compile cl -nologo',
                                   'CXXFLAGS=-%s' % runtime,
                                   'CPPFLAGS=-D_WIN32_WINNT=0x0600 -I%s/include' % prefix,
                                   'LDFLAGS=-L%s/lib' % prefix,
                                   'LD=link',
                                   'NM=dumpbin -symbols',
                                   'STRIP=:',
                                   'AR=$PWD/build-aux/ar-lib lib',
                                   'RANLIB=:'])
            env_vars['win32_target'] = '_WIN32_WINNT_VISTA'

            with tools.chdir(self.archive_name):
                tools.run_in_windows_bash(self, 'chmod +x build-aux/ar-lib build-aux/compile')

        if rc:
            configure_args.extend(['RC=%s' % rc, 'WINDRES=%s' % rc])

        with tools.chdir(self.archive_name):
            with tools.environment_append(env_vars):
                env_build.configure(args=configure_args, host=host, build=build)
                env_build.make()
                env_build.make(args=["install"])

    def cmake_build(self):
        cmake = CMake(self)
        cmake.configure(build_folder='~build',
        defs={'USE_CONAN_IO':True})
        
        cmake.build()
        cmake.install()


    def build(self):
        if self.settings.os == "Windows":
            self.cmake_build()
            #if tools.os_info.detect_windows_subsystem() not in ("cygwin", "msys2"):
            #    raise Exception("This recipe needs a Windows Subsystem to be compiled. "
            #                    "You can specify a build_require to:"
            #                    " 'msys2_installer/latest@bincrafters/stable' or"
            #                    " 'cygwin_installer/2.9.0@bincrafters/stable' or"
            #                    " put in the PATH your own installation")
            #if self.is_msvc:
            #    with tools.vcvars(self.settings):
            #        self.build_autotools()
            #elif self.is_mingw:
            #    self.build_autotools()
            #else:
            #    raise Exception("unsupported build")
        else:
            self.build_autotools()

    def package(self):
        pass
        #self.copy(os.path.join(self.archive_name, "COPYING.LIB"), dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        #if self.is_msvc and self.options.shared:
        #    self.cpp_info.libs = ['iconv.dll.lib']
        #else:
        self.cpp_info.libs = ['intl']
        #self.env_info.path.append(os.path.join(self.package_folder, "bin"))
