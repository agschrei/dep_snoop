""" module provides definition of the Package format
and helpers that build an instance of Package """

import logging
from json import JSONEncoder
from packageurl import PackageURL
import purl_extractor
from pypi_detail_crawler import get_json_from_project_page

log = logging.getLogger("rich")


class Package:
    """Simple representation of a python package"""

    def __init__(  # pylint: disable=too-many-arguments,dangerous-default-value
        self,
        name,
        version,
        homepage=None,
        license_name="UNKNOWN",
        requirements=[],
        source_url=None,
        package_url=None,
    ):
        self.name = name
        self.version = version
        self.homepage = homepage
        self.license = license_name
        self.requirements = requirements
        self.source_url = source_url
        if not package_url:
            self.package_url = PackageURL(
                "pypi", None, name, version, None, None
            ).to_string()
        else:
            self.package_url = package_url
        self.detail_info = DetailInformation(get_json_from_project_page(self))

    def get_sdist_info(self):
        """ return sdist release info for package version, if any """
        return self.detail_info.get_sdist_release_info(self.version)

    def get_bdist_info(self):
        """ return bdist release info for package version, if any """
        return self.detail_info.get_bdist_release_info(self.version)

    def get_release_info(self):
        """ return info on all dist releases for package version """
        return self.detail_info.get_release_info(self.version)

    def __str__(self):
        return "{}\t{} {}\t\t\tLicense: {}".format(
            self.package_url, self.name, self.version, self.license
        )

    @classmethod
    def from_metadata(cls, meta):
        """ generate a valid Package from an importlib.metadata.metadata object """
        return Package(
            name=meta["Name"],
            version=meta["Version"],
            homepage=meta["Home-page"],
            license_name=meta["License"],
            source_url=meta["Project-URL"],
            package_url=purl_extractor.get_purl_from_meta_dict(meta),
        )

    @classmethod
    def from_dist(cls, dist):
        """ generate a valid Package from an importlib.metadata.Distribution object """
        pkg = Package.from_metadata(dist.metadata)
        pkg.requirements = dist.requires
        print(dist.requires)
        return pkg


class PackageEncoder(JSONEncoder):
    """Custom JSONEncoder for Package Type"""

    def default(self, package):  # pylint: disable=arguments-differ
        return {
            k: v for k, v in package.__dict__.items() if v is not None and len(v) > 0
        }


class DetailInformation:
    def __init__(self, detail_json):
        self._detail = detail_json

    def get_release_info(self, version):
        """ extract release info for requested version from details if any """
        try:
            return self._detail["releases"][version]
        except KeyError as key_error:
            log.warning(key_error)
            return []

    def get_sdist_release_info(self, version):
        """ extract sdist release info from details if any """
        for dist in self.get_release_info(version):
            if "sdist" in dist["packagetype"]:
                return dist
        return {}

    def get_bdist_release_info(self, version):
        """ extract bdist release info from details if any """
        for dist in self.get_release_info(version):
            if "bdist" in dist["packagetype"]:
                return dist
        return {}
