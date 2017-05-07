#! /usr/bin/env python3
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
import numpy as np

# Requires OpenCV 3
import cv2
cv2_ver = cv2.__version__.split('.')
assert int(cv2_ver[0]) >= 3

class Video:
    '''
    A class for reading, seeking, and playing videos.

    This class uses cv2.VideoCapture to open a video. It builds on top
    of that class to provide useful functions to facilitate reading
    frames from videos.
    '''
    def __init__(self, filename):
        self.filename = filename
        self.capture = cv2.VideoCapture(filename)

        if self.capture.isOpened():
            self.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            self.frame_count = int(self.capture.get(
                cv2.CAP_PROP_FRAME_COUNT))
            fourcc = int(self.capture.get(cv2.CAP_PROP_FOURCC))
            self.fourcc = fourcc.to_bytes(4, sys.byteorder).decode()
            self.duration = self.frame_count / self.fps

    def read(self, frame_number=None):
        if frame_number is not None:
            self.seek_frame(frame_number)
        return self.capture.read()

    def _on_trackbar(self, frame_number):
        self.seek_frame(frame_number)
        ret_val, frame = self.read()
        if ret_val:
            cv2.imshow(self.filename, frame)

    #def play(self):
        #cv2.namedWindow(self.filename, cv2.WINDOW_AUTOSIZE)
        #cv2.createTrackbar('Frame #', self.filename, 0,
                #self.frame_count, self._on_trackbar)

        #self.seek_frame(0)
        #ret_val, frame = self.read()
        #cv2.imshow(self.filename, frame)
        #key = cv2.waitKey(0)
        #if key == 27:
            #cv2.destroyWindow(self.filename)

    def play(self):
        while True:
            ret_val, frame = self.read()
            if ret_val is False:
                break
            cv2.imshow(self.filename, frame)
            key = cv2.waitKey(1)
            if key == 27:
                #self.capture.release()
                cv2.destroyWindow(self.filename)
                break

    def seek_frame(self, frame_number=0):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def seek_time(self, milliseconds=0):
        self.capture.set(cv2.CAP_PROP_POS_MSEC, milliseconds)

    def get_pos_frames(self):
        return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    def get_pos_ms(self):
        return self.capture.get(cv2.CAP_PROP_POS_MSEC)

    def get_duration(self):
        '''
        Returns total duration in string format min:sec
        '''
        m = self.duration // 60.
        s = self.duration % 60.
        return '{:02}:{:02}'.format(int(m), int(s))

    def close(self):
        self.capture.release()
