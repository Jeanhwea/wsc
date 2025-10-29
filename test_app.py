# -*- coding: utf-8 -*-
from app import DataCollector
from unittest import TestCase


class TestDartBalloonGame(TestCase):

    def test_calc_md5(self):
        target = "D:/temp/aaa.png"
        hash_md5 = DataCollector.calc_file_md5_hash(target)
        print(hash_md5)

        self.assertEqual(64, len(hash_md5))

    def test_update_atlas_png_file(self):
        src = "./example/南瓜瓶/南瓜瓶子_接水.atlas"
        dst = "./temp/1.atlas"
        png_name = "心形瓶子_接水.png"
        DataCollector._replace_atlas_png_file(src, dst, png_name)

    def test_list_atlas_files(self):
        src_dir = "./example/南瓜瓶"
        atlas_files = DataCollector._list_glob_files(src_dir, "atlas")
        print(atlas_files)
        self.assertEqual(1, len(atlas_files))
