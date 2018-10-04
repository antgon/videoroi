VideoROI
========

Get fluorescence intensity from one or more regions of interest (ROI)
in a video.

Originally written to obtain fluorescence changes over time of cells *in
vitro* that express a calcium indicator (see Suppl. Fig. 3 in González
*et al*, [Curr Biol 26: 2486, 2016](http://dx.doi.org/10.1016/j.cub.2016.07.013).

Copyright 2016-2017 Antonio González, The Francis Crick Institute.


Requirements
------------

* Python 3.x
* [PyQtGraph](http://pyqtgraph.org/)
* [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)
* [NumPy](http://www.numpy.org/)
* [OpenCV](http://opencv.org/) version 3.0 or above
* [Pandas](https://pandas.pydata.org/)

These are available on the standard repositories; e.g. on Debian/Ubuntu/
Raspbian run (as `su`):

    apt-get install python3-pyqtgraph python3-pyqt5 python3-numpy \
    python3-opencv python3-pandas


How to use
----------

Run

    python3 videoroi.py

from the command window to launch VideoROI. (Optional: pass a video file
name as an extra argument to open that file directly.)

1. *Open* a video file.

2. With the slider at the bottom of the widow navigate to a frame in the
   video where a fluorescent cell or cells can be clearly seen. The
   mouse can be used to zoom in/out (wheel) or move the field of view
   (click and drag). *Reset view* displays the frame in full again after
   zooming/dragging.

3. Click *Add* to add a ROI. Drag the ROI to the cell of interest and
   adjust its size and shape as necessary. More than one ROI can be
   added. *Clear* will remove all ROIs. *Double click* on a ROI will allow
   to change its name, and a *right click* will present a dialog with the
   option to delete it.

4. Click *Measure* to measure fluorescence in the ROIs across all
   frames in the video.

5. Click *Plot* to display a plot of raw fluorescence by frame.

6. Click *Save* to save the data (fluorescence per ROI by frame). The
   data will be saved as tsv file in the same directory as the source
   video.

7. Clicking the *Save* button in the ROI box will save the ROIs used as a tsv
   file. This file can be loaded at a later stage to re-create the ROIs used.

8. Right click on the working space to save an image (with ROIs) for future
   reference.


Alternatives
------------

A similar analysis could be done using Fiji/ImageJ by following these steps:

1. Analyze --> Tools --> ROI Manager...

2. Add ROIs: select shape from toolbar, add to image, then Add on ROI Manager.

3. Tick Show All on ROI Manager to see them all.

4. Select all ROIs on ROI Manager (shift click) - or deselect all.

5. ROI Manager --> More >> Multi Measure

6. Tick Measure all slices; untick One row per slice; click OK

7. Save as csv.
