# Spritely-Graphical
Updated graphical version of the CLI tool Spritely.

# About and Features
</p>
<p align="center">
Spritely is a free & open-source tool to completely automate your spritesheet creation workflow. 

Features include:

- Evenly remove extra images from a large set, so it can fit on a smaller spritesheet

- Smart trimming (crops all images evenly based on combined maximum dimensions)

- Previewing spritesheet as a .GIF File

- Customizable grid specifications

- Now in GUI!


# Usage

### Step 0.5:

Download spritely_gui.py from this repo, and put it in a folder. cd to the folder with
```sh
cd {YOUR FOLDER PATH}
```

It makes things easier to [set up a venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for this part.

### Step 1:

```sh
pip install pillow
```

```sh
pip install tk
```


### Step 2:

You should be all set now. You can run the script with

```sh
python spritely_gui.py
```


The only reason you'd need to continue from here is if you want to make an executable file.

# Executable

### Step 1: 

Do everything under Usage first.

### Step 2:

```sh
pip install pyinstaller
```

### Step 3:

```sh
pyinstaller --onefile spritely_gui.py
```

Your executable file will be under a folder named 'dist' under your project directory.
