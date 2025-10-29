# -*- coding: utf-8 -*-
from app import DataCollector
from unittest import TestCase


class TestDartBalloonGame(TestCase):

    def test_calc_md5(self):
        target = "D:/temp/aaa.png"
        hash_md5 = DataCollector.calc_file_md5_hash(target)
        print(hash_md5)

        self.assertEqual(64, len(hash_md5))
