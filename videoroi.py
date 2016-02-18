#!/usr/bin/env python3
# coding=utf-8

import sys, os

from PyQt4.QtGui import (QMainWindow, QWidget, QMessageBox,
                         QApplication, QFont, QDialog,
                         QFileDialog, QLabel)
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

        self.video = None
        self.rois = []
        self.intensity = None
        self.working_dir = '.'

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
        self.statusbar_centre = QLabel()
        self.statusbar_right = QLabel()
        self.statusbar.addPermanentWidget(
                self.statusbar_left, stretch=2)
        self.statusbar.addPermanentWidget(
                self.statusbar_centre, stretch=1)
        self.statusbar.addPermanentWidget(
                self.statusbar_right, stretch=1)

    def setup_scrollbar(self):
        self.scrollbar.setMinimum(0)
        self.scrollbar.setMaximum(self.video.frame_count)
        self.scrollbar.setValue(0)

    def setup_statusbar(self):
        self.statusbar_left.setText("fps: {} | Duration: {}".format(
            self.video.fps, self.video.get_duration()))
        self.statusbar_centre.setText("00:00.00")
        self.statusbar_right.setText("Frame 0/{}".format(
            self.video.frame_count))

    def on_scrollbar_valueChanged(self):
        if self.video is None:
            return
        frame_number = self.scrollbar.value()
        self.display_video_frame(frame_number)

    def get_video_frame(self, frame_number):
        ret_val, frame = self.video.read(frame_number)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame.astype('float') # pg crashes if a uint is passed
        frame = frame.T # because pg rotates images by 90 deg.
        if self.autoLevel_button.isChecked():
            levels = (0.0, frame.max())
        else:
            levels = (0.0, 255.0)
        return frame, levels

    def display_video_frame(self, frame_number):
        if frame_number < self.video.frame_count:
            self.frame, self.levels = self.get_video_frame(frame_number)
            self.img_item.setImage(self.frame, levels=self.levels)
            self.statusbar_right.setText('Frame {}/{}'.format(
                frame_number, self.video.frame_count))
            self.statusbar_centre.setText(
                    fmt_frame_to_time(frame_number, self.video.fps))

    def on_open_video_button_clicked(self, checked=None):
        if checked is None: return
        filename = QFileDialog.getOpenFileName(
                self, caption='Open file...',
                directory = self.working_dir,
                filter='Video files (*.avi *.mp4 *.mov)')
        if not filename: return
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

        # Display video information.
        self.setWindowTitle(short_fname)
        self.setup_statusbar()
        self.setup_scrollbar()

        # Enable ROI group box.
        self.roi_box.setEnabled(True)
    
    # ROI buttons -----------------------------------------------------

    def on_add_roi_button_clicked(self, checked=None):
        if checked is None: return
        centre = (self.video.width/2, self.video.height/2)
        roi = pg.EllipseROI(pos=centre, size=[50, 50], pen=(3, 9))
        roi.setObjectName('roi{}'.format(len(self.rois)))
        self.view_box.addItem(roi)
        self.rois.append(roi)
        if not self.fluorescence_box.isEnabled():
            self.fluorescence_box.setEnabled(True)

    def on_clear_roi_button_clicked(self, checked=None):
        if checked is None: return
        if len(self.rois) == 0: return
        for roi in self.rois:
            self.view_box.removeItem(roi)
        self.rois = []
        self.fluorescence_box.setDisabled(True)

    # Fluorescence buttons --------------------------------------------

    def on_measure_button_clicked(self, checked=None):
        if checked is None: return

        self.measure_button.setDisabled(True)
        
        frames = np.arange(self.video.frame_count)
        time = frames / self.video.fps
        self.intensity = np.empty([self.video.frame_count,
            len(self.rois)])

        for (roi_number, roi) in enumerate(self.rois):
            mask = np.ones_like(self.frame)
            mask = roi.getArrayRegion(mask, self.img_item)
            mask = mask.astype('bool')
            sys.stdout.write('\n')
            for frame_number in frames:
                sys.stdout.write('Processing frame {}/{}\r'.format(
                    frame_number, self.video.frame_count))
                frame, _ = self.get_video_frame(frame_number)
                data = roi.getArrayRegion(frame, self.img_item)
                mean_intensity = data[mask].mean()
                self.intensity[frame_number, roi_number] = (
                        mean_intensity)

        self.intensity = np.c_[frames, time, self.intensity]

        self.statusbar_right.setText("Done")
        self.measure_button.setEnabled(True)

    def on_plot_button_clicked(self, checked=None):
        if checked is None: return
        if self.intensity is None: return
        x = self.intensity[:,0]
        win = pg.GraphicsWindow()
        for c, y in enumerate(self.intensity[:,2:].T):
            plt = win.addPlot()
            plt.plot(x, y, pen=(3, 9))
            win.nextRow()
        win.show()

    def on_save_button_clicked(self, checked=None):
        '''
        Save intensity data from ROIs in a tab-separated file.
        '''
        if checked is None: return

        names = [roi.objectName() for roi in self.rois]
        header = ['frame', 'time'] + names
        header = '\t'.join(header)
        fmt = '%i\t%f' + ('\t%.4f' * len(self.rois))

        filename = os.path.splitext(self.video.filename)
        filename = filename[0] + '.tab'
        np.savetxt(filename, self.intensity, fmt=fmt, header=header,
                comments="")
        self.statusbar_right.setText("Saved")

    # Quit button -----------------------------------------------------

    def on_quit_button_clicked(self, checked=None):
        if checked is None: return
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
