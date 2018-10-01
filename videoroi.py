#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (c) 2016-2017 Antonio González
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

import sys
import os

from PyQt5.QtWidgets import (QMainWindow, QWidget, QMessageBox,
                             QApplication, QDialog, QFileDialog,
                             QLabel, QProgressDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import numpy as np
import cv2

from ui.ui_main import Ui_MainWindow
from video import Video


def fmt_frame_to_time(frame, fps):
    seconds = frame / fps
    minutes = seconds // 60
    seconds = seconds % 60
    return '{:02}:{:05.2f}'.format(int(minutes), seconds)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.rois = []
        self.video = None
        self.intensity = None
        self.working_dir = os.path.expanduser('~')

        self.fluorescence_box.setDisabled(True)
        self.roi_box.setDisabled(True)
        self._init_image_item()
        self._init_statusbar()

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
        ret_val, frame = self.video.read(frame_number)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame.astype('float')  # pg crashes if a uint is passed
        frame = frame.T  # because pg rotates images by 90 deg.
        if self.autoLevel_button.isChecked():
            levels = (0.0, frame.max())
        else:
            levels = (0.0, 255.0)
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
                filter='Video files (*.avi *.mp4 *.mov)')
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

    def on_add_roi_button_clicked(self, checked=None):
        if checked is None:
            return
        centre = (self.video.width/2, self.video.height/2)
        roi = pg.EllipseROI(pos=centre, size=[50, 50], pen=(3, 9))
        roi.setObjectName('roi{}'.format(len(self.rois)))
        self.view_box.addItem(roi)
        self.rois.append(roi)
        if not self.fluorescence_box.isEnabled():
            self.fluorescence_box.setEnabled(True)

    def on_clear_roi_button_clicked(self, checked=None):
        if checked is None:
            return
        if len(self.rois) == 0:
            return
        for roi in self.rois:
            self.view_box.removeItem(roi)
        self.rois = []
        self.intensity = None
        self.fluorescence_box.setDisabled(True)

    # Fluorescence buttons --------------------------------------------

    def on_measure_button_clicked(self, checked=None):
        if checked is None:
            return
        if len(self.rois) == 0:
            return

        self.statusbar_right.setText("")

        # Set-up progress dialog.
        total_frame_count = self.video.frame_count * len(self.rois)
        total_frame_count -= 1
        progress = QProgressDialog(
            'Processing...', 'Cancel', 0, total_frame_count,
            parent=self)
        progress.setWindowModality(Qt.WindowModal)

        # Create array.
        frames = np.arange(self.video.frame_count)
        time = frames / self.video.fps
        self.intensity = np.empty([self.video.frame_count,
                                   len(self.rois)])

        # Loop over ROIs and frames and calculate mean intensity.
        for (roi_number, roi) in enumerate(self.rois):
            mask = np.ones_like(self.frame)
            mask = roi.getArrayRegion(mask, self.img_item)
            mask = mask.astype('bool')
            for frame_number in frames:

                # Update progress dialog.
                progress_frame = frame_number + (
                        roi_number * self.video.frame_count)
                progress.setValue(progress_frame)

                # If the user cancells, clear data.
                if progress.wasCanceled():
                    self.intensity = None
                    return

                # Calculate ROI mean intensity.
                frame, _ = self.get_video_frame(frame_number)
                data = roi.getArrayRegion(frame, self.img_item)
                mean_intensity = data[mask].mean()
                self.intensity[frame_number, roi_number] = (
                        mean_intensity)

        # Concatenate intensity data with frames / time.
        self.intensity = np.c_[frames, time, self.intensity]

        # Print message to statusbar.
        self.statusbar_right.setText("Done")

    def on_plot_button_clicked(self, checked=None):
        if checked is None:
            return
        if self.intensity is None:
            return

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

        x = self.intensity[:, 0]
        self.plot_window = pg.GraphicsWindow(
                title='Fluorescence intensity per ROI')
        for c, y in enumerate(self.intensity[:, 2:].T):
            plt = self.plot_window.addPlot()
            plt.plot(x, y, pen=(3, 9))
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

        names = [roi.objectName() for roi in self.rois]
        header = ['frame', 'time'] + names
        header = '\t'.join(header)
        fmt = '%i\t%f' + ('\t%.4f' * len(self.rois))

        filename = os.path.splitext(self.video.filename)
        filename = filename[0] + '.tab'
        np.savetxt(filename, self.intensity, fmt=fmt, header=header,
                   comments="")
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
