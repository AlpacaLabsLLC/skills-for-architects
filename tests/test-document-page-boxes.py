#!/usr/bin/env python3
"""Synthetic PDF geometry probes; requires the declared host pypdf capability."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(os.environ.get('AS_TEST_OUTPUTS_ROOT',ROOT))
sys.path.insert(0,str(SOURCE/'tools/renderers'))
spec=importlib.util.spec_from_file_location('outputs',SOURCE/'tools/renderers/ffe_outputs.py');outputs=importlib.util.module_from_spec(spec);spec.loader.exec_module(outputs)
try:
    from pypdf import PdfWriter
    from pypdf.generic import NameObject,NumberObject,RectangleObject
except ImportError:
    PdfWriter=None

@unittest.skipUnless(PdfWriter,'Host pypdf unavailable; page-box acceptance not exercised')
class Geometry(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def pdf(self,change=None):
        writer=PdfWriter();writer.add_blank_page(width=612,height=792);writer.add_blank_page(width=612,height=792)
        if change:change(writer.pages[1])
        target=self.root/'fixture.pdf';writer.write(target);return target
    def check(self,path):return outputs.verify_page_boxes(path,{'width_pt':612,'height_pt':792})
    def test_matching_all_pages_pass(self):self.assertEqual(len(self.check(self.pdf())),2)
    def test_wrong_second_page_size_is_rejected(self):
        with self.assertRaises(ValueError):self.check(self.pdf(lambda p:setattr(p,'mediabox',RectangleObject([0,0,595,842]))))
    def test_crop_concealing_content_is_rejected(self):
        with self.assertRaises(ValueError):self.check(self.pdf(lambda p:setattr(p,'cropbox',RectangleObject([0,0,600,792]))))
    def test_rotation_cannot_stand_in_for_landscape(self):
        with self.assertRaises(ValueError):self.check(self.pdf(lambda p:p.rotate(90)))
    def test_userunit_scaling_is_rejected(self):
        with self.assertRaises(ValueError):self.check(self.pdf(lambda p:p.__setitem__(NameObject('/UserUnit'),NumberObject(2))))
    def test_shifted_origin_is_rejected(self):
        with self.assertRaises(ValueError):self.check(self.pdf(lambda p:setattr(p,'mediabox',RectangleObject([10,10,622,802]))))

if __name__=='__main__':unittest.main()
