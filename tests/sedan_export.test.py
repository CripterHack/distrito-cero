"""Verify the portable play-ready sedan and its native wheel parts."""
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


def unpack(name):
    raw = (ROOT/'assets'/name).read_bytes()
    if struct.unpack_from('<4sII',raw)!=(b'glTF',2,len(raw)):
        raise ValueError('Invalid GLB header')
    size,kind=struct.unpack_from('<I4s',raw,12)
    if kind!=b'JSON' or struct.unpack_from('<I4s',raw,20+size)!=(len(raw)-28-size,b'BIN\0'):
        raise ValueError('Invalid GLB container')
    return json.loads(raw[20:20+size]),raw[28+size:]


def native_vertices(doc, binary, node):
    primitive=doc['meshes'][node['mesh']]['primitives'][0]
    accessor=doc['accessors'][primitive['attributes']['POSITION']]
    view=doc['bufferViews'][accessor['bufferView']]
    if view['byteStride']!=32 or view['byteLength']!=accessor['count']*32:
        raise ValueError('Invalid native vertex stream')
    return binary[view['byteOffset']:view['byteOffset']+view['byteLength']]


class SedanExport(unittest.TestCase):
    def test_full_car_and_four_articulated_wheel_sets(self):
        car,data=unpack('dc-native-sedan.glb')
        wheel,reference=unpack('dc-sedan-wheel.glb')
        wheel_meshes={n['name']:native_vertices(wheel,reference,n) for n in wheel['nodes'] if 'mesh' in n}
        nodes=car['nodes']
        ids={n['name']:i for i,n in enumerate(nodes)}
        parts=[n for n in nodes if 'mesh' in n]
        self.assertEqual(len(parts),59)
        self.assertEqual(sum(len(native_vertices(car,data,n))//96 for n in parts),15570)
        self.assertTrue({'asset_BODY_shell','asset_GLASS_rear','asset_GLASS_windshield','steeringRing'}<=ids.keys())
        for corner,x,z in [('FrontLeft',-.92,1.36),('FrontRight',.92,1.36),
                           ('RearLeft',-.92,-1.39),('RearRight',.92,-1.39)]:
            steer,roll=ids['Steering_'+corner],ids['Rolling_'+corner]
            self.assertEqual(nodes[steer]['translation'],[x,.365,z])
            self.assertIn(roll,nodes[steer]['children'])
            for key,vertices in wheel_meshes.items():
                mesh_id=ids[corner+'_'+key]
                self.assertIn(mesh_id,nodes[steer if key=='wheelCaliper' else roll]['children'])
                buffer=native_vertices(car,data,nodes[mesh_id])
                self.assertEqual(len(buffer),len(vertices))
                # Node and Chromium agree on positions/UVs. Normal accumulation
                # at a symmetric spoke seam differs by 8.43e-17 between V8 builds.
                if buffer!=vertices:
                    for a,b in zip(struct.iter_unpack('<8f',buffer),struct.iter_unpack('<8f',vertices),strict=True):
                        self.assertEqual(a[:3]+a[6:],b[:3]+b[6:])
                        self.assertLessEqual(max(abs(x-y) for x,y in zip(a[3:6],b[3:6])),2.22e-16)


if __name__=='__main__':
    unittest.main()
