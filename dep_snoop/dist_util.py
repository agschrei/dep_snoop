""" utility to extract information about installed packages from active environment """

from importlib.metadata import Distribution
from package import Package


def get_installed_packages():
    """ get a list of all packages currently installed in the active environment """
    packages = [Package.from_dist(dist) for dist in Distribution.discover()]
    return packages
