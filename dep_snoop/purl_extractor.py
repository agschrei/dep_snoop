""" module that provides extraction of purl-spec URL from packages """

import importlib.metadata as meta
from packageurl import PackageURL


def get_purl_from_package_name(dist_name):
    """ extract purl-spec compliant URL from package name using metadata """
    if not dist_name:
        return None
    meta_dict = meta.metadata(dist_name)
    return get_purl_from_meta_dict(meta_dict)


def get_purl_from_meta_dict(meta_dict):
    """ extract purl-spec compliant URL from package metadata dictionary """
    if not meta_dict:
        return None
    return PackageURL(
        "pypi", None, meta_dict["Name"], meta_dict["Version"], None, None
    ).to_string()
