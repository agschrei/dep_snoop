""" main entrypoint for snoop """

from rich.console import Console
from rich.table import Table
from dist_util import get_installed_packages


def main():
    """ main entrypoint, more to come soon """
    packages = get_installed_packages()
    table = get_table_from_packages(packages)

    console = Console()
    console.print(table, justify="center")


def get_table_from_packages(packages):
    """ returns a rich.Table built from the packages """
    table = Table(title="pypi packages in your project")

    table.add_column("purl", style="bold cyan")
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("License")

    for package in packages:
        table.add_row(
            package.package_url, package.name, package.version, package.license
        )
    return table


if __name__ == "__main__":
    main()
