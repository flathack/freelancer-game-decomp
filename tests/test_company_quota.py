import importlib.util,json,pathlib,sys,threading,http.server,urllib.request,urllib.error,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/paperclip'))
import freelancer_quota as gate
import gateway_quota as gateway
import codex_quota as codex
class Upstream(http.server.BaseHTTPRequestHandler):
 calls=[]
 def log_message(self,*a):pass
 def do_POST(self):
  body=self.rfile.read(int(self.headers.get('Content-Length','0')));self.calls.append((self.path,self.headers.get('Authorization'),body))
  data=b'{"run_id":"fixture-run"}';self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  self.calls.append((self.path,self.headers.get('Authorization'),b''));data=b'{"status":"running"}' if self.path.endswith('fixture-run') else b'data: completed\n\n'
  self.send_response(200);self.end_headers();self.wfile.write(data)
class CompanyQuota(unittest.TestCase):
 def setUp(self):
  Upstream.calls.clear();gateway.runs.clear();self.up=http.server.ThreadingHTTPServer(('127.0.0.1',0),Upstream)
  self.relay=http.server.ThreadingHTTPServer(('127.0.0.1',0),gateway.Handler)
  self.base='http://127.0.0.1:'+str(self.relay.server_port)
  self.patch=patch.object(gateway,'UPSTREAM','http://127.0.0.1:'+str(self.up.server_port));self.patch.start()
  for server in [self.up,self.relay]:threading.Thread(target=server.serve_forever,daemon=True).start()
 def tearDown(self):
  for server in [self.up,self.relay]:server.shutdown();server.server_close()
  self.patch.stop()
 def request(self,body):
  req=urllib.request.Request(self.base+'/api/v1/runs',data=json.dumps(body).encode(),headers={'Authorization':'Bearer fixture-only'})
  return urllib.request.urlopen(req,timeout=2)
 def test_insufficient_or_unknown_never_reaches_remote_model(self):
  for value in [30,29,None]:
   with patch.object(gate,'probe',return_value=(False,value)):
    with self.assertRaises(urllib.error.HTTPError) as error:self.request({'input':'Freelancer review'})
    self.assertEqual(error.exception.code,429);error.exception.close()
   self.assertEqual(Upstream.calls,[])
 def test_allowed_preserves_auth_body_and_tracks_run(self):
  with patch.object(gate,'probe',return_value=(True,90)):
   with self.request({'input':'Freelancer review'}) as r:self.assertEqual(json.load(r),{'run_id':'fixture-run'})
  self.assertEqual(Upstream.calls[0][1],'Bearer fixture-only');self.assertEqual(json.loads(Upstream.calls[0][2]),{'input':'Freelancer review'})
  self.assertIn('fixture-run',gateway.runs);self.assertNotIn('Content-Length',gateway.runs['fixture-run'][0])
 def test_other_tasks_and_events_passthrough(self):
  with patch.object(gate,'probe',side_effect=AssertionError('quota probe should not run')):
   with self.request({'input':'Other authorized work'}) as r:self.assertEqual(r.status,200)
   with urllib.request.urlopen(self.base+'/api/v1/runs/a/events',timeout=2) as r:self.assertEqual(r.read(),b'data: completed\n\n')
 def test_remote_run_is_cancelled_when_quota_drops(self):
  with patch.object(gate,'probe',return_value=(True,90)):
   with self.request({'input':'Freelancer review'}) as r:r.read()
  with patch.object(gate,'probe',return_value=(False,30)):
   gateway.monitor_once()
  self.assertEqual(Upstream.calls[-1],('/api/v1/runs/fixture-run/stop','Bearer fixture-only',b''))
  self.assertEqual(gateway.runs,{})
 def test_codex_scope(self):
  self.assertTrue(codex.scoped(['exec','-'],'Freelancer CEO','/tmp'))
  self.assertTrue(codex.scoped(['exec','-'],'Next milestone','/opt/data/projects/Freelancer-Decomp'))
  self.assertFalse(codex.scoped(['--version'],'','/tmp'))
  self.assertFalse(codex.scoped(['exec','-'],'Other task','/tmp'))
if __name__=='__main__':unittest.main()
