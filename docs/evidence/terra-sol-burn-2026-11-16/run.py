import json,os,subprocess,sys,time,sqlite3,shutil,urllib.request,glob
B=os.path.dirname(os.path.abspath(__file__)); tasks=json.load(open(os.path.join(B,'tasks.json'),encoding='utf-8'))
runs=[('a','gpt-6.1-terra','default'),('a','gpt-6.1-sol','default'),('b','gpt-6.1-terra','default'),('b','gpt-6.1-sol','default'),('c','gpt-6.1-terra','default'),('c','gpt-6.1-sol','default'),('a','gpt-6.1-terra','priority'),('a','gpt-6.1-sol','priority')]
def quota():
    try:
        d=json.load(urllib.request.urlopen('http://127.0.0.1:8765/api/data?h=1',timeout=90)); q=d['codex']['quota']; return q['five_hour']['used'],q['weekly']['used']
    except Exception as e: return None,None
def busy():
    out=subprocess.run(['powershell','-NoProfile','-Command',"(Get-CimInstance Win32_Process -Filter \"Name='codex.exe'\" | Where-Object { $_.CommandLine -match ' exec ' }).Count"],capture_output=True,text=True).stdout.strip()
    return out
env=dict(os.environ,CODEX_HOME=r'C:\AgentData\Agents\codex\.codex')
codex=os.path.expanduser('~/bin/codex.cmd'); res=json.load(open(os.path.join(B,'results.json'),encoding='utf-8')) if len(sys.argv)>1 else []
sel=[int(x) for x in sys.argv[1:]]
for i,(t,model,tier) in enumerate(runs):
    if sel and i not in sel: continue
    d=os.path.join(B,f'run{i}{"r" if sel else ""}-{t}-{model.split("-")[-1]}-{tier}'); shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    subprocess.run(['git','init','-q',d]); 
    other=busy(); q0=quota(); t0=time.time()
    p=subprocess.run(['cmd','/c',codex,'exec','-C',d,'-m',model,'-s','workspace-write','-c',f'service_tier="{tier}"','-c','model_reasoning_effort="medium"','--skip-git-repo-check',tasks[t]['prompt']],stdin=subprocess.DEVNULL,capture_output=True,text=True,encoding='utf-8',errors='replace',env=env)
    dt=time.time()-t0; time.sleep(5); q1=quota()
    con=sqlite3.connect('file:C:/AgentData/Agents/codex/.codex/state_5.sqlite?mode=ro',uri=True)
    row=con.execute('select id,tokens_used,model from threads where cwd like ? order by created_at desc limit 1',('%'+os.path.basename(d),)).fetchone()
    for h in glob.glob(os.path.join(B,'hidden','test_hidden_'+tasks[t]['module']+'.py')): shutil.copy(h,d)
    g=subprocess.run([sys.executable,'-m','unittest','test_hidden_'+tasks[t]['module'],'-v'],cwd=d,capture_output=True,text=True)
    passed=g.stderr.count(' ... ok'); total=g.stderr.count(' ... ')
    r=dict(run=i,task=t,model=model,tier=tier,exit=p.returncode,secs=round(dt),thread=row[0] if row else None,tokens=row[1] if row else None,quota_5h_before=q0[0],quota_5h_after=q1[0],weekly_before=q0[1],weekly_after=q1[1],other_codex_exec_at_start=other,hidden_pass=f'{passed}/{total}')
    res=[x for x in res if x['run']!=i]+[dict(r,rerun=bool(sel))]; res.sort(key=lambda x:x['run']); print(json.dumps(r,ensure_ascii=False),flush=True)
    json.dump(res,open(os.path.join(B,'results.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
