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
        clauses = version_requirements.split(",")
        return lambda x: x

    def _extract_predicate_helper(self, predicate_string: str):
        pass

req = Requirement("urllib3 (!=1.25.1,<1.26,!=1.25.0,>=1.21.1)")

class VersionString:
    """ builds a hierarchical representation of a version from its string representation
        we assume compliance with https://www.python.org/dev/peps/pep-0440/#version-scheme """
    def __init__(self, version: str):
        regexp = r"([0-9]+!)?([0-9]+)((?:\.[0-9]+)*)((?:a|b|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?"

