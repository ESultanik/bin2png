#!/usr/bin/env python3

import argparse
import io
import math
import os
import sys

from tempfile import NamedTemporaryFile

from PIL import Image
from bin2png import Encoder

class FileReader(object):
    def __init__(self, path_or_stream, file_backed=False):
        self.tmpfile = None
        if hasattr(path_or_stream, "name") and path_or_stream.name != "<stdin>":
            self.length = os.path.getsize(path_or_stream.name)
            self.file = path_or_stream
            self.name = path_or_stream.name
        else:
            if sys.version_info.major >= 3:
                infile = sys.stdin.buffer.read()
            else:
                infile = sys.stdin.read()
            self.length = len(infile)
            if file_backed:
                if sys.version_info.major >= 3:
                    file_mode = 'wb'
                    read_mode = 'rb'
                else:
                    file_mode = 'w'
                    read_mode = 'r'
                tmp = NamedTemporaryFile(delete=False, mode=file_mode)
                self.tmpfile = tmp.name
                tmp.write(infile)
                tmp.close()
                self.file = open(self.tmpfile, read_mode)
                self.name = self.tmpfile
            else:
                self.file = io.BytesIO(infile)
                self.name = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tmpfile is not None:
            self.file.close()
            os.unlink(self.tmpfile)
            self.tmpfile = None
            self.file = None

    @staticmethod
    def new(path_or_stream, file_backed=False):
        if isinstance(path_or_stream, FileReader):
            return path_or_stream
        else:
            return FileReader(path_or_stream, file_backed=file_backed)

    def __len__(self):
        return self.length

    def read(self, n):
        if sys.version_info.major >= 3:
            return [i for i in self.file.read(n)]
        else:
            return map(ord, self.file.read(n))

