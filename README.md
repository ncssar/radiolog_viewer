# radiolog_viewer
semi-real-time view-only interface for radiolog data files being written on a shared drive

# installation
You will need to install pygtail and regex modules:
```
pip install pygtail
pip install regex
```
To run the viewer, run radiolog_viewer.bat.

The first time you run radiolog_viewer.bat, the file local/radiolog_viewer.cfg will be created.  You will probably need to edit that file by hand to make sure it is looking at the correct shared file location where radiolog is creating its data.
