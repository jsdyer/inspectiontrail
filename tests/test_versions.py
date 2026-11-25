import re,sys,tempfile,unittest,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import ROOT,build
class VersionTests(unittest.TestCase):
 def test_whole_asset_graph_changes_with_data_and_preserves_probe_bytes(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);shutil.copytree(ROOT/'web',root/'web')
   for name in ['tool.json','README.md']:shutil.copyfile(ROOT/name,root/name)
   build(root);old=(root/'dist/index.html').read_text();version=re.search(r'\?v=([a-f0-9]{16})',old).group(1)
   app=(root/'dist/app.mjs').read_text();self.assertIn('./model.mjs?v='+version,app);self.assertIn('./data/latest.json?v='+version,app)
   self.assertEqual((root/'web/data/status.json').read_bytes(),(root/'dist/data/status.json').read_bytes())
   build(root);self.assertEqual(old,(root/'dist/index.html').read_text())
   with (root/'web/data/latest.json').open('a') as f:f.write('\n')
   build(root);self.assertNotEqual(old,(root/'dist/index.html').read_text())
