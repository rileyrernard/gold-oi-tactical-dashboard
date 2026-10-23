import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'skills/gold-oi-tactical-dashboard/scripts'))
from install_skill import install, manifest
from validate_extracted_csv import validate_datasets

def data():
    common=dict(as_of_date='2026-01-02',contract='DEMO',expiry='2026-02-01',strike='4000')
    return {'oi':[dict(common,call_oi='10',put_oi='12')],
            'change':[dict(common,call_oi_change='2',put_oi_change='-1')],
            'volume':[dict(common,call_volume='5',put_volume='3')]}

class DistributionTests(unittest.TestCase):
    def test_installer_scopes_integrity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            for agent in ('codex','claude','antigravity'):
                project=base/agent; project.mkdir()
                target=install(agent,project)
                self.assertEqual(manifest(target),manifest(ROOT/'skills/gold-oi-tactical-dashboard'))
                self.assertEqual(install(agent,project),target)
                marker=target/'SKILL.md'; marker.write_text('preserve user edit',encoding='utf-8')
                with self.assertRaises(ValueError): install(agent,project)
                self.assertEqual(marker.read_text(encoding='utf-8'),'preserve user edit')
            for agent in ('codex','claude','antigravity'):
                self.assertTrue(install(agent,user=True,user_home=base/'fake-home').is_dir())

    def test_rejects_coverage_dates_and_contract_mismatch(self):
        self.assertEqual(set(validate_datasets(data()).values()),{'2026-01-02'})
        for field,value in [('strike','4001'),('as_of_date','2026-01-03'),('contract','OTHER')]:
            d=data(); d['volume'][0][field]=value
            with self.assertRaises(ValueError): validate_datasets(d)

    def test_rejects_missing_unsafe_fractional_and_normalized_duplicates(self):
        for value in ('','NaN','Infinity','1.5','9007199254740992'):
            d=data();d['volume'][0]['call_volume']=value
            with self.assertRaises(ValueError):validate_datasets(d)
        d=data();d['oi'].append(dict(d['oi'][0],strike='4000.0'))
        with self.assertRaises(ValueError):validate_datasets(d)

if __name__=='__main__': unittest.main()
