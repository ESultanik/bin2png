bin2png
=======

A simple cross-platform script for encoding any binary file into a lossless PNG.  Each pixel of the output image encodes three bytes of the input file: The first byte is encoded in the red channel, the second byte in the green channel, and the third byte in the blue channel.  All files will be tail-padded with zeros so that they have a byte count that is a multiple of three.  The dimensions of the output image are automatically calculated such that they are as close to a multiple of three as possible.  If there are multiple dimensions that require minimal padding, the one that is closest to square is chosen.  The width and height of the output image can also be optionally overridden.

On Windows, this is another solution: https://github.com/leeroybrun/Bin2PNG

## Usage

```shell
$ python bin2png.py file_to_encode -o output.png

$ python bin2png.py -d output.png | diff - file_to_encode -s
Files - and file_to_encode are identical
```

Additional instructions are availble by running with the `-h` option.

## Author

Evan A. Sultanik, Ph.D.<br />
http://www.sultanik.com/<br />
http://www.digitaloperatives.com/
