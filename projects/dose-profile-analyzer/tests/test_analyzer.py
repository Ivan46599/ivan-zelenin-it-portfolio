from pathlib import Path
import tempfile
import unittest
import warnings

import numpy as np
from scipy.special import erf

from dose_analyzer.io import Profile, load_profile, load_reference
from dose_analyzer.measurement import analyze_profile, locate_lattice, shared_pitch
from dose_analyzer.outputs import compare_reference


def synthetic(offset=0., slope=0., noisy=True):
    x = np.linspace(0, 1.035, 1700)
    c = .055 + .1*np.arange(10)
    depths = np.linspace(2., 155., 10)
    z = 27 + offset + (12+slope)*x + 1.5*x*x
    for center, depth in zip(c, depths):
        box = .5*(erf((x-(center-.015))/.0012)-erf((x-(center+.015))/.0012))
        z -= depth*box
    if noisy:
        z += np.random.default_rng(420).normal(0,.035,len(x))
        z[[235,568,912,1350]] += [20.,-30.,40.,-25.]
    return Profile('synthetic',Path('synthetic.txt'),x,z,{}), depths


class MeasurementTests(unittest.TestCase):
    def test_known_depths_without_using_reference(self):
        p, expected = synthetic()
        g = locate_lattice(p,10)
        rows,_=analyze_profile(p,g,{})
        self.assertEqual(sum(r['depth_nm'] is not None for r in rows),10)
        error=np.asarray([r['depth_nm'] for r in rows])-expected
        self.assertLess(float(np.max(abs(error))),.25)
        self.assertLess(abs(g['pitch_mm']-.1),.002)

    def test_vertical_offset_and_linear_tilt_invariance(self):
        p,_=synthetic(noisy=False); q,_=synthetic(offset=1234.,slope=55.,noisy=False)
        g={'count':10,'pitch_mm':.1,'first_center_mm':.055}
        a,_=analyze_profile(p,g,{});b,_=analyze_profile(q,g,{})
        np.testing.assert_allclose([r['depth_nm'] for r in a],[r['depth_nm'] for r in b],atol=.025)

    def test_flat_signal_is_not_ten_detected_steps(self):
        p,_=synthetic();p.z[:]=17.
        rows,_=analyze_profile(p,locate_lattice(p,10),{})
        self.assertTrue(all(r['depth_nm'] is None for r in rows))

    def test_cropped_feature_is_unresolved(self):
        p,_=synthetic();m=p.x>=.05;p.x=p.x[m];p.z=p.z[m]
        g={'count':10,'pitch_mm':.1,'first_center_mm':.055}
        rows,_=analyze_profile(p,g,{})
        self.assertIsNone(rows[0]['depth_nm'])

    def test_grid_and_manual_modes(self):
        p,expected=synthetic(noisy=False)
        g={'count':10,'pitch_mm':.1,'first_center_mm':.055}
        for mode in ['grid','manual']:
            options={'mode':mode,'intervals_mm':{str(i+1):[.055+.1*i-.015,.055+.1*i+.015] for i in range(10)}}
            rows,_=analyze_profile(p,g,options)
            np.testing.assert_allclose([r['depth_nm'] for r in rows],expected,atol=.04)
        with self.assertRaises(ValueError):analyze_profile(p,g,{'mode':'manual'})

    def test_dose_labels_cannot_change_depth(self):
        p,_=synthetic();g=locate_lattice(p,10)
        a,_=analyze_profile(p,g,{},list(range(1,11)))
        b,_=analyze_profile(p,g,{},list(range(300,310)))
        self.assertEqual([r['depth_nm'] for r in a],[r['depth_nm'] for r in b])

    def test_large_gap_is_not_interpolated_for_measurement(self):
        p,_=synthetic();m=~((p.x>.043)&(p.x<.063));p.x=p.x[m];p.z=p.z[m]
        rows,_=analyze_profile(p,{'count':10,'pitch_mm':.1,'first_center_mm':.055},{})
        self.assertIsNone(rows[0]['depth_nm'])

    def test_common_pitch_needs_agreement(self):
        self.assertIsNone(shared_pitch({'a':dict(pitch_mm=.1,score=10,count=10)}))
        self.assertIsNone(shared_pitch({'a':dict(pitch_mm=.1,score=10,count=10),'b':dict(pitch_mm=.2,score=10,count=10)}))


class InputTests(unittest.TestCase):
    def test_duplicates_no_header_and_no_lost_first_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'p.txt'
            p.write_text('\n'.join(f'{i//2*.001}\t{i}' for i in range(60)))
            a=load_profile(p,x_unit='mm',z_unit='nm')
            self.assertEqual(a.metadata['raw_points'],60)
            self.assertEqual(a.metadata['duplicate_x'],30)
            self.assertEqual(a.z[0],.5)
            self.assertTrue(np.all(np.diff(a.x)>0))
            with warnings.catch_warnings():
                warnings.simplefilter('error',RuntimeWarning)
                self.assertTrue(np.all(np.isfinite(np.gradient(a.z,a.x))))

    def test_decimal_comma_units_and_reversed_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'p.txt'
            p.write_text('X(um)\tZ(um)\n'+'\n'.join(f'{i},0\t0,160' for i in range(30,-1,-1)))
            a=load_profile(p)
            self.assertTrue(a.metadata['reversed_scan'])
            self.assertAlmostEqual(a.x[-1],.03)
            self.assertAlmostEqual(a.z[0],160.)

    def test_matrix_and_multiple_sweeps_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'p.txt';p.write_text('1 2 3\n'*25)
            with self.assertRaises(ValueError):load_profile(p)
            p.write_text('X(mm)\tZ(nm)\n'+'\n'.join(f'{i} 0' for i in [*range(20),*range(20,0,-1)]))
            with self.assertRaises(ValueError):load_profile(p)

    def test_nonfinite_points_are_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'p.txt';p.write_text('X(mm) Z(nm)\n'+'\n'.join(f'{i} {i}' for i in range(30))+'\n30 nan\n')
            a=load_profile(p)
            self.assertEqual(a.metadata['nonfinite_removed'],1)

    def test_reference_compared_by_dose_with_visible_missing(self):
        rows=[dict(profile='a',square=1,dose=11,depth_nm=4.,status='measured'),
              dict(profile='a',square=2,dose=12,depth_nm=None,status='unresolved')]
        refs=[dict(dose=12,manual_depth_nm=10.,reference_row=1),dict(dose=11,manual_depth_nm=3.,reference_row=2),dict(dose=30,manual_depth_nm=5.,reference_row=3)]
        comparison,m=compare_reference(rows,refs)
        self.assertEqual(m['all_resolved']['mae_nm'],1.)
        self.assertEqual(m['all_resolved']['n'],1)
        self.assertEqual(m['unresolved_matched'],1)
        self.assertEqual(m['unmatched_reference_doses'],[30])

    def test_bad_reference_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'ref.csv';p.write_text('dose;depth\n1;2\n1;3\n')
            with self.assertRaises(ValueError):load_reference(p,{'start_row':2})


if __name__=='__main__':unittest.main()
