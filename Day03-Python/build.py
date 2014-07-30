#!/usr/bin/env python

import glob
import subprocess

notebooks = glob.glob('../../master/Day03-Python/*.ipynb')
for notebook in notebooks:
  subprocess.Popen('ipython nbconvert {}'.format(notebook), shell=True).wait()
