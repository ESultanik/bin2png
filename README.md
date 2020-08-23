bin2png
=======

A simple cross-platform script for encoding any binary file into a lossless PNG.  Each pixel of the output image encodes three bytes of the input file: The first byte is encoded in the red channel, the second byte in the green channel, and the third byte in the blue channel.  All files will be tail-padded with zeros so that they have a byte count that is a multiple of three.  The dimensions of the output image are automatically calculated such that they are as close to a multiple of three as possible.  If there are multiple dimensions that require minimal padding, the one that is closest to square is chosen.  The width and height of the output image can also be optionally overridden.

On Windows, this is another solution: https://github.com/leeroybrun/Bin2PNG

## Usage

```shell
$ python3 bin2png.py file_to_encode -o output.png

$ python3 bin2png.py -d output.png | diff - file_to_encode -s
Files - and file_to_encode are identical
```

Additional instructions are availble by running with the `-h` option.

## Author

Evan A. Sultanik, Ph.D.<br />
http://www.sultanik.com/<br />
http://www.digitaloperatives.com/

--------------------------------------------------
zenarcher007's fork:
On this fork of bin2png from Evan A. Sultanik, I made some major changes to the script
• Manually converted it to work with Python 3
• Added a -v --verbose option to only display extra information when that flag is specified
    (I changed the previous flag for height to -l)
• Added a progress percentage display
    (Specify the --no-progress option to prevent displaying the progress)
• Decoding an image to a file now cuts off null bytes from the end that may be created when generating an image
• Added a -s --square flag to only generate square images
