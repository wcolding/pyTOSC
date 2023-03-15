import sys
import os

full_dir = os.getcwd()
working_index = full_dir.rfind(os.path.normpath("/")) + 1
dir = full_dir[working_index:]

is_pyTOSC_folder = dir == "pyTOSC"

if (is_pyTOSC_folder):
    print("Program must be run from containing project directory. Run 'python init.py' first!")
    exit()

doUnpack = False
doBuild = False
doClean = False
doCleanLua = False

from pyTOSC.unpack import Unpack
from pyTOSC.pack import Pack
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

UNPACK_FILE = config["pyTOSC"]["UnpackTarget"]
BUILD_FILE  = config["pyTOSC"]["BuildXML"]

help_string = """Usage: 'python pyTOSC.py [argument]'    
Arguments:
    -u, --unpack      unpack .tosc file
    -b, --build       build .tosc file(s)
    -c, --clean       clean build directory
    -l, --clean-lua   clean lua directory
    Anything else     show these arguments
"""

lua_warning = """WARNING: You have selected 'clean lua directory.' This will erase all files in your Lua folder. 
It is advised you only do this if you are unpacking a .tosc file. Do you wish to proceed? (Y/n): """

def Clean():
    print("Clean selected")
    build_files = os.listdir("Build")
    for file in build_files:
        if file != ".gitignore":
            os.remove(os.path.normpath(f'Build/{file}'))
    print("Build directory cleaned!")

def CleanLua():
    print("Clean Lua selected")
    lua_files = os.listdir("Lua")
    for file in lua_files:
        if file != "Submodules":
            os.remove(os.path.normpath(f'Lua/{file}'))
        else:
            sub_files = os.listdir(os.path.normpath("Lua/Submodules"))
            for sub in sub_files:
                os.remove(os.path.normpath(f'Lua/Submodules/{sub}'))
    print("Lua directory cleaned!")

def Help():
    print(help_string)

def ParseChar(char: str):
    match char.lower():
        case "u":
            global doUnpack
            doUnpack = True
        case "b":
            global doBuild
            doBuild = True
        case "c":
            global doClean
            doClean = True
        case "l":
            global doCleanLua
            doCleanLua = True
        

def ParseArgs():
    for arg in sys.argv:
        # Check for multiple args in one string
        if ("-" in arg) and ("--" not in arg):
            for char in arg[1:]:
                ParseChar(char)
        elif ("--" in arg):
            match arg.lower():
                case "--unpack":
                    global doUnpack
                    doUnpack = True
                case "--build":
                    global doBuild
                    doBuild = True
                case "--clean":
                    global doClean
                    doClean = True
                case "--clean-lua":
                    global doCleanLua
                    doCleanLua = True
                
    
    if doCleanLua:
        confirm_clean = input(lua_warning)
        if confirm_clean.lower() == "y":
            CleanLua()
        else:
            print("Cancelling clean lua function...")
    if doUnpack:
        Unpack(UNPACK_FILE)
    if doClean:
        Clean()
    if doBuild:
        Pack(BUILD_FILE)

    if (doUnpack | doBuild | doClean | doCleanLua) == False:
        Help()

if (len(sys.argv) < 2):
    print("Expected argument\n")
    Help()
    exit()
else:
    ParseArgs()