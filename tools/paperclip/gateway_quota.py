#!/usr/bin/python3
"""Loopback-only gateway relay; retain existing upstream auth and gate Freelancer runs."""
import http.server,json,threading,time,urllib.request,urllib.error
import freelancer_quota as gate
UPSTREAM='http://nasa-cachy.tail2b5c2.ts.net:8642'
HOP={'connection','transfer-encoding','keep-alive','proxy-authenticate','proxy-authorization','te','trailer','upgrade','host'}
runs={};lock=threading.Lock()
def scoped(body):return b'freelancer' in body.lower() or b'093c103e-0cc0-4ed2-8c9b-cf5eca333e76' in body.lower()
def run_id(value):
    if isinstance(value,dict):
        for key in ['run_id','runId','id']:
            if isinstance(value.get(key),str):return value[key]
        for key in ['data','run']:
            if key in value:
                found=run_id(value[key])
                if found:return found
    return None
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):self.relay()
    def do_POST(self):self.relay()
    def do_DELETE(self):self.relay()
    def relay(self):
        if not self.path.startswith('/') or self.path.startswith('//'):
            self.send_error(400);return
        length=int(self.headers.get('Content-Length','0'))
        if length>2_000_000:self.send_error(413);return
        body=self.rfile.read(length) if length else b''
        protected=self.command=='POST' and self.path.rstrip('/').endswith('/v1/runs') and scoped(body)
        if protected:
            allowed,remaining=gate.probe();gate.log(allowed,remaining)
            if not allowed:
                self.send_response(429);self.send_header('Content-Type','application/json');self.end_headers()
                self.wfile.write(b'{"error":"Freelancer requires more than 30 percent weekly quota; current quota insufficient or unknown"}');return
        headers={k:v for k,v in self.headers.items() if k.lower() not in HOP and k.lower() != 'content-length'}
        req=urllib.request.Request(UPSTREAM+self.path,data=body if self.command!='GET' else None,headers=headers,method=self.command)
        try:
            try:response=urllib.request.urlopen(req,timeout=60)
            except urllib.error.HTTPError as error:response=error
            with response:
                self.send_response(response.status)
                for k,v in response.headers.items():
                    if k.lower() not in HOP:self.send_header(k,v)
                self.end_headers()
                if protected and response.status<300:
                    data=response.read();self.wfile.write(data)
                    try:identifier=run_id(json.loads(data))
                    except ValueError:identifier=None
                    if identifier:
                        with lock:runs[identifier]=(headers,self.path.rstrip('/'))
                else:
                    while True:
                        data=response.read1(4096)
                        if not data:break
                        self.wfile.write(data);self.wfile.flush()
        except (OSError,ValueError):
            self.close_connection=True

def monitor_once():
    with lock:active=list(runs.items())
    if not active:return
    allowed,remaining=gate.probe();gate.log(allowed,remaining)
    for identifier,(headers,base) in active:
        url=UPSTREAM+base+'/'+urllib.parse.quote(identifier,safe='')
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15) as r:status=json.load(r)
            for key in ['data','run']:
                if isinstance(status.get(key),dict):status=status[key]
            if str(status.get('status','')).lower() in ['completed','succeeded','failed','cancelled','canceled','stopped','error','done']:
                with lock:runs.pop(identifier,None)
                continue
            if not allowed:
                with urllib.request.urlopen(urllib.request.Request(url+'/stop',data=b'',headers=headers,method='POST'),timeout=15) as r:r.read()
                with lock:runs.pop(identifier,None)
        except (OSError,ValueError):pass

def monitor():
    while True:
        time.sleep(gate.INTERVAL)
        monitor_once()
if __name__=='__main__':
    threading.Thread(target=monitor,daemon=True).start()
    http.server.ThreadingHTTPServer(('127.0.0.1',18642),Handler).serve_forever()
