import json,pathlib,tempfile,unittest,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]));import skilllock
class T(unittest.TestCase):
 def make_skill(self,lib,name,text='x'):
  p=lib/name;p.mkdir(parents=True);(p/'SKILL.md').write_text(text);return p
 def test_lock_and_verify(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);lib=root/'skills';lib.mkdir();self.make_skill(lib,'a');lock=root/'lock.json';skilllock.write_lock(lock,lib,root/'sources.json');self.assertEqual(skilllock.verify_lock(lock,lib)[0]['status'],'ok')
 def test_drift(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);lib=root/'skills';lib.mkdir();p=self.make_skill(lib,'a');lock=root/'lock.json';skilllock.write_lock(lock,lib,root/'sources.json');(p/'SKILL.md').write_text('changed');self.assertEqual(skilllock.verify_lock(lock,lib)[0]['status'],'drifted')
 def test_unlocked(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);lib=root/'skills';lib.mkdir();self.make_skill(lib,'a');(root/'lock.json').write_text('{"skills":[]}');self.assertEqual(skilllock.verify_lock(root/'lock.json',lib)[0]['status'],'unlocked')
if __name__=='__main__':unittest.main()
