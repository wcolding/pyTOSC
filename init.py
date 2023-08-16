import os
import io
import platform
import shutil
import py_compile

print('Making build folder...')
try:
    os.mkdir(os.path.normpath("../Build"))
    print('Success!')
except:
    print('Folder already exists...')

print('Making Lua folder...')
try:
    os.mkdir(os.path.normpath("../Lua"))
    print('Success!')
except:
    print('Folder already exists...')

print('Making Submodules folder...')
try:
    os.mkdir(os.path.normpath("../Lua/Submodules"))
    print('Success!')
except:
    print('Folder already exists...')

print("Creating submodules dummy file...")
submodules_file = io.open(os.path.normpath("../Lua/Submodules/submodules.txt"), "w")
submodules_file.close()
print('Success!')

print("Creating version file...")
version_file = io.open(os.path.normpath("../version"), "w")
version_file.write("1.0.0")
version_file.close()
print('Success!')

print("Creating gitignore files...")
gitignore_file = io.open(os.path.normpath("../.gitignore"), "w")
gitignore_file.write("*.tosc")
gitignore_file.close()

gitignore_file = io.open(os.path.normpath("../Build/.gitignore"), "w")
gitignore_file.write("*.tosc")
gitignore_file.close()
print("Success!")

print("Copying config files...")
files = os.listdir()
for file in files:
    if str.lower(file[-4:]) == ".ini":
        print("Found config: {0}".format(file))
        print("Copying...", end='')
        shutil.copy(file, os.path.normpath("../{0}".format(file)))
        print("done!")
        
print("Success!")

print("Copying main script...")
shutil.copy("pyTOSC.py", os.path.normpath("../pyTOSC.py"))
print("Success!")

print("\nAll done!")