import unittest

from dep_snoop.requirements_parser import Version, VersionBuilder, VersionComparator, Requirement


class TestVersion(unittest.TestCase):
    def test_valid_release_only(self):
        version = Version("1.2.3")
        self.assertEqual(version.tokens.release, "1.2.3")

    def test_valid_prerelease(self):
        version = Version("1.2.3rc3")
        self.assertEqual(version.tokens.release, "1.2.3")
        self.assertEqual(version.tokens.prerelease, "rc3")

    def test_invalid_prerelease(self):
        with self.assertRaises(ValueError):
            Version("1.2.3abc3")

    def test_invalid_empty(self):
        with self.assertRaises(ValueError):
            Version("")

    def test_invalid_epoch_only(self):
        with self.assertRaises(ValueError):
            Version("1!")

    def test_invalid_dev_only(self):
        with self.assertRaises(ValueError):
            Version("dev3")

    def test_idempotence(self):
        version = Version("1.2.3.4")
        self.assertEqual(version, version)

    def test_less_than(self):
        version_a = Version("1.2")
        version_b = Version("1.3")
        self.assertLess(version_a, version_b)

    def test_release_greater_than_rc(self):
        version_a = Version("1.2")
        version_b = Version("1.2rc1")
        self.assertGreater(version_a, version_b)


class TestVersionBuilder(unittest.TestCase):
    def test_none_if_illegal(self):
        self.assertIsNone(VersionBuilder.build_from_string(".post0"))

    def test_increment(self):
        version = VersionBuilder.build_from_string("3!1.2.3")
        incremented_version = VersionBuilder.increment_least_significant(
            version)
        self.assertEqual(str(incremented_version), "3!1.2.4")

    def test_strip_least_significant(self):
        rep = "3!1.2.3a2.dev4"
        version = VersionBuilder.build_from_string(rep)
        version_stripped = VersionBuilder.strip_least_significant(version)
        self.assertIsNone(version_stripped.tokens.dev)
        self.assertEqual(str(version_stripped), rep[:-5:])

    def test_strip_least_significant_release(self):
        rep = "1.2.3"
        version = VersionBuilder.build_from_string(rep)
        version_stripped = VersionBuilder.strip_least_significant(version)
        self.assertIsNone(version_stripped.tokens.dev)
        self.assertEqual(str(version_stripped), "1.2")


class TestVersionComparator(unittest.TestCase):
    def test_successful_compat(self):
        version_a = Version("1.2.4.5.6.7")
        version_b = Version("1.1")
        compare = VersionComparator.COMPATIBLE
        self.assertTrue(compare(version_a, version_b))


class TestRequirement(unittest.TestCase):
    def test_predicate_check(self):
        req = Requirement("urllib3 (!=1.25.1,<1.26,!=1.25.0,>=1.21.1)")
        self.assertTrue(req.check_compatible(Version("1.25.2")))
        self.assertFalse(req.check_compatible(Version("1.26")))


if __name__ == "__main__":
    unittest.main()
