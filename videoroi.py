#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (c) 2016-2018 Antonio González
#
# This file is part of videoroi.
#
# Videoroi is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Videoroi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with videoroi. If not, see <http://www.gnu.org/licenses/>.

import os

from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication,
                             QFileDialog, QLabel)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import pyqtgraph as pg
import numpy as np
import pandas as pd
import cv2

from ui.ui_main import Ui_MainWindow
from video import Video

ROI_PEN = (3, 9)


def fmt_frame_to_time(frame, fps):
    seconds = frame / fps
    minutes = seconds // 60
    seconds = seconds % 60
    return '{:02}:{:05.2f}'.format(int(minutes), seconds)


class Roi(pg.EllipseROI):
    '''
    A labelled ROI.

    This is a subclass derived from pyqtgraph's EllipseROI with an
    added label. Double clicking on it allows to change the label.
    '''
    def __init__(self, parent, pos, size, pen=ROI_PEN, **args):
        # The label must be created before the actual ROI. If not, then
        # the function `stateChanged` below will make the thing crash
        # because it is triggered when the ROI is created.
        self.lbl = pg.TextItem("", anchor=(0.5, 0.5), color=pen)
        super().__init__(pos, size, pen=pen, removable=True, **args)
        self.setParent(parent)
        self.lbl.setPos(self.pos())
        parent.view_box.addItem(self)
        parent.view_box.addItem(self.lbl)

    def setObjectName(self, name):
        '''
        Set the ROI's name.

        Method from EllipseROI, overridden so that the label is updated
        when the name of the ROI is set.
        '''
        self.lbl.setText(name)
        super().setObjectName(name)

    def stateChanged(self, finish=True):
        '''
        Method from EllipseROI, overridden so that the label moves with
        its ROI.
        '''
        super().stateChanged(finish)
        self.lbl.setPos(self.pos())

    def removeClicked(self):
        '''
        Remove both label and ROI when a remove event is requested.

        Method from EllipseROI, overrdiden to remove the label together
        with the ROI when there's a request to remove latter.
        '''
        self.parent().view_box.removeItem(self.lbl)
        self.parent().view_box.removeItem(self)
        super().removeClicked()

    def mouseClickEvent(self, event):
        '''
        A double click pops-up a dialog to change the name of the ROI.

        Method from EllipseROI, overrdiden to present a dialog to change
        the label when the ROI is double clicked.
        '''
        if event.double():
            text, okPressed = QtGui.QInputDialog.getText(
                self.parent(), "Rename ROI", "ROI:",
                QtGui.QLineEdit.Normal, text=self.objectName())
            if okPressed and text != '':
                self.setObjectName(text)
        else:
            super().mouseClickEvent(event)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.video = None
        self.intensity = None
        self.working_dir = os.path.expanduser('~')

        self.fluorescence_box.setDisabled(True)
        self.roi_box.setDisabled(True)
        self._init_image_item()
        self._init_statusbar()
        self._roi_counter = 0

    def _init_image_item(self):
        self.layout = pg.GraphicsLayout()
        self.graphicsView.setCentralItem(self.layout)

        self.view_box = self.layout.addViewBox()
        self.view_box.invertY(True)
        self.view_box.setAspectLocked(True)

        self.img_item = pg.ImageItem()
        self.view_box.addItem(self.img_item)

    def _init_statusbar(self):
        self.statusbar_left = QLabel()
        self.statusbar_right = QLabel()
        self.statusbar.addPermanentWidget(
                self.statusbar_left, stretch=4)
        self.statusbar.addPermanentWidget(
                self.statusbar_right, stretch=1)

    def setup_scrollbar(self):
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(self.video.frame_count)
        self.scrollbar.setValue(0)

    def setup_info(self):
        self.max_frame = self.video.frame_count - 1
        info_text = ('Framerate: {} fps | ' +
                     'Codec: {} | ' +
                     'Dimensions: {} x {}')
        self.statusbar_left.setText(info_text.format(
            self.video.fps,
            self.video.fourcc,
            self.video.width,
            self.video.height))
        self.left_label.setText('00:00.00')
        self.centre_label.setText('Frame 0/{}'.format(
            self.max_frame))
        self.right_label.setText('-' + fmt_frame_to_time(
            self.max_frame, self.video.fps))

    # Scrollbar -------------------------------------------------------

    def on_scrollbar_valueChanged(self):
        if self.video is None:
            return
        frame_number = self.scrollbar.value()
        self.display_video_frame(frame_number)

    # Display video ---------------------------------------------------

    def get_video_frame(self, frame_number):
        frame = self.video.read(frame_number)
        # If the video has 3 dfimensions it is assumed to be RGB; convert
        # gray.
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame.astype('float')  # pg crashes if a uint is passed
        frame = frame.T  # because pg rotates images by 90 deg.
        if self.autoLevel_button.isChecked():
            # If Auto level is selected, set the image display range to the
            # maximum value in that frame.
            levels = (0.0, frame.max())
        else:
            # If no Auto level, then the image is displayed in its full
            # bit-depth range
            levels = (0.0, float(2**self.video.bits_per_sample) - 1)
        return frame, levels

    def display_video_frame(self, frame_number):
        if frame_number < self.video.frame_count:
            self.frame, self.levels = self.get_video_frame(frame_number)
            self.img_item.setImage(self.frame, levels=self.levels)
            self.centre_label.setText("{}/{}".format(frame_number,
                                                     self.max_frame))
            self.left_label.setText(fmt_frame_to_time(
                frame_number, self.video.fps))
            self.right_label.setText('-' + fmt_frame_to_time(
                self.max_frame - frame_number, self.video.fps))

    def on_open_video_button_clicked(self, checked=None):
        if checked is None:
            return
        filename = QFileDialog.getOpenFileName(
                self, caption='Open file...',
                directory=self.working_dir,
                filter='Video files (*.avi *.mp4 *.mov *.tif *.tiff)')
        filename = filename[0]
        if not filename:
            return
        self.open_video(filename)

    def open_video(self, filename):
        if self.video is not None:
            self.video.close()
            self.clear_roi_button.click()

        self.working_dir, short_fname = os.path.split(filename)

        # Open video.
        self.video = Video(filename)

        # Read and display first frame.
        self.frame, levels = self.get_video_frame(frame_number=0)
        self.img_item.setImage(self.frame, levels)
        self.view_box.setRange(xRange=(0, self.video.width),
                               yRange=(0, self.video.height))

        # Display video information.
        self.setWindowTitle(short_fname)
        self.setup_scrollbar()
        self.setup_info()

        # Enable ROI group box.
        self.roi_box.setEnabled(True)

    def on_reset_view_button_clicked(self, checked=None):
        if checked is None:
            return
        self.view_box.setRange(xRange=(0, self.video.width),
                               yRange=(0, self.video.height))

    # ROI buttons -----------------------------------------------------

    @property
    def rois(self):
        return [item for item in self.view_box.addedItems if
                isinstance(item, Roi)]

    def on_add_roi_button_clicked(self, checked=None):
        if checked is None:
            return

        centre = (self.video.width/2, self.video.height/2)
        roi = Roi(parent=self, pos=centre, size=(50, 50))
        roi.setObjectName('roi{}'.format(self._roi_counter))
        self._roi_counter += 1

        if not self.fluorescence_box.isEnabled():
            self.fluorescence_box.setEnabled(True)

    def on_clear_roi_button_clicked(self, checked=None):
        if checked is None:
            return
        if len(self.rois) == 0:
            return

        for roi in self.rois:
            self.view_box.removeItem(roi.lbl)
            self.view_box.removeItem(roi)
        self.intensity = None
        self.fluorescence_box.setDisabled(True)
        self._roi_counter = 0

    def on_load_rois_button_clicked(self, checked=None):
        '''
        Loads ROIs from a tab separated file. This file should consist of
        a header, one line per ROI, and 6 columns:
            roi_name, x_pos, y_pos, x_size, y_size, angle
        '''
        # TODO: The ROI file is hardcoded to be in the same place as video file
        # and with extension _ROI.tsv. Change this so that user can choose the
        # file instead.

        if checked is None:
            return
        filename = os.path.splitext(self.video.filename)
        filename = filename[0] + '_ROIs.tsv'

        rois = pd.read_csv(filename, sep='\t')

        for (index, roi) in rois.iterrows():
            pos = (roi.x_pos, roi.y_pos)
            size = (roi.x_size, roi.y_size)
            new_roi = Roi(parent=self, pos=pos, size=size, angle=roi.angle)
            new_roi.setObjectName(roi['name'])
        self._roi_counter = index + 1

        if not self.fluorescence_box.isEnabled():
            self.fluorescence_box.setEnabled(True)

    def on_save_rois_button_clicked(self, checked=None):
        '''
        Save ROIs as a tsv list. This is a file with a header, one line per ROI
        and 6 columns:
            roi_name, x_pos, y_pos, x_size, y_size, angle

        This file can be loaded later to re-create these ROIs.
        '''
        if checked is None:
            return

        if len(self.rois) == 0:
            self.statusbar_right.setText("Nothing to save")
            return
        filename = os.path.splitext(self.video.filename)
        filename = filename[0] + '_ROIs.tsv'

        headerfmt = '{}\t{}\t{}\t{}\t{}\t{}\n'
        datafmt = '{}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\n'
        header = ("name", "x_pos", "y_pos", "x_size", "y_size", "angle")
        header = headerfmt.format(*header)

        f = open(filename, 'w')
        f.write(header)
        for roi in self.rois:
            data = datafmt.format(roi.objectName(),
                                  roi.pos().x(), roi.pos().y(),
                                  roi.size().x(), roi.size().y(),
                                  roi.angle())
            f.write(data)
        f.close()

    # Fluorescence buttons --------------------------------------------

    def on_measure_button_clicked(self, checked=None):
        if checked is None:
            return

        # Get the ROIs from the list of added items to the view box and sort
        # them by object name.
        if len(self.rois) == 0:
            return
        rois = sorted(self.rois, key=lambda x: x.objectName())

        # Check if any names are duplicated. If so, stop and ask the
        # user to rename the ofending ROI(s).
        names = [roi.objectName() for roi in rois]
        if len(set(names)) != len(names):
            msg = ('Some ROI names are duplicated.\n' +
                   'Fix this before continuing.')
            QtGui.QMessageBox.warning(self.parent(), "Warning", msg)
            return

        # Set-up progress dialog.
        self.statusbar_right.setText("Measure")
        total_frame_count = self.video.frame_count * len(rois)
        total_frame_count -= 1
        progress = QtGui.QProgressDialog(
            'Processing...', 'Cancel', 0, total_frame_count,
            parent=self)
        progress.setWindowModality(Qt.WindowModal)

        # Create a data frame to hold mean intensity values. Each row is a
        # frame and each column is a ROI. Add also a 'time' column.
        frames = np.arange(self.video.frame_count)
        self.intensity = pd.DataFrame(index=frames, columns=['time'] + names)
        self.intensity.index.name = 'frame'
        self.intensity.time = frames / self.video.fps

        # Loop over ROIs and frames and calculate mean intensity.
        for (roi_number, roi) in enumerate(rois):
            mask = np.ones_like(self.frame)
            mask = roi.getArrayRegion(mask, self.img_item)
            mask = mask.astype('bool')
            roi_name = roi.objectName()

            for frame_number in frames:

                # Update progress dialog.
                progress_frame = frame_number + (
                        roi_number * self.video.frame_count)
                progress.setValue(progress_frame)

                # If the user cancels, clear data.
                if progress.wasCanceled():
                    self.intensity = None
                    return

                # Calculate ROI mean intensity.
                frame, _ = self.get_video_frame(frame_number)
                data = roi.getArrayRegion(frame, self.img_item)
                mean_intensity = data[mask].mean()
                self.intensity.loc[frame_number, roi_name] = mean_intensity

        # These lines calculate the intensity of the whole video without
        # looping. They require the video to be fully loaded as a 3D arrray,
        # which is the case when reading tiff files. However, with cv2 it is
        # necessary to read one frame a time, sonce not all the frames are
        # loaded at once when the video is opened. I've compared this 'fast'
        # method to the startdard, looping one, and the results are identical.
        # if IS_TIFF:
        #     roi_region = roi.getArrayRegion(self.video.capture,
        #                                     self.img_item, axes=(2, 1))
        #     mask = roi_region.astype('bool')
        #     roi_region[~mask] = np.nan
        #     intensity = np.nanmean(roi_region, axis=(1, 2))
        # else:
        #     pass

        # Print message to statusbar.
        self.statusbar_right.setText("Done")

    def on_plot_button_clicked(self, checked=None):
        if checked is None:
            return
        if self.intensity is None:
            return

        self.statusbar_right.setText("")

        # Plot window properties. These should probably go in a
        # configuration file/section, but for my current purposes it is
        # just fine to have them here because in practice I never need
        # to modify them.
        x_tick_fontsize = 10
        y_tick_fontsize = 10
        plot_window_size = (600, 300)
        xfont = pg.QtGui.QFont()
        yfont = pg.QtGui.QFont()
        yfont.setPointSize(y_tick_fontsize)
        xfont.setPointSize(x_tick_fontsize)

        self.plot_window = pg.GraphicsWindow(
                title='Fluorescence intensity per ROI')
        # First column is time so should be ignored.
        for column in self.intensity.columns[1:]:
            plt = self.plot_window.addPlot()
            y = self.intensity[column]
            plt.plot(self.intensity.time, y, pen=(3, 9))
            # Set x-axis label.
            plt.setLabel('bottom', 'Frame')
            plt.getAxis('bottom').tickFont = xfont
            # Set y-axis label.
            plt.setLabel('left', 'Raw intensity')
            plt.getAxis('left').tickFont = yfont
            self.plot_window.nextRow()
        self.plot_window.resize(*plot_window_size)
        self.plot_window.show()

    def on_save_button_clicked(self, checked=None):
        '''
        Save intensity data from ROIs in a tab-separated file.
        '''
        if checked is None:
            return
        if self.intensity is None:
            return

        filename = os.path.splitext(self.video.filename)
        filename = filename[0] + '.tsv'
        self.intensity.to_csv(filename, sep='\t')
        self.statusbar_right.setText("Data saved")

    # Quit button -----------------------------------------------------

    def on_quit_button_clicked(self, checked=None):
        if checked is None:
            return
        if self.video is not None:
            self.video.close()
        self.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
            description='Obtain intensity of a ROI in a video')
    parser.add_argument(
            'filename', nargs='?', type=str, default=None,
            help='Open video')
    args = parser.parse_args()

    app = QApplication([])
    window = MainWindow()
    if args.filename:
        window.open_video(args.filename)
    window.show()

    QApplication.instance().exec_()
