import pkg_resources

with open(pkg_resources.resource_filename('wc_rules', 'VERSION'), 'r') as file:
    __version__ = file.read().strip()
# :obj:`str`: version