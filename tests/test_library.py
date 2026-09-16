import unittest,pathlib,tempfile,sys,json
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]));import skilldock
class T(unittest.TestCase):
 def test_examples_exist(self):self.assertTrue((pathlib.Path(__file__).parents[1]/'skills/git-expert/SKILL.md').exists())
 def test_hash_detects_change(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'SKILL.md').write_text('one');a=skilldock.skill_hash(p);(p/'SKILL.md').write_text('two');self.assertNotEqual(a,skilldock.skill_hash(p))
 def test_registry(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'r.json';p.write_text(json.dumps({'skills':[{'name':'x','source':'./x','description':'Git helper'}]}));self.assertEqual(skilldock.load_registry(str(p))[0]['name'],'x')
 def test_local_source_add(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);src=root/'src';src.mkdir();(src/'SKILL.md').write_text('# skill');oldlib,oldsources=skilldock.LIB,skilldock.SOURCES
   try:
    skilldock.LIB=root/'lib';skilldock.SOURCES=root/'sources.json';skilldock.source_add('demo',str(src));self.assertTrue((skilldock.LIB/'demo/SKILL.md').exists())
   finally:skilldock.LIB,skilldock.SOURCES=oldlib,oldsources
if __name__=='__main__':unittest.main()
