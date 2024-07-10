# pyTOSC
This repo is intended to be used as a git submodule for managing source control of TouchOSC files using Python. Through a simple Python script you can unpack the XML and Lua from a .tosc file, edit them externally, and repack them. There is also some support for automating multiple builds from one source XML file, as well as for replicating button controls. This work is in progress!

## Projects that use pyTOSC
**[X32 Touchscreen](https://github.com/wcolding/X32-Touchscreen)** - Large touchscreen button interface for routing audio channels to multiple mixbuses using a Behringer X32

**[A2 Touchscreen](https://github.com/wcolding/A2-Touchscreen)** - Tablet interface with X32 mixbuses on tabs instead of in multiple boxes

**[Producer Monitor](https://github.com/wcolding/Producer-Monitor)** - Tablet interface for routing X32 monitor feeds. Users can select presets or make a custom mix

# Requirements
Python 3.10+

# Installing
To begin, enter your repo and run `git submodule add https://github.com/wcolding/pyTOSC`

Enter the submodule directory and run `python init.py`. This should copy and create some project scaffolding in the main repo directory. When it finishes, cd back to the main directory.

# Using
Edit `config.ini` and change the `UnpackTarget` value to the name of the .tosc file you'd like to unpack. This file should be in your main directory. By default all .tosc files should be ignored by git but you can edit the .gitignore if you want to change this.

Then you can run `python pyTOSC.py -u` or `python pyTOSC.py --unpack` and it should populate the folder with XML and Lua files.

When you make your changes you can run `python pyTOSC.py -b` or `python pyTOSC.py --build` to create a .tosc file in the Build folder, according to whatever XML target you specify in `config.ini`.
