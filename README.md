bin2png
=======

A simple cross-platform script for encoding any binary file into a lossless PNG.

On Windows, this is another solution: https://github.com/leeroybrun/Bin2PNG

## Usage

```shell
$ python bin2png.py file_to_encode -o output.png

$ python bin2png.py output.png | diff - file_to_encode
Files - and file_to_encode are identical
```

Note that all files will be tail-padded with zeros so that they have a byte count that is a multiple of three.

Additional instructions are availble by running with the `-h` option.

## Author

Evan A. Sultanik, Ph.D.<br />
http://www.sultanik.com/<br />
http://www.digitaloperatives.com/
