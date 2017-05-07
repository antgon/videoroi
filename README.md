VideoROI
========

Get fluorescence intensity from one or more regions of interest (ROI)
in a video.

Originally written to obtain fluorescence changes over time of cells in
vitro that express a calcium indicator (GCaMP).


Requirements
------------

* python3
* pyqtgraph
* pyqt5
* numpy
* cv2 version 3


How to use
----------

Run

`python3 videoroi.py`

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
   added. *Clear* will remove all ROIs.

4. Click *Measure* to measure fluorescence in the ROIs across all
   frames in the video.

5. Click *Plot* to display a plot of raw fluorescence by frame.

6. Click *Save* to save the data (fluorescence per ROI by frame). The
   data will be saved as csv file in the same directory as the source
   video.
