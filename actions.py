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
# 2020-10-25 Ljubomir Kurij <ljubomir_kurij@protonmail.com>
#
# * actions.py: created.
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

from sys import (
    stderr,
    stdout
    )
from os.path import basename
from tifffile import (
    imwrite,
    TiffFile
    )
import numpy as np
import validators as vd


# =============================================================================
# Module level constants
# =============================================================================

APP_EXIT_CODES = {
    'noerr': 0,
    'nonexisten_path': 1,
    'no_valid_images': 2,
    'units_not_supported': 3,
    'invalid_resolution': 4,
    'invalid_color_channel': 5,
    'unknown_error': 6
    }


# =============================================================================
# Module utility classes and functions
# =============================================================================

def type_from_bitdepth(bitdepth):
    """TODO: Put function docstring here.
    """

    if bitdepth == 8:
        return np.uint8

    if bitdepth == 16:
        return np.uint16

    if bitdepth == 32:
        return np.uint32

    return np.uint64


# =============================================================================
# App action classes
# =============================================================================

class ProgramAction():
    """Abstract base class for all program actions, that provides execute.

    The execute method contains code that will actually be executed after
    arguments parsing is finished. The method is called from within method
    run of the CommandLineApp instance.
    """

    def __init__(self, exitf):
        self._exit_app = exitf

    def execute(self):
        """TODO: Put method docstring HERE.
        """


class ProgramUsageAction(ProgramAction):
    """Program action that formats and displays usage message to the stdout.
    """

    def __init__(self, parser, exitf):
        super().__init__(exitf)
        self._usg_msg = \
            '{usage}Try \'{prog} --help\' for more information.'\
            .format(usage=parser.format_usage(), prog=parser.prog)

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        print(self._usg_msg)
        self._exit_app(APP_EXIT_CODES['noerr'])


class ShowVersionAction(ProgramAction):
    """Program action that formats and displays program version information
    to the stdout.
    """

    def __init__(self, prog, ver, year, author, license, exitf):
        super().__init__(exitf)
        self._ver_msg = \
            '{0} {1} Copyright (C) {2} {3}\n{4}'\
            .format(prog, ver, year, author, license)

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        print(self._ver_msg)
        self._exit_app(APP_EXIT_CODES['noerr'])


