#!/usr/bin/env python2

from PIL import Image

 def get_length(stream):
    """Gets the number of bytes in the stream."""
    old_position = stream.tell()
    stream.seek(0)
    length = 0
    while True:
        r = stream.read(1024)
        if not r:
            break
        length += len(r)
    stream.seek(old_position)
    return length

def choose_file_dimensions(infile):
    length = get_length(infile)

def file_to_png(infile, outfile):
    img = Image.new('RGB', (1024, 1024))
    pixels = img.load()
    row = 0
    column = 0
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
    import sys
    
    parser = argparse.ArgumentParser(description="A simple cross-platform script for encoding any binary file into a lossless PNG.", prog="bin2png")

    parser.add_argument('file', type=argparse.FileType('r'), help="the file to process")
    parser.add_argument("-o", "--outfile", type=argparse.FileType('w'), default=sys.stdout, help="the output file (default to stdout)")

    args = parser.parse_args()

    file_to_png(args.file, args.outfile)
