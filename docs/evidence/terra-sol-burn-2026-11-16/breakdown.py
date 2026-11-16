import json,sqlite3
c=sqlite3.connect('file:C:/AgentData/Agents/codex/.codex/state_5.sqlite?mode=ro',uri=True)
res=json.load(open('results.json',encoding='utf-8'))
for r in res:
    p=c.execute('select rollout_path from threads where id=?',(r['thread'],)).fetchone()[0]
    last=None; err=None
    for l in open(p,encoding='utf-8'):
        if '"token_count"' in l:
            j=json.loads(l); u=(j['payload'].get('info') or {}).get('total_token_usage');  last=u or last
        if '"task_complete"' in l and '"error"' in l: err='502' if '502' in l else 'error'
    r.update(input=last['input_tokens'],cached=last['cached_input_tokens'],output=last['output_tokens'],reasoning=last['reasoning_output_tokens'],uncached=last['input_tokens']-last['cached_input_tokens'],upstream_error=err)
json.dump(res,open('results.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for r in res: print(r['run'],r['task'],r['model'][-5:],r['tier'],'tot',r['tokens'],'uncached',r['uncached'],'out',r['output'],'5h',r['quota_5h_before'],'->',r['quota_5h_after'],'secs',r['secs'],'hidden',r['hidden_pass'],'err',r['upstream_error'],'rerun',r.get('rerun',False))
