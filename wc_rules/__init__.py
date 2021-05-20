"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

import pkg_resources

with open(pkg_resources.resource_filename('wc_rules', 'VERSION'), 'r') as file:
	__version__ = file.read().strip()

from ._version import __version__

