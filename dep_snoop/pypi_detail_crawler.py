""" this module handles crawling details from pypi.org """
import logging
import requests
from rich.logging import RichHandler

URL_FORMAT = "https://pypi.org/pypi/{}/{}/json"

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


def get_json_from_project_page(package):
    """get detailed JSON from pypi.org"""
    if not package:
        return None
    request_url = URL_FORMAT.format(package.name, package.version)
    try:
        req = requests.get(request_url, verify=True)
        log.info(
            f"GET {request_url} content-length : {req.headers.get('content-length')}"
        )

        if not "application/json" in req.headers["content-type"]:
            return req.content

        return req.json()
    except ConnectionError:
        return None
