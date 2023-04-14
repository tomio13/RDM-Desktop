# Packages
For windows, especially when users do not really care about having
python installed, it is good to have a binary that can be run.
The zip files in this folder are simpel 'packages', where
the python interpreter and source code are packed together,
building an exe file. This is supplemented with the corresponding
icons and templates.
Extracting the content to a folder (RDM-desktop), one can run
and use the standalone program.

# speed penalty
since python and its libraries are packed into the exe file,
there is a packaging overhead which slows down the start up of the
program.

# versions
The current version has been built and tested on Windows 10 professional.

# build
the program was built using pyinstaller as
```bash
pyinstaller -F ./rdm_project.py
```

