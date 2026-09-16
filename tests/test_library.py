import unittest,pathlib
class T(unittest.TestCase):
 def test_examples_exist(self):
  root=pathlib.Path(__file__).parents[1];self.assertTrue((root/'skills/git-expert/SKILL.md').exists())
if __name__=='__main__':unittest.main()