def choose_file_dimensions(infile, input_dimensions=None, square=False, verbose=False):
    if input_dimensions is not None and len(input_dimensions) >= 2 and input_dimensions[0] is not None \
            and input_dimensions[1] is not None:
        # the dimensions were already fully specified
        return input_dimensions
    #infile = FileReader.new(infile)
    num_bytes = len(infile)
    num_pixels = int(math.ceil(float(num_bytes) / 3.0))
    sqrt = math.sqrt(num_pixels)
    sqrt_max = int(math.ceil(sqrt))

    if square is True:
        return sqrt_max, sqrt_max

    if input_dimensions is not None and len(input_dimensions) >= 1:
        if input_dimensions[0] is not None:
            # the width is specified but the height is not
            if num_pixels % input_dimensions[0] == 0:
                return input_dimensions[0], num_pixels // input_dimensions[0]
            else:
                return input_dimensions[0], num_pixels // input_dimensions[0] + 1
        else:
            # the height is specified but the width is not
            if num_pixels % input_dimensions[1] == 0:
                return num_pixels // input_dimensions[1], input_dimensions[1]
            else:
                return num_pixels // input_dimensions[1] + 1, input_dimensions[1]

    best_dimensions = None
    best_extra_bytes = None
    for i in range(int(sqrt_max), 0, -1):
        is_perfect = num_pixels % i == 0
        if is_perfect:
            dimensions = (i, num_pixels // i)
        else:
            dimensions = (i, num_pixels // i + 1)
        extra_bytes = dimensions[0] * dimensions[1] * 3 - num_bytes
        if dimensions[0] * dimensions[1] >= num_pixels and (best_dimensions is None or extra_bytes < best_extra_bytes):
            best_dimensions = dimensions
            best_extra_bytes = extra_bytes
        if is_perfect:
            break
    if best_extra_bytes > 0:
        if verbose is True:
            sys.stderr.write("Could not find PNG dimensions that perfectly encode "
                             "%s bytes; the encoding will be tail-padded with %s zeros.\n"
                             % (num_bytes, int(best_extra_bytes)))
    return best_dimensions


def file_to_png(reader, outfile, dimensions, progress=False):
    
    dim = (int(dimensions[0]), int(dimensions[1]))
    img = Image.new('RGB', dim)
    pixels = img.load()
    row = 0
    column = -1
    while True:
        b = reader.read(3)
        if not b:
            break

        column += 1
        if column >= img.size[0]:
            column = 0
            row += 1
            if progress is True:
                percent = float(((row + 1) // dimensions[1]) * 100)
                sys.stderr.write("\r%s%s" % (round(percent, 2), "%"))

            if row >= img.size[1]:
                raise Exception("Error: row %s is greater than maximum rows in image, %s." % (row, img.size[1]))

        color = [b[0], 0, 0]
        if len(b) > 1:
            color[1] = b[1]
        if len(b) > 2:
            color[2] = b[2]

        if not row >= img.size[1]:
            pixels[column, row] = tuple(color)
    if progress is True:
        sys.stderr.write("\n")
    if outfile and sys.version_info.major >= 3 and outfile.name == '<stdout>' and hasattr(outfile, 'buffer'):
        outfile = outfile.buffer
    if outfile:
        img.save(outfile, format="PNG")
    else:
        return img


def png_to_file(infile, outfile, progress=True, verbose=False):
    #with FileReader.new(infile, file_backed=True) as reader:
    if isinstance(infile, Image.Image):
        #In this mode, a full PNG image was already provided through input
        isInputImage = True
        returnArray = bytearray()
        
    with infile as reader:
        if isInputImage:
            img = infile
        else:
            img = Image.open(reader.name)
        rgb_im = img.convert('RGB')
        #TODO: Only store the image that is needed to save RAM?

        def writeOutput(data): #Nested function to improve readability below
            if sys.version_info.major >= 3:
                if outfile:
                    outfile.write(bytes([data]))
                else:
                    returnArray.append(data)
            else:
                if outfile:
                    outfile.write(chr(data))
                else:
                    returnArray.append(data)
            
        pix_buffer = 0
        for row in range(img.size[1]):
            if progress is True:
                percent = float(((row + 1) // img.size[1]) * 100)
                sys.stderr.write("\r%s%s" % (round(percent, 2), "%"))
            for col in range(img.size[0]):
                pixel = rgb_im.getpixel((col, row))

                # Omit the null bytes created in the generation of the image file.
                # If it is a null byte, save it for later and see if there is going to be another null byte.
                # If the original file ended in null bytes, it will omit those too, but there is
                # probably no way to detect that.
                for segment in pixel:
                    if segment == 0:
                        pix_buffer += 1
                    else:
                        if pix_buffer != 0:
                            for color in range(pix_buffer):
                                # flush the cache to the file if a non-null byte was detected
                                writeOutput(0)
                                #returnArray.append(0)
                            pix_buffer = 0
                        writeOutput(segment)
                        #returnArray.append(segment)

        if progress is True:
            sys.stderr.write("\n")
        if pix_buffer != 0 and verbose:
            length = pix_buffer
            if length == 1:
                sys.stderr.write("Omitting %s zero from end of file\n" % pix_buffer)
            else:  # Why not...
                sys.stderr.write("Omitting %s zeroes from end of file\n" % pix_buffer)
        
        if not outfile:
            #return bytearray(str(returnArray,'char'), 'char')
            return bytes(returnArray) #.decode(encoding='UTF-8')



def encode(infile, outfile=None, square=False, width=None, height=None, progress=False, verbose=False):
    if sys.version_info.major >= 3:
        file_mode = 'wb'
        read_mode = 'rb'
    else:
        file_mode = 'w'
        read_mode = 'r'
        
    if isinstance(infile, str):
        infile = open(infile, read_mode)
    if isinstance(outfile, str):
        outfile = open(outfile, file_mode)
        
    dims = None
    if width is not None or height is not None:
        dims = (width, height)
    #Both functions need to use the same file reader for best results.
    reader = FileReader.new(infile)
    calc_dimensions = choose_file_dimensions(reader, dims, square=square,verbose=verbose)
    return file_to_png(reader, outfile, calc_dimensions, progress=progress)




def decode(infile, outfile=None, progress=False, verbose=False):
    if sys.version_info.major >= 3:
        file_mode = 'wb'
        read_mode = 'rb'
    else:
        file_mode = 'w'
        read_mode = 'r'
        
    if isinstance(infile, str):
        infile = open(infile, read_mode)
    if isinstance(outfile, str):
        outfile = open(outfile, file_mode)
    
    #if not isinstance(infile, Image.Image) and not hasattr(infile, "name"):
    #    print("noarggggg")
    reader = None
    if not isinstance(infile, Image.Image): #Don't need a reader because
        #a full image is already passed in
        reader = FileReader.new(infile, file_backed=True)
    else:
        reader = infile
        
    return png_to_file(reader, outfile, progress=progress, verbose=verbose)


