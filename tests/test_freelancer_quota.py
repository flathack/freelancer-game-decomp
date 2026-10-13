"""Quota boundary, unknown data and project isolation without live model calls."""
import importlib.util
import pathlib
import unittest
from unittest.mock import patch, Mock
import subprocess
p=pathlib.Path(__file__).resolve().parents[1]/'tools/paperclip/freelancer_quota.py'
s=importlib.util.spec_from_file_location('quota',p);quota=importlib.util.module_from_spec(s);s.loader.exec_module(quota)
class QuotaTest(unittest.TestCase):
 def document(self,used):return dict(provider='openai-codex',windows=[dict(label='Weekly',used_percent=used)])
 def test_boundary(self):
  for used,allowed in [(0,True),(10,True),(69.99,True),(70,False),(70.01,False),(100,False)]:
   self.assertEqual(quota.decision(self.document(used)),(allowed,100-used))
 def test_unknown(self):
  for used in [None,True,'10',-1,101,float('nan'),float('inf')]:self.assertEqual(quota.decision(self.document(used)),(False,None))
  self.assertEqual(quota.decision(dict(provider='openai-codex',windows=[])),(False,None))
  self.assertEqual(quota.decision(dict(provider='other',windows=[])),(False,None))
 def test_worst_weekly(self):
  d=self.document(10);d['windows'].append(dict(label='Weekly',used_percent=71));self.assertEqual(quota.decision(d),(False,29))
 def test_scope(self):
  self.assertTrue(quota.freelancer(['chat','-q','Work /opt/data/projects/Freelancer-Decomp']))
  self.assertTrue(quota.freelancer(['chat','--query','Freelancer: Decompilierung fortführen']))
  self.assertFalse(quota.freelancer(['chat','-q','DailyTasks']))
  self.assertFalse(quota.freelancer(['usage','--json']))
 def test_blocked_launch_uses_no_model(self):
  for remaining in [30,29,None]:
   with patch.object(quota,'probe',return_value=(False,remaining)), patch.object(quota.subprocess,'Popen') as launch:
    self.assertEqual(quota.main(['chat','-q','/opt/data/projects/Freelancer-Decomp']),0)
    launch.assert_not_called()
 def test_running_work_stops_at_boundary(self):
  child=Mock();child.poll.return_value=None
  child.wait.side_effect=subprocess.TimeoutExpired('fixture',60)
  def stopped(p):p.poll.return_value=0
  with patch.object(quota,'probe',side_effect=[(True,90),(False,30)]), patch.object(quota.subprocess,'Popen',return_value=child), patch.object(quota,'stop',side_effect=stopped) as stop:
   self.assertEqual(quota.main(['chat','-q','/opt/data/projects/Freelancer-Decomp']),0)
   stop.assert_called_once_with(child)
if __name__=='__main__':unittest.main()
