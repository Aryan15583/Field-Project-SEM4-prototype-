import json,re,subprocess,sys
reg=json.load(open('builder/registry.json'))
n=int(re.search(r'Pages:\s+(\d+)',subprocess.check_output(['pdfinfo','Codeingo_Field_Project_Report.pdf']).decode()).group(1))
pages=[]
for i in range(1,n+1):
    t=subprocess.check_output(['pdftotext','-f',str(i),'-l',str(i),'-layout','Codeingo_Field_Project_Report.pdf','-']).decode()
    lines=[l.strip() for l in t.splitlines() if l.strip()]
    foot=lines[-1] if lines else ''
    pages.append((foot,re.sub(r'\s+',' ',t)))
norm=lambda s:re.sub(r'\s+',' ',s)
out={};miss=[]
items=[e['search'] for e in reg['toc']]+[e['search'] for e in reg['tables']]+[e['search'] for e in reg['figures']]
for s in items:
    key=norm(s)[:60]
    for foot,t in pages:
        if foot.isdigit() and key in t:
            out[s]=int(foot);break
    else: miss.append(s)
json.dump(out,open('builder/pages.json','w'))
print(len(out),'found; missing',len(miss));print(miss[:15])
