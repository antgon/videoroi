#! /usr/bin/env python3
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

import sys
import os
import warnings

# Requires OpenCV 3
import cv2
cv2_ver = cv2.__version__.split('.')
assert int(cv2_ver[0]) >= 3


class VideoBase:
    def __init__(self, filename):
        self.filename = filename
        # Placeholders: all these properties must be defined by any
        # class derived from this one.
        self._width = None
        self._height = None
        self._frame_count = None
        self._fps = None
        self.bits_per_sample = None
        # A counter to keep track of current frame.
        self._current_frame = 0
        # FourCC is for information only; optional.
        self.fourcc = None

    @property
    def duration_str(self):
        '''
        Returns total duration in string format h:m:s
        '''
        if self.duration is None:
            return ''
        else:
            s = self.duration % 60
            m = (self.duration // 60) % 60
            h = self.duration // 3600
            return '{:02.0f}:{:02.0f}:{:04.1f}'.format(h, m, s)

    @property
    def fps(self):
        '''
        Frames per second
        '''
        return self._fps

    @fps.setter
    def fps(self, value):
        self._fps = value

    @property
    def width(self):
        '''
        Video width in px
        '''
        return self._width

    @property
    def height(self):
        '''
        Video height in px
        '''
        return self._height

    @property
    def frame_count(self):
        '''
        Number of frames in the video
        '''
        return self._frame_count

    @property
    def duration(self):
        '''
        Duration in seconds
        '''
        return self.frame_count / self.fps

    def close(self):
        # Does nothing by default, but needed for compatibility with
        # videoroi
        pass


class VideoTiff(VideoBase):
    '''
    A class for reading a multi-frame tiff. Requires Christoph Gohlke's
    tifffile.py, found here:

    https://www.lfd.uci.edu/~gohlke/code/tifffile.py.html

    (also available on pip).
    '''
    def __init__(self, filename, fps=None):

        # Requires tiffffile to handle multi-image tiff files.
        try:
            import tifffiles
        except ModuleNotFoundError as error:
            msg = ("Requires `tiffffile` module, available on pip or\n" +
                   "at https://www.lfd.uci.edu/~gohlke/code/" +
                   "tifffile.py.html")
            raise ModuleNotFoundError(msg) from error

        super().__init__(filename)
        self._frames = tifffile.imread(self.filename)
        self._width = self._frames.shape[-1]
        self._height = self._frames.shape[-2]
        self._frame_count = self._frames.shape[-3]
        if fps is None:
            warnings.warn("FPS is not defined, defaulting to 1.")
            fps = 1
        self._fps = fps
        self.bits_per_sample = self._frames.dtype.itemsize * 8

        # An alternative implementation:
        # t = tifffile.TiffFile(filename)
        # page = t.pages[0]
        # page.imagelength, page.imagewidth
        # frame_count = len(t.pages)
        # im = t.pages[9].asarray()
        # bits = page.bitspersample

    def seek_frame(self, frame_number=0):
        '''
        Moves the pointer to frame `frame_number` (0-based index). If
        `frame_number` is greater than the total number of frames, then
        the pointer will be the last frame in the video.
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
        Returns video frame `frame_number` (0-based index). If no
        frame_number is specified, the frame returned will be
        '''
        if frame_number is not None:
            # If a specific frame has been requested move the pointer
            # to that frame before reading data.
            self.seek_frame(frame_number)
        # Read the video frame.
        img = self._frames[self.pos_frames, :, :]
        # After reading the frame shift the pointer one place forward
        # so that the next read will return the next frame in the
        # video.
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


class VideoCv(VideoBase):
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
            self._width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self.capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT))
            self._frame_count = int(self.capture.get(
                cv2.CAP_PROP_FRAME_COUNT))
            self._fps = self.capture.get(cv2.CAP_PROP_FPS)
            fourcc = int(self.capture.get(cv2.CAP_PROP_FOURCC))
            self.fourcc = fourcc.to_bytes(4, sys.byteorder).decode()

            # Read the first frame to get bit depth information
            frame = self.read()
            self.bits_per_sample = frame.dtype.itemsize * 8
            self.seek_frame(0)

    def seek_frame(self, frame_number=0):
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def seek_time(self, milliseconds=0):
        self.capture.set(cv2.CAP_PROP_POS_MSEC, milliseconds)

    def read(self, frame_number=None):
        if frame_number is not None:
            self.seek_frame(frame_number)
        ret_val, img = self.capture.read()
        return img

    # def _on_trackbar(self, frame_number):
    #     self.seek_frame(frame_number)
    #     ret_val, frame = self.read()
    #     if ret_val:
    #         cv2.imshow(self.filename, frame)

    def play(self):
        while True:
            ret_val, frame = self.capture.read()
            if ret_val is False:
                break
            cv2.imshow(self.filename, frame)
            key = cv2.waitKey(1)
            if key == 27:
                # self.capture.release()
                cv2.destroyWindow(self.filename)
                break

    @property
    def pos_frames(self):
        return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    @property
    def pos_ms(self):
        return self.capture.get(cv2.CAP_PROP_POS_MSEC)

    def close(self):
        self.capture.release()


def Video(filename):
    if os.path.splitext(filename)[-1] in (".tif", ".tiff"):
        return VideoTiff(filename)
    else:
        return VideoCv(filename)
