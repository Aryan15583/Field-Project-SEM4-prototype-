import json,re,subprocess
pdf='Aryan_Sawant_Codeingo_Field_Project_Report.pdf'
reg=json.load(open('registry3.json'))
n=int(re.search(r'Pages:\s+(\d+)',subprocess.check_output(['pdfinfo',pdf]).decode()).group(1))
pages=[re.sub(r'\s+',' ',subprocess.check_output(['pdftotext','-f',str(i),'-l',str(i),'-layout',pdf,'-']).decode()) for i in range(1,n+1)]
start=next(i for i,t in enumerate(pages) if 'Periodic Field Project Report' in t)
out={};miss=[]
for e in reg['toc']+reg['tables']+reg['figures']:
    s=e['search'];k=re.sub(r'\s+',' ',s)[:60]
    for i in range(start,n):
        if k in pages[i]: out[s]=i+1;break
    else: miss.append(s)
json.dump(out,open('pages3.json','w'));print(n,'pages;',len(out),'found; missing',miss)
