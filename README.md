VideoROI
========

Get mean fluorescence intensity from one or more regions of interest
(ROI) in a video.

Originally written to obtain fluorescence changes over time in cells *in
vitro* that express a calcium indicator (see Suppl. Fig. 3 in González
*et al*, [Curr Biol 26: 2486, 2016](http://dx.doi.org/10.1016/j.cub.2016.07.013).

Copyright (c) 2016-2018, Antonio González.

Created at The Francis Crick Institute and at the University of Aberdeen.


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

    apt-get install python3-pyqtgraph python3-pyqt5 python3-numpy python3-opencv python3-pandas

Additional support for TIFF videos (i.e. multi-frame TIFF files) requires
Christoph Gohlke's [`tifffile.py`](https://www.lfd.uci.edu/~gohlke/) or
[`scikit-image`](https://scikit-image.org/). Both are availble from pip.


How to use
----------

Run

    python3 videoroi.py

from the command window to launch VideoROI (optional: pass a video file
name as an extra argument to open that file directly). Then:

1. *Open* a video file.

2. With the slider at the bottom of the widow navigate to a frame in the
video where a fluorescent cell or cells can be clearly seen. The mouse
can be used to zoom in/out (wheel) or move the field of view (click and
drag). *Reset view* displays the frame in full again after
zooming/dragging. *Auto level* will stretch the image depth to its
maximum; deselect to display the image in the video's full bit-depth
range.

3. Click *Add* to add a ROI. Drag the ROI to the cell of interest and
adjust its size and shape as necessary. More than one ROI can be added.
*Clear* will remove all ROIs. *Double clicking* on a ROI will allow to
change its name, and a *right click* will present a dialog with the
option to remove it.

4. Click *Measure* to calculate mean intensity in each ROI across all
frames in the video.

5. Click *Plot* to display the measured intensity by frame.

6. Click *Save* to save the data (intensity by ROI and frame). The data
will be saved as a tab-separated values (.tsv) file in the same
directory as the source video.

7. Optional: click the *Save* button in the ROI box to save the ROIs as
a .tsv file. This file can be loaded later to re-create the ROIs used.

8. Optional: Right click on the working space (the image) to save the
image and its ROIs for future reference.


Alternatives
------------

As an alternative to videoROI, it is possible to do a similar analysis
of fluorescence intensity using Fiji/ImageJ by following these steps:

1. Open the file in Fiji.

1. Go to *Analyze* → *Tools* → *ROI Manager...*

1. Add ROIs: select shape from toolbar, add to image, then *Add* on ROI Manager.

1. Tick *Show All* on ROI Manager to display all the ROIs.

1. Select all ROIs on ROI Manager (shift click).

1. ROI Manager → More >> Multi Measure

1. Tick *Measure all slices*; untick *One row per slice*; click OK.

1. Save as csv.
