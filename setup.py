from setuptools import setup

setup(
    name='bin2png',
    description='A simple cross-platform script for encoding any binary file into a lossless PNG',
    url='https://github.com/ESultanik/bin2png',
    author='Evan Sultanik',
    version='2.0',
    py_modules=['bin2png'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
    install_requires=[
        "Pillow"
    ],
    entry_points={
        'console_scripts': [
            'bin2png = bin2png:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ]
)
