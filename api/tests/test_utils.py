import os
from unittest import TestCase

from werkzeug.datastructures import FileStorage

import utils


class TestUtils(TestCase):
    def test_allowed_file(self):
        self.assertTrue(utils.allowed_file("cat.JPG"))
        self.assertTrue(utils.allowed_file("cat.jpeg"))
        self.assertTrue(utils.allowed_file("cat.JPEG"))
        self.assertTrue(utils.allowed_file("../../car.PNG"))
        self.assertTrue(utils.allowed_file("/usr/var/src/car.gif"))

        self.assertFalse(utils.allowed_file("cat.JPGG"))
        self.assertFalse(utils.allowed_file("invoice.pdf"))
        self.assertFalse(utils.allowed_file("/usr/src/slides.odt"))
        self.assertFalse(utils.allowed_file("/usr/src/api"))
        self.assertFalse(utils.allowed_file("/usr/src/api/"))
        self.assertFalse(utils.allowed_file("/usr/src/dog."))
        self.assertFalse(utils.allowed_file("/usr/src/dog./"))

    def test_get_file_hash(self):
        filename = "tests/dog.jpeg"
        md5_filename = "0a7c757a80f2c5b13fa7a2a47a683593.jpeg"
        with open(filename, "rb") as fp:
            file = FileStorage(fp)

            # Check the new filename is correct
            new_filename = utils.get_file_hash(file)
            self.assertEqual(md5_filename, new_filename, new_filename)

            # Check the file content is still readable!
            self.assertTrue(file.read() != b"")
