import unittest,pathlib,tempfile,sys
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]));import skilldock
class T(unittest.TestCase):
 def test_examples_exist(self): self.assertTrue((pathlib.Path(__file__).parents[1]/'skills/git-expert/SKILL.md').exists())
 def test_hash_detects_change(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'SKILL.md').write_text('one');a=skilldock.skill_hash(p);(p/'SKILL.md').write_text('two');self.assertNotEqual(a,skilldock.skill_hash(p))
if __name__=='__main__':unittest.main()
