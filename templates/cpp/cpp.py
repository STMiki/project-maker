import os
import json
import shutil
import pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
CONFIG_FILE = "config.json"
DEPENDANCY_PATH = "_deps"
COMMON_PATH = "_common"
MULTI_PATH = "_multi"

class ConanFile():
    """"""
    packages = []
    options = []
    generators = []

    def read(self, path):
        with open(path, 'r') as f:
            req = False
            opt = False
            gen = False

            for _line in f.readlines():
                line = _line.strip()

                if line == "":
                    continue

                if line == "[requires]":
                    req = True
                    gen = False
                    opt = False
                    continue
                elif line == "[generators]":
                    req = False
                    gen = True
                    opt = False
                    continue
                elif line == "[options]":
                    req = False
                    gen = False
                    opt = True
                    continue

                if req:
                    self.require(line)
                elif opt:
                    self.option(line)
                elif gen:
                    self.generator(line)


    def write(self, path):
        with open(path, 'w') as f:
            f.write(str(self))

    def require(self, package):
        self.packages.append(package)

    def generator(self, gen):
        if gen not in self.generators:
            self.generators.append(gen)

    def option(self, opt):
        self.options.append(opt)

    def __str__(self):
        result = "[requires]\n"
        for pkg in self.packages:
            result += pkg + "\n"
        result += "\n[generators]\n"
        for generator in self.generators:
            result += generator + "\n"
        result += "\n[options]\n"
        for opt in self.options:
            result += opt + "\n"
        return result + "\n"

class ConfigFile():
    """"""

    need_init = []
    deps = []

    def __init__(self, path: str):
        # Open and read file
        with open(j(path, CONFIG_FILE), 'r') as f:
            self.json = json.load(f)

        self.keys = self.json.keys()

        # Need init
        self.need_init = []
        if "need_init" in self.keys:
            need_init = self.json["need_init"]
            for data in need_init:
                file = data if type(data) is type(str()) else j("", *data)
                self.need_init.append(file)

        # Deps
        self.deps = []
        if "deps" in self.keys:
            self.deps = self.json["deps"]

def j(*paths):
    return os.path.join(*paths)

def generate_cmake(path: str, name: str):
    """
cmake_minimum_required(VERSION 3.10)

# Set up project
project(
    <PNAME>
    VERSION 1.0
    LANGUAGES CXX
)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

# Set flags
if(MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "/O2 /Ox")
    set(CMAKE_CXX_FLAGS "/W4")
else()
    set(CMAKE_CXX_FLAGS "-Wall -Wextra -pedantic")
endif()

# Find libraries
find_package(Threads)

"""
    with open(j(path, "CMakeLists.txt"), 'w') as f:
        f.write(generate_cmake.__doc__.replace("<PNAME>", name))

def copyWithProjectName(fileName, projectName, loc, path, dest = "", append=True):
    mode = 'a' if append else 'w'
    shutil.copyfile(j(loc, fileName), j(path, dest, fileName + ".temp"))
    with open(j(path, dest, fileName + ".temp"), "r") as inf:
        with open(j(path, dest, fileName), mode) as outf:
            for line in inf:
                outf.write(line.replace("<PNAME>", projectName))
    os.remove(j(path, dest, fileName + ".temp"))

def init_deps(path: str, dependencies: [str]) -> None:
    deps = []
    for dep in dependencies:
        if not os.path.isdir(j(path, "deps")):
            pathlib.Path(j(path, "deps")).mkdir(parents=True, exist_ok=True)
        shutil.copytree(j(ROOT, dep), j(path, "deps", dep))
        deps.append(dep)
    if len(deps) > 0:
        with open(j(path, "deps", "CMakeLists.txt"), "w") as outfile:
            for dep in deps:
                outfile.write("add_subdirectory(" + dep + ")\n")

def init_common(path: str, name: str) -> None:
    commonPath = j(ROOT, COMMON_PATH)
    shutil.copytree(commonPath, path, dirs_exist_ok=True)
    os.remove(j(path, CONFIG_FILE))

    config = ConfigFile(commonPath)

    for file in config.need_init:
        copyWithProjectName(file, name, commonPath, path, append=False)

# TODO: need to change how _multi folder works
def init_multi(path: str, name: str, subName: str):
    if pathlib.Path(j(path, "CMakeLists.txt")).exists():
        with open(j(path, "CMakeLists.txt"), 'a') as f:
            f.write("add_subdirectory(" + subName + ")" + os.linesep)
        return

    multiPath = j(ROOT, MULTI_PATH)

    files = [f for f in os.listdir(multiPath) if os.path.isfile(j(multiPath, f))]
    for file in files:
        copyWithProjectName(file, name, multiPath, path)

def build(name: str, path: str, template, recursive=False):
    if type(template) != type(""):
        deps = []
        conan = ConanFile()
        generate_cmake(path, name)
        for subName, subTemplate in template:
            pathlib.Path(j(path, subName)).mkdir(parents=True, exist_ok=True)
            deps += build(subName, j(path, subName), subTemplate, recursive=True)
            init_multi(path, name, subName)
            conan.read(j(path, subName, "conanfile.txt"))
            pathlib.Path(j(path, subName, "conanfile.txt")).unlink()
        init_deps(path, deps)
        # TODO: change this to support multi template
        init_common(path, name)
        conan.write(j(path, "conanfile.txt"))
        return

    templatePath = j(ROOT, template)

    config = ConfigFile(templatePath)

    shutil.copytree(templatePath, path, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*config.need_init))
    os.remove(j(path, CONFIG_FILE))

    if not recursive:
        generate_cmake(path, name)

    for data in config.need_init:
        copyWithProjectName(data, name, templatePath, path)

    if recursive:
        return config.deps
    init_deps(path, config.deps)
    init_common(path, name)
