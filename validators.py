#!/usr/bin/env python3
"""TODO: Put module docstring HERE.
"""

# =============================================================================
# Copyright (C) 2020 Ljubomir Kurij <kurijlj@gmail.com>
#
# This file is part of Radiochromic Denoiser.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================


# =============================================================================
#
# 2020-10-24 Ljubomir Kurij <ljubomir_kurij@protonmail.com.com>
#
# * algorithms.py: created.
#
# =============================================================================


# ============================================================================
#
# TODO:
#
#
# ============================================================================


# ============================================================================
#
# References (this section should be deleted in the release version)
#
#
# ============================================================================

# =============================================================================
# Modules import section
# =============================================================================

from imghdr import what
from pathlib import Path


# =============================================================================
# Module level constants
# =============================================================================

# Supported image types by ImageDir and ImageScan classes.
IMAGE_TYPES = (
    'rgb',
    'gif',
    'pbm',
    'pgm',
    'ppm',
    'tiff',
    'rast',
    'xbm',
    'jpeg',
    'bmp',
    'png',
    'webp',
    'exr'
    )


# =============================================================================
# Models classes and functions
# =============================================================================

class ColorChannelSelection():
    """TODO: Put class docstring here.
    """

    valid_channels = ('red', 'green', 'blue')

    def __init__(self, chnl=None):
        self._chnl = chnl

    @property
    def int(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is not None:
            if self.isValid():
                map_to_int = {'red': 0, 'green': 1, 'blue': 2}
                return map_to_int[self._chnl]

        return None

    @property
    def value(self):
        """TODO: Put method docstring here.
        """

        return self._chnl

    def isNone(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is None:
            return True

        return False

    def isValid(self):
        """TODO: Put method docstring here.
        """

        if self._chnl is not None:
            if self._chnl in ColorChannelSelection.valid_channels:
                return True

            return False

        return True


class ImageFileValidate():
    """TODO: Put class docstring here.
    """

    def __init__(self, image_file_type, file_path=None):
        if image_file_type not in IMAGE_TYPES:
            raise ValueError(
                'Image type not supported (\'{0}\')'.format(image_file_type)
                )

        self._type = image_file_type

        if file_path is not None:
            self._file_path = Path(file_path)
        else:
            self._file_path = None

    @property
    def file_name(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is not None:
            return self._file_path.name

        return None

    @property
    def file_type(self):
        """TODO: Put method docstring here.
        """

        return self._type

    def absolutePath(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is not None:
            return self._file_path.resolve()

        return None

    def fileExists(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is not None:
            return self._file_path.exists()

        return False

    def isFile(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is not None:
            return self._file_path.is_file()

        return False

    def isNonePath(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is None:
            return True

        return False

    def isTypeValid(self):
        """TODO: Put method docstring here.
        """

        if self._file_path is not None and what(self._file_path) == self._type:
            return True

        return False


class ResolutionSelection():
    """TODO: Put class docstring here.
    """

    valid_units = ('dpi', 'dpcm')

    def __init__(self, units=None, resolution=None):
        self._units = units
        self._resolution = resolution

    @property
    def units(self):
        """TODO: Put method docstring here.
        """

        return self._units

    @property
    def resolution(self):
        """TODO: Put method docstring here.
        """

        return self._resolution

    def isNone(self):
        """TODO: Put method docstring here.
        """

        if self._units is None:
            return True

        return False

    def validUnits(self):
        """TODO: Put method docstring here.
        """

        if self._units is not None:
            if self._units in ResolutionSelection.valid_units:
                return True

            return False

        return True

    def validResolution(self):
        """TODO: Put method docstring here.
        """

        if self._units is not None:
            if self._resolution > 0:
                return True

            return False

        return True


class TiffConformityValidate():
    """TODO: Put class docstring here.
    """

    valid_bitspersample = [8, 16, 32, 64]

    def __init__(
            self,
            target_size=None,
            target_units=None,
            target_resolution=None,
            ):

        self._target_size = target_size
        self._target_units = target_units
        self._target_resolution = target_resolution
        self._tiff_object = None

    @property
    def target_units(self):
        """Put method docstring HERE.
        """

        return self._target_units

    @property
    def target_size(self):
        """Put method docstring HERE.
        """

        return self._target_size

    @property
    def target_resolution(self):
        """Put method docstring HERE.
        """

        return self._target_resolution

    @property
    def tiff_object(self):
        """Put method docstring HERE.
        """

        return self._tiff_object

    @tiff_object.setter
    def tiff_object(self, tiff_object=None):
        """Put method docstring HERE.
        """

        if tiff_object is not None:
            self._tiff_object = tiff_object

    def bitsPerSampleMatch(self):
        """Put method docstring HERE.
        """

        if self._tiff_object.pages[0].bitspersample in \
                TiffConformityValidate.valid_bitspersample:
            return True

        return False

    def resolutionMatch(self):
        """Put method docstring HERE.
        """

        if self._target_units is not None:
            if self._tiff_object is not None:
                res_x = self._tiff_object.pages[0].tags['XResolution'].value[0]
                res_y = self._tiff_object.pages[0].tags['YResolution'].value[0]
                if res_x == self._target_resolution \
                        and res_y == self._target_resolution:
                    return True

                return False

        return True

    def sizeMatch(self):
        """Put method docstring HERE.
        """

        if self._tiff_object is not None \
                and self._target_size is not None:
            height = self._tiff_object.pages[0].shape[0]
            width = self._tiff_object.pages[0].shape[1]
            if height == self._target_size[0]\
                    and width == self._target_size[1]:
                return True

        return False

    def unitsMatch(self):
        """Put method docstring HERE.
        """

        if self._target_units is not None:
            if self._tiff_object is not None:
                units = res_unit_string(
                    self._tiff_object.pages[0].tags['ResolutionUnit'].value
                    )
                if units == self._target_units:
                    return True

                return False

        return True


def res_unit_string(res_unit):
    """TODO: Put function docstring here.
    """

    if res_unit == 2:
        return 'dpi'

    if res_unit == 3:
        return 'dpcm'

    return 'none'


def res_unit_value(res_unit_str):
    """TODO: Put function docstring here.
    """

    if res_unit_str == 'dpi':
        return 2

    if res_unit_str == 'dpcm':
        return 3

    return 1
