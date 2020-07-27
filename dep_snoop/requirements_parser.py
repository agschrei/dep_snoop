from enum import Enum
import functools
import logging
import re
from typing import Callable
from collections import namedtuple

VersionTokens = namedtuple("VersionTokens", ["epoch", "release", "prerelease", "post", "dev"])

log = logging.getLogger("rich")

def cleanNoneFromDict(original_dict):
    return {k: v for k,v in original_dict.items() if v is not None}

@functools.total_ordering
class Version:
    """ builds a hierarchical representation of a version from its string representation
        we assume compliance with https://www.python.org/dev/peps/pep-0440/#version-scheme 
        This raises a ValueError if instantiated with an illegal verstion string"""
    def __init__(self, version: str):
        self.raw = version
        regexp = re.compile(r"(?P<epoch>[0-9]+!)?(?P<release>([0-9]+)((?:\.[0-9]+)*))"+
        r"(?P<prerelease>(?:a|b|rc)[0-9]+)?(?P<post>\.post[0-9]+)?(?P<dev>\.dev[0-9]+)?")
        matches = regexp.match(version)
        if matches!=None and matches.group() is version.strip():
            groups = matches.groupdict()
            self.tokens = VersionTokens(groups.get("epoch"), groups.get("release"), groups.get("prerelease"), \
            groups.get("post"), groups.get("dev"))
        else:
            raise ValueError("The string you passed is not in compliance with PEP440!")
    
    def __lt__(self, other):
        last = True
        other_dict = other.tokens._asdict()
        for key, val in self.tokens._asdict().items():
            if not last:
                return False
            if key in ["prerelease", "post", "dev"]:
                last = last and (other_dict.get(key) is None or (val is not None and val <= other_dict[key]))
            else:
                last = last and (val is None or (other_dict.get(key) is not None and val <= other_dict[key]))

        return last and not self == other

    def __eq__(self, other):
        return self.tokens.epoch == other.tokens.epoch and self.tokens.release == other.tokens.release and \
        self.tokens.prerelease == other.tokens.prerelease and self.tokens.post == other.tokens.post and \
        self.tokens.dev == other.tokens.dev

    @classmethod
    def __less_than_or_not_present(cls, a, b):
        return a is not None and a < b or b is None

    def __str__(self):
        representation = ""
        if self.tokens.epoch is not None:
            representation += self.tokens.epoch
        if self.tokens.release is not None:
            representation += self.tokens.release
        if self.tokens.prerelease is not None:
            representation += self.tokens.prerelease
        if self.tokens.post is not None:
            representation += self.tokens.post
        if self.tokens.dev is not None:
            representation += self.tokens.dev
        return representation

class VersionBuilder:
    @classmethod
    def build_from_string(cls, version: str) -> Version:
        try:
            return Version(version)
        except ValueError as v_e:
            log.warn("{0} is not a valid version string!".format(version))
    
    @classmethod
    def strip_least_significant(cls, version: Version) -> Version:
        """returns a new Version with the least significant token removed"""
        #remove null elements and slice off the least significant token
        filtered = list(filter(lambda item: item[1] is not None, version.tokens._asdict().items()))
        last = filtered.pop()
        #if least significant token is release, strip least significant portion of that
        if last[0] == "release":
            stripped_release = (last[0], last[1].rsplit(".", 1)[0])
            filtered.append(stripped_release)
        return cls.build_from_string("".join(map(lambda item: item[1], filtered)))

    @classmethod
    def __build_with_filtered_tokens(cls, version: Version,
    filter_operation: Callable, pop_last=False) -> Version:
        filtered_tokens = list(map(lambda x: x[1], filter(filter_operation,
        version.tokens._asdict().items())))
        if pop_last:
            filtered_tokens.pop()
        return Version("".join(filtered_tokens))

    @classmethod
    def increment_least_significant(cls, version: Version) -> Version:
        """returns a new Version with the least significant token incremented"""
        token_list = list(filter(lambda token: token is not None,
        version.tokens._asdict().values()))
        token_list.append(VersionBuilder._increment(token_list.pop()))
        return Version("".join(token_list))

    @classmethod
    def _increment(cls, token: str)->str:
        regexp = re.compile(r"[a-zA-Z]{0,4}((?:\.?(?:[0-9]+))+)$")
        match = regexp.match(token)
        if match is None:
            return None
        numerals = match.group(1).split(".")
        numerals.append(str(int(numerals.pop())+1))
        return ".".join(numerals)

class VersionComparator(Enum):
    """TODO: Refactor to get rid of enum and only use LUT"""
    @classmethod
    def get(cls, group_name: str):
        func = {
            "match": VersionComparator.MATCH, 
            "exclude": VersionComparator.EXCLUDE, 
            "lt": VersionComparator.LT, 
            "gt": VersionComparator.GT, 
            "lte": VersionComparator.LTE, 
            "gte": VersionComparator.GTE, 
            "comp": VersionComparator.COMPATIBLE,
            "eq": VersionComparator.EQUALS
        }.get(group_name)
        return func

    MATCH = lambda x, y: x == y
    EXCLUDE = lambda x, y: x != y
    LTE = lambda x, y: x <= y
    GTE = lambda x, y: x >= y
    LT = lambda x, y: x < y
    GT = lambda x, y: x > y
    EQUALS = lambda x, y: x.raw == y.raw
    COMPATIBLE = lambda x, y: VersionComparator.GTE(x, y) and VersionComparator.LT(x,
    VersionBuilder.increment_least_significant(VersionBuilder.strip_least_significant(y)))

class Requirement:
    def __init__(self, requirement_string : str):
        if not requirement_string:
            raise ValueError("provided empty requirements string!")
        tokens = requirement_string.split()
        self.name = tokens.pop(0)
        self.check_compatible: Callable = self._build_version_check(tokens)
        self.raw_string = requirement_string

    def _build_version_check(self, version_requirements: list) -> Callable[[str], bool]:
        """here we parse the requirements and generate predicate lambdas for each of them
        and combine them into one lambda that checks whether all of them are satisfied"""
        version_requirements = re.findall(r'\((.*?) *\)', "".join(version_requirements))
        predicates = []
        for requirements_group in version_requirements:
            for version_requirement in requirements_group.split(","):
                try:
                    predicates.append(self._extract_predicate_helper(version_requirement))
                except ValueError as v_e:
                    log.warn(v_e.args)
        return lambda version: all(map(lambda x: x(version), predicates))

    def _extract_predicate_helper(self, predicate_string: str) -> Callable[[str], bool]:
        """returns a lambda that checks whether a specific version satisfies the requirement"""
        regexp = re.compile(r"(?:(?P<comp>~=)|(?P<match>==)|(?P<exclude>!=)|" +\
            r"(?P<lte><=)|(?P<gte>>=)|(?P<lt><)|(?P<gt>>)|(?P<eq>===))")
        matches = regexp.match(predicate_string)
        if matches is None:
            raise ValueError(predicate_string + " is not a valid requirement predicate!")
        for match in filter(lambda item: item[1] is not None, matches.groupdict().items()):
            version_string = predicate_string[len(match[1])::]
            #this workaround is actually necessary for packages that don't comply with PEP440
            if ".*" in version_string:
                version_string = version_string.replace(".*", "")
                if match[0] == "eq":
                    match = ("gte", match[1])
                    log.info(f"Truncated {predicate_string} to {'>='+version_string}")
                    
            version = VersionBuilder.build_from_string(version_string)
            predicate = lambda x, y=version: VersionComparator.get(match[0])(x, y)
            return predicate
