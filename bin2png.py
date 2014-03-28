#!/usr/bin/env python2

from PIL import Image
import math
import StringIO
import os
import sys

class FileReader(object):
    def __init__(self, path):
        if isinstance(path, file):
            if path.name == "<stdin>":
                infile = sys.stdin.read()
                self.length = len(infile)
                self.file = StringIO.StringIO(infile)
            else:
                self.length = os.path.getsize(path.name)
                self.file = path
        else:
            self.length = os.path.getsize(path)
            self.file = open(path)
    def __len__(self):
        return self.length
    def __getattr__(self, attr):
        return getattr(self.file, attr)
    def __iter__(self):
        return iter(self.file)

def choose_file_dimensions(infile):
    if not isinstance(infile, FileReader):
        infile = FileReader(infile)
    num_bytes = len(infile)
    num_pixels = int(math.ceil(float(num_bytes) / 3.0))
    sqrt = math.sqrt(num_pixels)
    sqrt_max = int(math.ceil(sqrt))
    dimensions = (sqrt_max, sqrt_max)
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
        sys.stderr.write("Could not find PNG dimensions that perfectly encode %s bytes; the encoding will be tail-padded with %s zeros.\n" % (num_bytes, best_extra_bytes))
    return best_dimensions

def file_to_png(infile, outfile, dimensions = None):
    if dimensions is None:
        dimensions = choose_file_dimensions(infile)
    img = Image.new('RGB', dimensions)
    pixels = img.load()
    row = 0
    column = -1
    while True:
        b = infile.read(3)
        if not b:
            break

        column += 1
        if column >= img.size[0]:
            column = 0
            row += 1
            if row >= img.size[1]:
                raise Exception("TODO: Write exception!")
                
        color = [ord(b[0]), 0, 0]
        if len(b) > 1:
            color[1] = ord(b[1])
        if len(b) > 2:
            color[2] = ord(b[2])

        pixels[column,row] = tuple(color)

    img.save(outfile, format="PNG")

def png_to_file(infile, outfile):
    img = Image.open(infile)
    rgb_im = img.convert('RGB')
    for row in range(img.size[1]):
        for col in range(img.size[0]):
            r, g, b = rgb_im.getpixel((col, row))
            outfile.write(chr(r))
            outfile.write(chr(g))
            outfile.write(chr(b))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A simple cross-platform script for encoding any binary file into a lossless PNG.", prog="bin2png")

    parser.add_argument('file', type=argparse.FileType('r'), default=sys.stdin, help="the file to encode as a PNG (defaults to '-', which is stdin)")
    parser.add_argument("-o", "--outfile", type=argparse.FileType('w'), default=sys.stdout, help="the output file (defaults to '-', which is stdout)")
    parser.add_argument("-d", "--decode", action="store_true", default=False, help="decodes the input PNG back to a file")

    args = parser.parse_args()

    if args.decode:
        png_to_file(args.file, args.outfile)
    else:
        file_to_png(args.file, args.outfile)