class DefaultAction(ProgramAction):
    """Program action that wraps some specific code to be executed based on
    command line input. In this particular case it prints simple message
    to the stdout.
    """

    def __init__(self, prog, exitf):
        super().__init__(exitf)
        self._program_name = prog
        self._validators = {
            'resolution': vd.ResolutionSelection(None, None),
            'color': vd.ColorChannelSelection(None),
            'file': vd.ImageFileValidate('tiff', None),
            'tif': vd.TiffConformityValidate(None, None, None)
            }
        self._input_list = tuple()
        self._valid_images = list()

    def execute(self):
        """TODO: Put method docstring HERE.
        """

        for image in self._valid_images:
            print('Processing image: \'{0}\' ...'.format(image.filename))
            stdout.flush()

            # We need bits per sample to properly calculate inverted
            # pixel value.
            bits = image.pages[0].bitspersample
            bits_type = type_from_bitdepth(bits)

            # We need image size to properly allocate storage for the result.
            height = image.pages[0].shape[0]
            width = image.pages[0].shape[1]

            # Convert pixels to an array.
            data = image.asarray().astype(bits_type)

            # Here we will store resulting pixel values.
            result = None

            # Allocate memory for the storing of resulting pixel values.
            if self._validators['color'].isNone():
                result = np.zeros(
                    (height, width, 3),
                    dtype=bits_type
                    )
            else:
                result = np.zeros(
                    (height, width),
                    dtype=bits_type
                    )

            # Invert pixel values.
            if self._validators['color'].isNone():
                result[:, :, 0] = np.iinfo(bits_type).max - data[:, :, 0]
                result[:, :, 1] = np.iinfo(bits_type).max - data[:, :, 1]
                result[:, :, 2] = np.iinfo(bits_type).max - data[:, :, 2]

            else:
                result = np.iinfo(bits_type).max \
                    - data[:, :, self._validators['color'].int]

            # Format output file name.
            file_name_split = image.filename.split('.')
            output_name = file_name_split[0]
            if not self._validators['color'].isNone():
                output_name += '_{0}'.format(self._validators['color'].value)
            output_name += '_inverted.tif'

            # Save result to a file.
            print('Saving to the \'{0}\' ...'.format(output_name))
            stdout.flush()

            # Save with original image resolution.
            res_units = image.pages[0].tags['ResolutionUnit'].value
            res_x = image.pages[0].tags['XResolution'].value[0]
            res_y = image.pages[0].tags['YResolution'].value[0]
            imwrite(
                output_name,
                result,
                resolution=(res_x, res_y),
                metadata={'ResolutionUnit': res_units}
                )

        self._exit_app(APP_EXIT_CODES['noerr'])

    def newColorSelectionValidator(self, channel=None):
        """TODO: Put method docstring HERE.
        """

        if channel is not None:
            self._validators['color'] \
                = vd.ColorChannelSelection(channel)

    def newInputList(self, file_list):
        """TODO: Put method docstring HERE.
        """

        self._input_list = (file_list)

    def newResolutionSelectionValidator(self, units=None, resolution=None):
        """TODO: Put method docstring HERE.
        """

        if units is not None:
            self._validators['resolution'] \
                = vd.ResolutionSelection(units, resolution)

    def newTiffValidator(self, target_size=None, target_units=None,
            target_resolution=None):
        """TODO: Put method docstring HERE.
        """

        if target_units is not None and target_resolution is not None:
            self._validators['tif'] \
                = vd.TiffConformityValidate(
                    target_size,
                    target_units,
                    target_resolution
                    )

    def validateInput(self):
        """TODO: Put method docstring HERE.
        """

        # Validate resolution selection.
        if not self._validators['resolution'].isNone():
            # User has supplied target resolution. Check supplied values.

            if not self._validators['resolution'].validUnits():
                # Invalid units string passed as option argument.
                print(
                    '{0}: Supplied resolution units \'{1}\' '.format(
                        self._program_name,
                        self._validators['resolution'].units
                        )
                    + 'are not supported.',
                    file=stderr
                    )

                self._exit_app(APP_EXIT_CODES['units_not_supported'])

            if not self._validators['resolution'].validResolution():
                # Invalid units string passed as option argument.
                print(
                    '{0}: Invalid resolution value \'{1}\'.'\
                            .format(
                        self._program_name,
                        self._validators['resolution'].resolution
                        ),
                    file=stderr
                    )

                self._exit_app(APP_EXIT_CODES['invalid_resolution'])

        # Resolution selection is valid so we can spawn new tif validator.
        self.newTiffValidator(
            None,  # We don;t care about image dimensions.
            self._validators['resolution'].units,
            self._validators['resolution'].resolution,
            )

        # Validate color channel selection.
        if not self._validators['color'].isValid():
            # Color channel option value is not valid.
            print(
                '{0}: Supplied color channel value ({1}) is not supported.'\
                        .format(
                    self._program_name,
                    self._validators['color'].value
                    ),
                file=stderr
                )

            self._exit_app(APP_EXIT_CODES['invalid_color_channel'])

        # Validate files selection.
        for file_path in self._input_list:
            print('Checking path for file: \'{0}\' ...'\
                .format(basename(file_path)))
            stdout.flush()

            file_vd = vd.ImageFileValidate('tiff', file_path)

            if not file_vd.fileExists():
                print(
                    '{0}: Supplied path \'{1}\' does not exist.'.format(
                        self._program_name,
                        file_vd.absolutePath()
                        ),
                    file=stderr
                    )
                stderr.flush()

                # File with given path does not exist at all so skip to
                # the nest file in the list.
                continue

            if not file_vd.isFile():
                print(
                    '{0}: Supplied path \'{1}\' is not a file.'.format(
                        self._program_name,
                        basename(file_path)
                        ),
                    file=stderr
                    )
                stderr.flush()

                # File with given path is not a file so skip to the nest file
                # in the list.
                continue

            if not file_vd.isTypeValid():
                print(
                    '{0}: Supplied path \'{1}\' is not an \'tif\' image.'\
                            .format(
                        self._program_name,
                        basename(file_path)
                        ),
                    file=stderr
                    )
                stderr.flush()

                # File with given path is not an 'tif' image so skip to
                # the nest file in the list.
                continue

            # We have a path pointing to the file of the valid type, so let's
            # check if file conforms to user set resolution.
            print('Loading image: \'{0}\' ...'.format(basename(file_path)))
            stdout.flush()

            tif_obj = TiffFile(file_path)
            self._validators['tif'].tiff_object = tif_obj

            if not self._validators['tif'].bitsPerSampleMatch():
                print(
                    '{0}: Image \'{1}\' does not conform to the required'
                    .format(self._program_name, basename(file_path))
                    + ' bits per sample: {0}.'
                    .format(tif_obj.pages[0].bitspersample),
                    file=stderr
                    )
                stderr.flush()

                # Image bits per sample don't conform to supported bits per
                # sample values (8, 16, 32, 64) so go to the next image in
                # the list.
                continue

            if not self._validators['tif'].unitsMatch():
                print(
                    '{0}: Image \'{1}\' does not conform to the required'
                    .format(self._program_name, basename(file_path))
                    + ' resolution units: {0}.'
                    .format(self._validators['tif'].target_units),
                    file=stderr
                    )
                stderr.flush()

                # Image resolution units don't conform to a user set
                # resolution units so go to the next image in the list.
                continue

            if not self._validators['tif'].resolutionMatch():
                print(
                    '{0}: Image \'{1}\' does not conform to the required'
                    .format(self._program_name, basename(file_path))
                    + ' resolution: {0}.'.format(
                        self._validators['tif'].target_resolution
                        ),
                    file=stderr
                    )
                stderr.flush()

                # Image resolution doesn't conform to a user set resolution
                # units so go to the next image in the list.
                continue

            # We have a path pointing to the file of the valid type so we can
            # add it to the list of files to be processed.
            self._valid_images.append(tif_obj)

        # Before we proceed we have to check if we have any file path in our
        # valid files list. If we don't we print the error message and exit
        # the application.
        if len(self._valid_images) == 0:
            # No valid files on the list.
            print(
                '{0}: Supplied file list contains no valid image files.'\
                    .format(self._program_name),
                file=stderr
                )

            self._exit_app(APP_EXIT_CODES['no_valid_images'])
