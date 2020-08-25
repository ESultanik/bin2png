#!/usr/bin/env python3

import io
import math
import os
import sys

from PIL import Image


class FileReader(object):
    def __init__(self, path):
        if 'file' in locals() and isinstance(path, file):
            if path.name == "<stdin>":
                infile = sys.stdin.buffer.read()
                self.length = len(infile)
                self.file = io.StringIO(infile)
            else:
                self.length = os.path.getsize(path.name)
                self.file = path
        else:
            str_path = path.name
            self.length = os.path.getsize(str_path)
            self.file = open(str_path)

    def __len__(self):
        return self.length

    def __getattr__(self, attr):
        return getattr(self.file, attr)

    def __iter__(self):
        return iter(self.file)


def choose_file_dimensions(infile, input_dimensions=None):
    if input_dimensions is not None and len(input_dimensions) >= 2 and input_dimensions[0] is not None \
            and input_dimensions[1] is not None:
        # the dimensions were already fully specified
        return input_dimensions
    if not isinstance(infile, FileReader):
        infile = FileReader(infile)
    num_bytes = len(infile)
    num_pixels = int(math.ceil(float(num_bytes) / 3.0))
    sqrt = math.sqrt(num_pixels)
    sqrt_max = int(math.ceil(sqrt))
    
    if args.square is True:
        return sqrt_max, sqrt_max
   
    if input_dimensions is not None and len(input_dimensions) >= 1:
        if input_dimensions[0] is not None:
            # the width is specified but the height is not
            if num_pixels % input_dimensions[0] == 0:
                return input_dimensions[0], num_pixels / input_dimensions[0]
            else:
                return input_dimensions[0], num_pixels / input_dimensions[0] + 1
        else:
            # the height is specified but the width is not
            if num_pixels % input_dimensions[1] == 0:
                return num_pixels / input_dimensions[1], input_dimensions[1]
            else:
                return num_pixels / input_dimensions[1] + 1, input_dimensions[1]

    best_dimensions = None
    best_extra_bytes = None
    for i in range(int(sqrt_max), 0, -1):
        is_perfect = num_pixels % i == 0
        if is_perfect:
            dimensions = (i, num_pixels / i)
        else:
            dimensions = (i, num_pixels / i + 1)
        extra_bytes = dimensions[0] * dimensions[1] * 3 - num_bytes
        if dimensions[0]*dimensions[1] >= num_pixels and (best_dimensions is None or extra_bytes < best_extra_bytes):
            best_dimensions = dimensions
            best_extra_bytes = extra_bytes
        if is_perfect:
            break
    if best_extra_bytes > 0:
        # TODO: If verbose mode is on...
        if args.verbose is True:
            sys.stderr.write("Could not find PNG dimensions that perfectly encode "
                             "%s bytes; the encoding will be tail-padded with %s zeros.\n"
                             % (num_bytes, int(best_extra_bytes)))
    return best_dimensions


def file_to_png(infile, outfile, dimensions=None):
    dimensions = choose_file_dimensions(infile, dimensions)
    dim = (int(dimensions[0]),int(dimensions[1]))
    img = Image.new('RGB', dim)
    pixels = img.load()
    row = 0
    column = -1
    while True:

        b = infile.buffer.read(3)
        if not b:
            break

        column += 1
        if column >= img.size[0]:
            column = 0
            row += 1
            if args.no_progress is False:
                percent = float(((row + 1) / dimensions[1]) * 100)
                sys.stderr.write("\r%s%s" % (round(percent,2),"%"))
            
            if row >= img.size[1]:
                raise Exception("Error: row %s is greater than maximum rows in image, %s." % (row, img.size[1]))

        color = [b[0], 0, 0]  # ord(b[0])
        if len(b) > 1:
            color[1] = b[1]  # ord(b[1])
        if len(b) > 2:
            color[2] = b[2]  # ord(str(b[2]))
        
        if not row >= img.size[1]:
            pixels[column, row] = tuple(color)
    if args.no_progress is False:
        sys.stderr.write("\n")
    img.save(outfile.name, format="PNG")


def png_to_file(infile, outfile):
    img = Image.open(infile.name)
    rgb_im = img.convert('RGB')

    pix_buffer = 0
    for row in range(img.size[1]):
        if args.no_progress is False:
            percent = float(((row + 1) / img.size[1]) * 100)
            sys.stderr.write("\r%s%s" % (round(percent,2),"%"))
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
                        for color in range(pix_buffer):  # flush the cache to the file if a non-null byte was detected
                            outfile.write(chr(0))
                        pix_buffer = 0
                    outfile.write(chr(segment))

    if args.no_progress is False:
        sys.stderr.write("\n")
    if pix_buffer != 0 and args.verbose is True:
        length = pix_buffer
        if length == 1:
            sys.stderr.write("Omitting %s zero from end of file\n" % pix_buffer)
        else:  # Why not...
            sys.stderr.write("Omitting %s zeroes from end of file\n" % pix_buffer)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A simple cross-platform script for encoding any binary file into a "
                                                 "lossless PNG.", prog="bin2png")

    parser.add_argument('file', type=argparse.FileType('r'), default=sys.stdin,
                        help="the file to encode as a PNG (defaults to '-', which is stdin)")
    parser.add_argument("-o", "--outfile", type=argparse.FileType('w'), default=sys.stdout,
                        help="the output file (defaults to '-', which is stdout)")
    parser.add_argument("-d", "--decode", action="store_true", default=False,
                        help="decodes the input PNG back to a file")
    parser.add_argument("-w", "--width", type=int, default=None,
                        help="constrain the output PNG to a specific width")
    parser.add_argument("-l", "--height", type=int, default=None,
                        help="constrain the output PNG to a specific height")
    parser.add_argument("-s", "--square", action="store_true", default=False, help="generate only square images")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="enable debugging messages")
    parser.add_argument("--no-progress", action="store_true", default=False, help="don't display percent progress")
    
    args = parser.parse_args()

    if args.decode:
        png_to_file(args.file, args.outfile)
    else:
        dims = None
        if args.height is not None or args.width is not None:
            dims = (args.width, args.height)
        
        file_to_png(args.file, args.outfile, dimensions=dims)
