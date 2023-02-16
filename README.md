# pyTOSC
This repo is intended to be used as a git submodule for managing source control of TouchOSC files using Python. Through a simple Python script you can unpack the XML and Lua from a .tosc file, edit them externally, and repack them. There is also some support for automating multiple builds from one source XML file, as well as for replicating button controls. This work is in progress!

# Requirements
Python 3.10+

# Installing
To begin, enter your repo and run `git submodule add https://github.com/wcolding/pyTOSC`

Enter the submodule directory and run `python init.py`. This should copy and create some project scaffolding in the main repo directory. When it finishes, cd back to the main directory.

# Using
Edit `config.ini` and change the `UnpackTarget` value to the name of the .tosc file you'd like to unpack. This file should be in your main directory. By default all .tosc files should be ignored by git but you can edit the .gitignore if you want to change this.

Then you can run `python pyTOSC.py -u` or `python pyTOSC.py --unpack` and it should populate the folder with XML and Lua files.

When you make your changes you can run `python pyTOSC.py -b` or `python pyTOSC.py --build` to create a .tosc file in the Build folder, according to whatever XML target you specify in `config.ini`.

Updated 2/16/23
