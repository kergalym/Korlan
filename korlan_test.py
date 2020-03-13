import unittest
from pathlib import Path

from main import app
from Settings.menu_settings import MenuSettings


class KorlanAppTest(unittest.TestCase):
    def test_check_and_do_cfg(self):
        result = app.check_and_do_cfg()
        self.assertEqual(isinstance(result, bool), True, "Should be bool")

    def test_input_validate(self):
        cfg_path = "{0}/Korlan - Daughter of the Steppes/settings.ini".format(str(Path.home()))
        result = MenuSettings().input_validate(cfg_path=cfg_path, op_type='lng')
        self.assertEqual(isinstance(result, str), True, "Should be str")


if __name__ == '__main__':
    unittest.main()
