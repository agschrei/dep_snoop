""" utility to extract information about installed packages from active environment """

from importlib.metadata import Distribution
from pathos.multiprocessing import ProcessingPool as Pool
from rich.progress import track
from package import Package
import logging

log = logging.getLogger("rich")


def get_installed_packages():
    """ get a list of all packages currently installed in the active environment """
    packages = []

    pool = Pool(4)

    # for dist in track(
    #     list(Distribution.discover()), description="[cyan]Grabbing dependency info"
    # ):
    #     packages.append(Package.from_dist(dist))

    dists = list(Distribution.discover())
    dists_num = len(dists)

    log.info("[bold]Found a total of {} distributions".format(
        dists_num), extra={"markup": True})

    for package_enum in enumerate(pool.imap(Package.from_dist, dists), start=1):
        package = package_enum[1]
        log.info("{0}/{1}: processed [bold cyan]{2} {3}[/bold cyan]"
                 .format(package_enum[0], dists_num, package.name,
                         package.version), extra={"markup": True})
        packages.append(package)

    return packages
