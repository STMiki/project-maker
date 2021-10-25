file(GLOB_RECURSE SRCS src/*.cpp)

add_executable(
    <PNAME>
    ${SRCS}
)

set_target_properties(
    <PNAME> PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

target_include_directories(<PNAME> PRIVATE include)
target_link_libraries(<PNAME> ${CONAN_LIBS})
