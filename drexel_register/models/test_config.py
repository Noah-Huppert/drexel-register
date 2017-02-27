import unittest

from models.config import Config

class ConfigTest (unittest.TestCase):
    def test_from_file(self):
        config = Config.from_file("../test-data/config.test.yaml")

        self.assertEqual(config.year, "16-17")
        self.assertEqual(config.quarter, "spring")
        self.assertEqual(config.courses, [
            {
                'subject': "MATH",
                'course': 201,
                'types': ["lecture", "lab"],
                'crns': [
                    {
                        'lecture': [
                            "!12345!"
                        ]
                    },
                    {
                        'lab': [
                            54321,
                            21345
                        ]
                    }
                ]
            },
            {
                'subject': "CS",
                'course': 172
            }
        ])