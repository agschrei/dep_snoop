""" module provides definition of the Package format
and helpers that build an instance of Package """

from json import JSONEncoder
from packageurl import PackageURL
import purl_extractor


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
        return pkg


class PackageEncoder(JSONEncoder):
    """Custom JSONEncoder for Package Type"""

    def default(self, package):  # pylint: disable=arguments-differ
        return {
            k: v for k, v in package.__dict__.items() if v is not None and len(v) > 0
        }
