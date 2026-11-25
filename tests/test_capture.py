import json, unittest
from pathlib import Path
class CaptureTests(unittest.TestCase):
 def test_checked_capture_has_distinct_source_dates_and_real_reports(self):
  root=Path(__file__).resolve().parents[1];data=json.loads((root/'web/data/latest.json').read_text())
  self.assertEqual(data['schema'],1);self.assertTrue(data['checked_at'])
  reports=[r for c in data['captures'] for r in c['reports'].values()]
  self.assertEqual(data['record_count'],len(reports));self.assertGreater(len(reports),0)
  for c in data['captures']:
   self.assertTrue(c['source_updated']);self.assertEqual(c['total'],len(c['establishments']))
  for r in reports:
   self.assertTrue(r['inspections']);self.assertNotIn('score',r)
