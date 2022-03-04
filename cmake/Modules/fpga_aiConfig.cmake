INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_FPGA_AI fpga_ai)

FIND_PATH(
    FPGA_AI_INCLUDE_DIRS
    NAMES fpga_ai/api.h
    HINTS $ENV{FPGA_AI_DIR}/include
        ${PC_FPGA_AI_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    FPGA_AI_LIBRARIES
    NAMES gnuradio-fpga_ai
    HINTS $ENV{FPGA_AI_DIR}/lib
        ${PC_FPGA_AI_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/fpga_aiTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(FPGA_AI DEFAULT_MSG FPGA_AI_LIBRARIES FPGA_AI_INCLUDE_DIRS)
MARK_AS_ADVANCED(FPGA_AI_LIBRARIES FPGA_AI_INCLUDE_DIRS)
