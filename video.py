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
import os
import warnings

# Requires OpenCV 3
import cv2
cv2_ver = cv2.__version__.split('.')
assert int(cv2_ver[0]) >= 3

# Optional: tiffffile to manage tif videos (i.e. multi-image tiffs)
try:
    from contrib import tifffile
    TIFF_SUPPORT = True
except ModuleNotFoundError:
    TIFF_SUPPORT = False


class VideoTiff:
    '''
    A class for reading a multi-frame tiff. Requires Christoph Gohlke's
    tifffile.py, found here:
    https://www.lfd.uci.edu/~gohlke/code/tifffile.py.html
    '''
    def __init__(self, filename, fps=None):
        self.filename = filename
        if TIFF_SUPPORT is False:
            raise ModuleNotFoundError("Requires tifffile.py")
        self.capture = tifffile.imread(filename)
        self.fourcc = 'N/A' # For compatibility with videoroi
        self._width = self.capture.shape[-1]
        self._height = self.capture.shape[-2]
        self._frame_count = self.capture.shape[-3]
        if fps is None:
            warnings.warn("FPS is not defined, defaulting to 1.")
            fps = 1
        self._fps = fps
        self._current_frame = 0
        self.bits = self.capture.dtype.itemsize * 8
        # An alternative implementation:
        # t = tifffile.TiffFile(filename)
        # page = t.pages[0]
        # page.imagelength, page.imagewidth
        # frame_count = len(t.pages)
        # im = t.pages[9].asarray()
        # bits = page.bitspersample

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def frame_count(self):
        return self._frame_count

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        self._fps = value

    @property
    def duration(self):
        return self.frame_count / self.fps

    def seek_frame(self, frame_number=0):
        '''
        Moves the pointer to frame `frame_number` (0-based index). If
        `frame_number` is greater than the total number of frames, then the
        pointer will be the last frame in the video.
        '''
        if frame_number >= self.frame_count:
            # print("End of file reached.")
            frame_number = self.frame_count - 1
        self._current_frame = frame_number

    def seek_time(self, milliseconds=0):
        '''
        Moves the pointer to the frame that is closest in time to
        `milliseconds`.
        '''
        seconds = milliseconds/1000
        frame = round(seconds * self.fps)
        self.seek_frame(frame)

    def read(self, frame_number=None):
        '''
        Returns video frame `frame_number` (0-based index). If no frame_number
        is specified, the frame returned will be
        '''
        if frame_number is not None:
            # If a specific frame has been requested move the pointer to that
            # frame before reading data.
            self.seek_frame(frame_number)
        # Read the video frame.
        img = self.capture[self.pos_frames, :, :]
        # After reading the frame shift the pointer one place forward so that
        # the next read will return the next frame in the video.
        self.seek_frame(self.pos_frames + 1)
        return img

    @property
    def pos_frames(self):
        return self._current_frame

    @property
    def pos_ms(self):
        '''
        Position in milliseconds
        '''
        return self._current_frame / self.fps * 1000

    @property
    def duration_str(self):
        '''
        Returns total duration in string format min:sec
        '''
        if self.duration is None:
            return ''
        else:
            m = self.duration // 60.
            s = self.duration % 60.
            return '{:02}:{:02}'.format(int(m), int(s))

    def close(self):
        # Does nothing. Needed for compatibility with videoroi
        pass


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
        ret_val, img = self.capture.read()
        return img

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
                # self.capture.release()
                cv2.destroyWindow(self.filename)
                break

    def seek_frame(self, frame_number=0):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def seek_time(self, milliseconds=0):
        self.capture.set(cv2.CAP_PROP_POS_MSEC, milliseconds)

    # def get_pos_frames(self):
    #     return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
    #
    # def get_pos_ms(self):
    #     return self.capture.get(cv2.CAP_PROP_POS_MSEC)

    def get_duration(self):
        '''
        Returns total duration in string format min:sec
        '''
        m = self.duration // 60.
        s = self.duration % 60.
        return '{:02}:{:02}'.format(int(m), int(s))

    def close(self):
        self.capture.release()


if __name__ == "__main__":
    fname = os.path.expanduser("~/projects/photometry/glucose_in_vitro/" +
                               "data/run1_Registered.tif")
    vid = VideoTiff(fname)
