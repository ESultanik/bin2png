#!/usr/bin/env/python3

import sys
import argparse
from bin2png import Encoder

#Helper functions for bin2png.
#These can be used when bin2png is imported as a module
#using "from bin2png import Encoder"
#From there you can use Encoder.encode(...)
#and Encoder.decode(...)

def main(argv=None):
    parser = argparse.ArgumentParser(description="A simple cross-platform script for encoding any binary file into a "
        "lossless PNG.", prog="bin2png")
    
    if sys.version_info.major >= 3:
        read_mode = 'rb'
        write_mode = 'wb'
        out_default = sys.stdout.buffer
    else:
        read_mode = 'r'
        write_mode = 'w'
        out_default = sys.stdout
        
    parser.add_argument('file', type=argparse.FileType(read_mode), default=sys.stdin, nargs='?',
                        help="the file to encode as a PNG (defaults to '-', which is stdin)")
    parser.add_argument("-o", "--outfile", type=argparse.FileType(write_mode), default=out_default,
                        help="the output file (defaults to '-', which is stdout)")
    parser.add_argument("-d", "--decode", action="store_true", default=False,
                        help="decodes the input PNG back to a file")
    parser.add_argument("-w", "--width", type=int, default=None,
                        help="constrain the output PNG to a specific width")
    parser.add_argument("-l", "--height", type=int, default=None,
                        help="constrain the output PNG to a specific height")
    parser.add_argument("-s", "--square", action="store_true", default=False, help="generate only square images")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="enable debugging messages")
    parser.add_argument("-p", "--progress", action="store_true", default=False, help="display percent progress")

    if argv is None:
        argv = sys.argv

    #Remove the first argument (the name of this file itsself)
    argv.pop(0)
    args = parser.parse_args(argv)

    if args.decode:
        Encoder.decode(reader, args.outfile, progress=args.progress, verbose=args.verbose)
    else:
        Encoder.encode(args.file, outfile=args.outfile, square=args.square, width=args.width, height=args.height, progress=args.progress, verbose=args.verbose)


if __name__ == "__main__":
    main()




