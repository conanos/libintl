cmake_minimum_required(VERSION 2.8)

project(libintl)
set(VERSION 0.19.8)

#
# Use Conan.io
#
if(USE_CONAN_IO)
    include(conanbuildinfo.cmake)
    conan_basic_setup()
    conan_define_targets()
endif()

# Required modules
include(GNUInstallDirs)
include(CheckIncludeFiles)



if(NOT GETTEXT_PROJECT_DIR)
  set(GETTEXT_PROJECT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/gettext-${VERSION})
endif()


set(SRCS intl/bindtextdom.c intl/dcgettext.c intl/dcigettext.c 
	intl/dcngettext.c intl/dgettext.c intl/dngettext.c 
	intl/explodename.c intl/finddomain.c intl/gettext.c 
	intl/hash-string.c intl/intl-compat.c intl/l10nflist.c 
	intl/langprefs.c intl/loadmsgcat.c intl/localcharset.c 	
	intl/localealias.c intl/localename.c intl/lock.c intl/log.c 
	intl/ngettext.c intl/osdep.c intl/plural-exp.c intl/plural.c 
	intl/printf.c intl/relocatable.c intl/textdomain.c 
	intl/version.c )
	
foreach(e ${SRCS})
	set(INTL_SRCS "${INTL_SRCS}" "${GETTEXT_PROJECT_DIR}/gettext-runtime/${e}")
endforeach()
#set(CMAKE_DEBUG_POSTFIX "d")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/msvc/include
                    ${GETTEXT_PROJECT_DIR}/gettext-runtime)

add_definitions(-DIN_LIBINTL
			    -DENABLE_RELOCATABLE=1
				-DIN_LIBRARY
				-DNO_XMALLOC
				-Dset_relocation_prefix=libintl_set_relocation_prefix
				-Drelocate=libintl_relocate
				-DDEPENDS_ON_LIBICONV=1
				-DHAVE_CONFIG_H
				-D_CRT_SECURE_NO_WARNINGS
				-DLOCALEDIR=\"\"
				-DLOCALE_ALIAS_PATH=\"\"
				-DLIBDIR=\"\"
				-D_GL_INLINE_HEADER_BEGIN=/*_GL_INLINE_HEADER_BEGIN*/
				-D_GL_INLINE_HEADER_END=/*_GL_INLINE_HEADER_END*/
				-Dintmax_t="long int"
				-D_GL_INLINE=inline
        -Dstrdup=_strdup
				)

if(BUILD_SHARED_LIBS)
  
	add_library(intl SHARED ${INTL_SRCS} ${INTL_SRCS} ${CMAKE_CURRENT_SOURCE_DIR}/msvc/libintl.def)
	list(APPEND DEFINITIONS BUILDING_LIBINTL)
	list(APPEND DEFINITIONS BUILDING_DLL)
	set_target_properties(intl PROPERTIES COMPILE_DEFINITIONS "${DEFINITIONS}")
#	install(TARGETS intl RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR})
else()
	add_library(intl STATIC ${INTL_SRCS})
#	install(TARGETS intl-static RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} FRAMEWORK DESTINATION ${CMAKE_INSTALL_LIBDIR})
endif()

install(FILES "${CMAKE_CURRENT_SOURCE_DIR}/msvc/include/libintl.h" DESTINATION include)
install(TARGETS intl
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin)