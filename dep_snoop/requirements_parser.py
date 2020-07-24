import functools
import re
from typing import Callable

class Requirement:
    def __init__(self, requirement_string : str):
        if not requirement_string:
            raise ValueError("provided empty requirements string!")
        tokens = requirement_string.split()
        self.name = tokens.pop(0)
        self.check_compatible: Callable = self._build_version_check(tokens)
        self.raw_string = requirement_string
        

    def _build_version_check(self, version_requirements: list):
        version_requirements = re.findall(r'\((.*?) *\)', "".join(version_requirements))
        for requirements_group in version_requirements:
            for version_requirement in requirements_group.split(","):
                print(version_requirement + "\n")

    def _extract_predicate_helper(self, predicate_string: str):
        pass

req = Requirement("urllib3 (!=1.25.1,<1.26,!=1.25.0,>=1.21.1)")


@functools.total_ordering
class VersionString:
    """ builds a hierarchical representation of a version from its string representation
        we assume compliance with https://www.python.org/dev/peps/pep-0440/#version-scheme 
        This raises a ValueError if instantiated with an illegal verstion string"""
    def __init__(self, version: str):
        regexp = re.compile(r"(?P<epoch>[0-9]+!)?(?P<release>([0-9]+)((?:\.[0-9]+)*))"+
        r"(?P<prerelease>(?:a|b|rc)[0-9]+)?(?P<post>\.post[0-9]+)?(?P<dev>\.dev[0-9]+)?")
        matches = regexp.match(version)
        if matches!=None:
            groups = matches.groupdict()
            self.epoch = groups.get("epoch")
            self.release = groups.get("release")
            self.prerelease = groups.get("prerelease")
            self.post = groups.get("post")
            self.dev = groups.get("dev")
            print(groups)
        else:
            raise ValueError("The string you passed is not in compliance with PEP440!")
    
    def __lt__(self, other):
        if not self.epoch < other.epoch:
            if not self.release < other.release:
                if other.prerelease == None or self.prerelease != None and not self.prerelease < other.prerelease:
                    if not self.post < other.post:
                        if not self.dev < other.dev:
                            return False
        return True

    def __eq__(self, other):
        return self.epoch == other.epoch and self.release == other.release and \
        self.prerelease == other.prerelease and self.post == other.post and \
        self.dev == other.dev

class VersionStringBuilder:
    @classmethod
    def buildFromString(cls, version: str) -> VersionString:
        try:
            return VersionString(version)
        except ValueError:
            return None

print(VersionStringBuilder.buildFromString("1!2.3.4rc5.post5.dev1"))
a = VersionStringBuilder.buildFromString("1!2.3.4rc5.post5.dev1")
b = VersionStringBuilder.buildFromString("1!2.3.post5.dev0")
print(a < b)
