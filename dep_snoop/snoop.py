""" main entrypoint for snoop """
from datetime import datetime
from rich.console import Console
from rich.table import Table
from dist_util import get_installed_packages


def main():
    """ main entrypoint, more to come soon """
    console = Console()
    packages = get_installed_packages()
    table = get_table_from_packages(packages)

    console.print("\n")  # newline to give it some spacing
    console.print(table, justify="left")


def get_table_from_packages(packages):
    """ returns a rich.Table built from the packages """
    table = Table(title="pypi packages in your project")

    table.add_column("[bold cyan]purl", style="bold cyan")
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("License")
    table.add_column("Release Date", justify="left")
    table.add_column("[b]sdist[/b] Size", justify="right")

    packages = sorted(packages, key=lambda package: package.name.lower())

    for package in packages:

        sdist_info = package.get_sdist_info()
        upload_time = datetime.fromisoformat(sdist_info.get("upload_time"))
        days_passed = (datetime.now() - upload_time).days
        padding = (4-len(str(days_passed)))*" "
        dist_size = round(sdist_info["size"] / 1024)
        if dist_size > 1024:
            dist_size = str(round(dist_size / 1024)) + " MiB"
        else:
            dist_size = str(dist_size) + " KiB"

        dnr_format = ""
        if "GPL" in package.license:
            dnr_format = "[bold red]"

        table.add_row(
            package.package_url,
            package.name,
            package.version,
            dnr_format + package.license,
            upload_time.strftime("%Y-%m-%d") + f"  | {padding}{days_passed}d ago",
            dist_size,
        )
    return table


if __name__ == "__main__":
    main()
