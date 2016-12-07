#!/usr/bin/python3

import os
import subprocess


for name in os.listdir('.'):
	if name.endswith('.graph'):
		subprocess.call('../../visualize/visualize_chaco.py %s --save pdf --no-show' % name, shell=True)
		subprocess.call('../../visualize/visualize_chaco.py %s --save svg --no-show' % name, shell=True)
