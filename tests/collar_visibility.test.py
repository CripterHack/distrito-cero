#!/usr/bin/env python3
"""Analytic checks for the offline collar projection diagnostic."""
from pathlib import Path
import importlib.util
import math
import unittest
import numpy as np

PATH=Path(__file__).resolve().parents[1]/'tools/qa/project_collar_visibility.py'
spec=importlib.util.spec_from_file_location('collar_visibility',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def plane(z, x=0):
    return module.Surface([x-2,-2,z, x+2,-2,z, x,2,z])


class ProjectionTests(unittest.TestCase):
    camera={'eye':[0,0,-1], 'target':[0,0,0], 'fov':math.pi/2}

    def test_points_behind_eye_are_not_projected_into_viewport(self):
        result=module.project([0,0,-2],self.camera)
        self.assertFalse(result['inFront']);self.assertFalse(result['withinViewport'])
        self.assertIsNone(result['coordinates'])

    def test_perspective_uses_forward_depth_not_euclidean_distance(self):
        near=module.project([.25,0,0],self.camera)
        far=module.project([.25,0,1],self.camera)
        self.assertAlmostEqual(near['coordinates'][0],270)
        self.assertAlmostEqual(far['coordinates'][0],315)
        self.assertAlmostEqual(near['depthM'],1)
        self.assertNotAlmostEqual(np.linalg.norm(np.array([.25,0,0])-self.camera['eye']),near['depthM'])

    def test_pixel_center_ray_is_distinct_from_continuous_target(self):
        point=[0,0,0];projected=module.project(point,self.camera)
        self.assertEqual(projected['coordinates'],[360,360])
        direction=module.pixel_direction([360,360],self.camera)
        self.assertNotEqual(float(direction[0]),0);self.assertNotEqual(float(direction[1]),0)
        self.assertAlmostEqual(float(np.linalg.norm(direction)),1)
        hit=plane(0).hit(np.array(self.camera['eye']),direction)
        self.assertIsNotNone(hit);self.assertGreater(hit['distanceM'],1)

    def test_missing_skin_probe_does_not_imply_background_or_garment_hole(self):
        surfaces={'skin2':plane(0,10),'jacket1':plane(-.2),'oldJacket2':plane(-.3),'sourceJacket0':plane(-.4)}
        self.assertIsNone(surfaces['skin2'].hit(np.zeros(3),np.array([0,0,1]),signed=True))
        result=module.ray_view([0,0,0],self.camera,surfaces)
        self.assertEqual(result['afterWinner'],'jacket1')
        self.assertEqual(result['afterPixelWinner'],'jacket1')

    def test_depth_order_detects_new_exposure_without_backface_culling(self):
        surfaces={'skin2':plane(0),'jacket1':plane(.2),'oldJacket2':plane(-.2),'sourceJacket0':plane(-.1)}
        result=module.ray_view([0,0,0],self.camera,surfaces)
        self.assertEqual(result['beforeWinner'],'oldJacket2')
        self.assertEqual(result['afterWinner'],'skin2')
        self.assertEqual(result['beforePixelWinner'],'oldJacket2')
        self.assertEqual(result['afterPixelWinner'],'skin2')
        self.assertEqual(result['sourceJacketWinnerAgainstSkin2'],'sourceJacket0')


if __name__=='__main__':unittest.main()
