import os
import io
import platform
import shutil
import py_compile

print('Making build folder...')
try:
    os.mkdir("..\\Build")
    print('Success!')
except:
    print('Folder already exists...')

print('Making Lua folder...')
try:
    os.mkdir("..\\Lua")
    print('Success!')
except:
    print('Folder already exists...')

print('Making Submodules folder...')
try:
    os.mkdir("..\\Lua\\Submodules")
    print('Success!')
except:
    print('Folder already exists...')

print("Creating submodules dummy file...")
submodules_file = io.open("..\\Lua\\Submodules\\submodules.txt", "w")
submodules_file.close()
print('Success!')

print("Creating version file...")
version_file = io.open("..\\version", "w")
version_file.write("1.0.0")
version_file.close()
print('Success!')

print("Creating gitignore files...")
gitignore_file = io.open("..\\.gitignore", "w")
gitignore_file.write("*.tosc")
gitignore_file.close()

gitignore_file = io.open("..\\Build\\.gitignore", "w")
gitignore_file.write("*.tosc")
gitignore_file.close()
print("Success!")

print("Copying config files...")
print("  (1/4) Builds")
shutil.copy("builds.ini", "..\\builds.ini")
print("  (2/4) Mix Layout")
shutil.copy("tabs.ini", "..\\tabs.ini")
print("  (3/4) Tabs")
shutil.copy("mix_layout.ini", "..\\mix_layout.ini")
print("  (4/4) Config")
shutil.copy("config.ini", "..\\config.ini")
print("Success!")

print("Copying main script...")
shutil.copy("pyTOSC.py", "..\\pyTOSC.py")
print("Success!")

print("\nAll done!")