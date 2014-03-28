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
    for i in range(int(sqrt), 1, -1):
        if num_pixels % i == 0:
            dimensions = (i, num_pixels / i)
            break
    extra_bytes = dimensions[0] * dimensions[1] * 3 - num_bytes
    if extra_bytes > 0:
        sys.stderr.write("Could not find PNG dimensions that perfectly encode %s bytes; the encoding will be tail-padded with %s zeros." % (num_bytes, extra_bytes))
    return dimensions

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

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="A simple cross-platform script for encoding any binary file into a lossless PNG.", prog="bin2png")

    parser.add_argument('file', type=argparse.FileType('r'), default=sys.stdin, help="the file to process (defaults to '-', which is stdin)")
    parser.add_argument("-o", "--outfile", type=argparse.FileType('w'), default=sys.stdout, help="the output file (defaults to '-', which is stdout)")

    args = parser.parse_args()

    file_to_png(args.file, args.outfile)
