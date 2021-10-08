import unittest

from src import mfaimagebot


class TestMFAImageBot(unittest.TestCase):
    def test_check_batsignal(self):
        self.assertTrue(mfaimagebot.check_batsignal("!MFAImageBot test"))
        self.assertTrue(mfaimagebot.check_batsignal("!mfaimagebot test"))
        self.assertTrue(mfaimagebot.check_batsignal("!MfAiMaGeBoT test"))
        self.assertTrue(mfaimagebot.check_batsignal("!mfaib test"))
        self.assertTrue(mfaimagebot.check_batsignal("!mfa test"))
        self.assertTrue(mfaimagebot.check_batsignal("!imagebot test"))
        self.assertTrue(mfaimagebot.check_batsignal("!ibot test"))

        self.assertFalse(mfaimagebot.check_batsignal(" !MFAImageBot test"))
        self.assertFalse(mfaimagebot.check_batsignal("!Test test"))
        self.assertFalse(mfaimagebot.check_batsignal("?MFAImageBot test"))

    def test_parse_imgur_url(self):
        self.assertEqual(
            mfaimagebot.parse_imgur_url("http://imgur.com/a/cjh4E"),
            {"id": "cjh4E", "type": "album"},
        )
        self.assertEqual(
            mfaimagebot.parse_imgur_url("HtTP://imgur.COM:80/gallery/59npG"),
            {"id": "59npG", "type": "gallery"},
        )
        self.assertEqual(
            mfaimagebot.parse_imgur_url("https://i.imgur.com/altd8Ld.png"),
            {"id": "altd8Ld", "type": "image"},
        )
        self.assertEqual(
            mfaimagebot.parse_imgur_url("https://i.stack.imgur.com/ELmEk.png"),
            {"id": "ELmEk", "type": "image"},
        )

    def test_parse_imgur_url_exceptions(self):
        with self.assertRaisesRegex(ValueError, "not-imgur.com"):
            mfaimagebot.parse_imgur_url("http://not-imgur.com/altd8Ld.png")
        with self.assertRaisesRegex(ValueError, "tftp://imgur.com"):
            mfaimagebot.parse_imgur_url("tftp://imgur.com/gallery/59npG")
        with self.assertRaisesRegex(ValueError, "Blah"):
            mfaimagebot.parse_imgur_url("Blah")


if __name__ == "__main__":
    unittest.main()
