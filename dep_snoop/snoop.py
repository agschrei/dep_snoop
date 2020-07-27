""" main entrypoint for snoop """
from datetime import datetime
import logging
import matplotlib.pyplot as plt
import networkx as nx
from rich.console import Console
from rich.table import Table
from dist_util import get_installed_packages
from requirements_parser import Version

log = logging.getLogger("rich")


def main():
    """ main entrypoint, more to come soon """
    console = Console()
    packages = get_installed_packages()
    table = get_table_from_packages(packages)

    console.print("\n")  # newline to give it some spacing
    console.print(table, justify="left")


def gather_dependencies(package, name_map):
    package.dependencies = []
    for req in package.requirements:
        try:
            dependency = name_map[req.name]
            package.dependencies.append(dependency)
            version = Version(name_map[req.name].version)
            if req.check_compatible(version):
                log.info("Requirement satisfied for {0}: {1}-{2}".format(package.name,
                                                                         dependency.name, dependency.version))
            else:
                raise KeyError
        except KeyError as k_e:
            log.warning(
                f"Requirement {req.raw_string} not satisfied for {package.name}!")
    return package


def buildGraph(packages):
    G = nx.Graph()
    for package in packages:
        G.add_node(package.name)
        G.add_edges_from(list(map(lambda dep: (package.name, dep.name), package.dependencies)))
        G.add_edge("this_package", package.name)
    plt.figure(figsize=(10,10), dpi=300)
    pos = nx.spring_layout(G, iterations=50)
    nx.draw(G, pos, with_labels=False, node_size=50, alpha=0.7, node_color="r")
    for p in pos:
        pos[p][1]+=0.1
    nx.draw_networkx_labels(G, pos)

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

    name_map = {package.name: package for package in packages}
    packages = list(map(lambda pkg: gather_dependencies(pkg, name_map), packages))
    log.info(len(packages))
    buildGraph(packages)

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
            upload_time.strftime("%Y-%m-%d") +
            f"  | {padding}{days_passed}d ago",
            dist_size,
        )
    return table


if __name__ == "__main__":
    main()
