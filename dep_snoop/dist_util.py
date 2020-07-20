""" utility to extract information about installed packages from active environment """

from importlib.metadata import Distribution
from rich.progress import track
from package import Package


def get_installed_packages():
    """ get a list of all packages currently installed in the active environment """
    packages = []
    for dist in track(
        list(Distribution.discover()), description="[cyan]Grabbing dependency info"
    ):
        packages.append(Package.from_dist(dist))

    return packages
