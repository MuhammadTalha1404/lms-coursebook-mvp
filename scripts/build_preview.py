#!/usr/bin/env python3
"""Build the clearly labeled, read-only HTML design preview.

The snapshot is calculated from the shipped sample SQL using the test adapter.
This script never starts a substitute backend or claims a MySQL connection.
"""
from pathlib import Path
from html import escape
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tests.sqlite_adapter import SQLiteTestDatabase
from lms.repository import Repository
from lms.reports import REPORTS
from lms.catalog import COLUMNS,DESCRIPTIONS,SINGULAR
from lms.ui import brand_html,heading_html,kpis_html,bars_html,status_html,table_html,icon


def markdown(text):
    blocks=[]
    for part in text.strip().split("\n\n"):
        part=part.strip()
        if not part: continue
        if part.startswith("### "):
            blocks.append("<h3>"+escape(part[4:])+"</h3>")
        else:
            html=escape(part.replace("\n"," "))
            html=re.sub(r"\*\*(.*?)\*\*",r"<strong>\1</strong>",html)
            blocks.append("<p>"+html+"</p>")
    return "".join(blocks)


def directory(entity,repo):
    rows=repo.list_records(entity)
    columns=dict(COLUMNS[entity])
    if entity=="courses": columns["fee"]="Fee (PKR)"
    html=table_html(rows,columns)
    pattern=re.compile(r"<tr>(.*?)</tr>",re.S)
    count=-1
    def annotate(match):
        nonlocal count
        count+=1
        if count==0: return match.group(0)
        row=rows[count-1]
        state=row.get("status",row.get("enrollment_status",""))
        return f'<tr data-record="1" data-status="{escape(str(state))}">'+match.group(1)+"</tr>"
    html=pattern.sub(annotate,html)
    statuses=("Enrolled","Completed","Dropped") if entity in {"enrollments","grades"} else ("Active","Inactive")
    options=''.join(f'<option>{value}</option>' for value in statuses)
    return f'''{heading_html(entity.capitalize(),DESCRIPTIONS[entity])}
    <div class="preview-tabs"><span class="selected">Records</span><button disabled title="Available in the running Streamlit application">Add {SINGULAR[entity]}</button><button disabled title="Available in the running Streamlit application">Edit {SINGULAR[entity]}</button><button disabled title="Available in the running Streamlit application">Delete {SINGULAR[entity]}</button></div>
    <div class="preview-filters"><label>Search records<input data-search="{entity}" type="search" placeholder="Search these sample records"></label><label>Status<select data-filter="{entity}"><option value="">All statuses</option>{options}</select></label></div>
    <p class="preview-count" data-count="{entity}">{len(rows)} matching sample record(s)</p>
    <div class="cb-card preview-directory" data-table="{entity}">{html}</div>
    <div class="preview-actions"><button class="preview-button" data-export="{entity}">Export displayed sample records</button><span>Editing is available in the Python application, not this preview.</span></div>'''


def main():
    db=SQLiteTestDatabase(seed=True)
    repo=Repository(db)
    summary=repo.summary()
    nav=[("dashboard","Dashboard","courses"),("students","Students","students"),("instructors","Instructors","instructors"),("courses","Courses","courses"),("enrollments","Enrollments","enrollments"),("grades","Grades","enrollments"),("reports","Reports","arrow")]
    links=''.join(f'<a href="#{key}" data-nav="{key}">{icon(symbol,18)}<span>{name}</span></a>' for key,name,symbol in nav)
    dash=f'''{heading_html("Academic overview","Student records, teaching assignments and course activity at a glance.")}
    <div class="preview-overview-line"><span>Snapshot of the included fictional training records.</span><a class="preview-button primary" href="#reports">View reports {icon("arrow",15)}</a></div>
    {kpis_html(summary)}
    <div class="preview-grid"><section class="cb-card"><h2 class="cb-card-title">Course popularity</h2><p class="cb-card-caption">Enrollment records across all statuses. Top six courses.</p>{bars_html(repo.report("BR-01"),"course_name","total_enrollments",limit=6)}</section>
    <section class="cb-card"><h2 class="cb-card-title">Enrollment status</h2><p class="cb-card-caption">Current status of every enrollment record.</p>{status_html(repo.report("BR-05"))}</section></div>
    <section class="cb-card preview-recent"><div class="cb-section-line"><div><h2 class="cb-card-title">Recent enrollments</h2><p class="cb-card-caption" style="margin-bottom:0">The six most recent course enrollment dates.</p></div><a href="#enrollments">View records {icon("arrow",14)}</a></div>{table_html(repo.recent_enrollments(),{"student_name":"Student","course_name":"Course","enrollment_date":"Enrolled on","status":"Status"})}</section>
    <p class="preview-count">{summary['awaiting_grades']} non-dropped enrollment(s) do not have a grade record yet.</p>'''
    pages=[f'<section class="preview-page" id="dashboard">{dash}</section>']
    for entity in COLUMNS:
        pages.append(f'<section class="preview-page" id="{entity}">{directory(entity,repo)}</section>')
    reportbuttons=''.join(f'<button data-report="{report.id}"><span>{report.id}</span>{escape(report.title)}</button>' for report in REPORTS)
    reportpanels=[]
    for report in REPORTS:
        rows=repo.report(report.id)
        cols={key:key.replace("_"," ").capitalize() for key in rows[0]} if rows else {}
        if report.id=="BR-05":
            chart=status_html(rows)
        elif report.id=="BR-04":
            chart=f'<div class="cb-status-total"><strong>{rows[0]["active_students"]}</strong><span>active students</span></div>'
        elif report.id in {"BR-01","BR-02","BR-03"}:
            label,value={"BR-01":("course_name","total_enrollments"),"BR-02":("instructor_name","course_count"),"BR-03":("student_name","total_marks")}[report.id]
            chart=bars_html(rows,label,value,limit=10)
        else: chart=""
        reportpanels.append(f'<section class="preview-report-panel" data-panel="{report.id}"><h2>{escape(report.title)}</h2><p class="report-description">{escape(report.description)}</p><div class="cb-card report-chart">{chart}</div><div class="cb-card preview-directory" data-table="{report.id}">{table_html(rows,cols)}</div><div class="preview-actions"><button class="preview-button" data-export="{report.id}">Export sample report</button></div><details><summary>View the SQL query</summary><pre>{escape(report.sql.strip())};</pre></details></section>')
    reports=heading_html("Reports","Six management reports, calculated from the included sample records.","Insights")+f'<div class="preview-report-grid"><nav class="preview-report-menu">{reportbuttons}</nav><div>{"".join(reportpanels)}</div></div>'
    pages.append(f'<section class="preview-page" id="reports">{reports}</section>')
    for slug,title,filename in [("terms","Terms & Conditions","TERMS.md"),("privacy","Privacy policy","PRIVACY.md")]:
        text=(ROOT/"docs"/filename).read_text().replace("{{INSTITUTE_NAME}}","Learning & Training Institute").replace("{{PRIVACY_CONTACT}}","Contact your institute administrator through your existing institute communication channel.")
        pages.append(f'<section class="preview-page" id="{slug}">{heading_html(title,"Project policy template. Complete the institute details before live use.","Workspace information")}<article class="preview-legal cb-card">{markdown(text)}</article></section>')
    stylesheet=(ROOT/"assets/style.css").read_text()
    extra_css=r'''*{box-sizing:border-box}body{margin:0;background:#f6f7f4;color:#182d2a;font-family:Arial,Helvetica,sans-serif}button,input,select{font:inherit}button,a,input,select{outline-offset:3px}a{color:#245f50}button{cursor:pointer}button:disabled{cursor:default}h2{font-size:19px}p{line-height:1.7}.preview-sidebar{position:fixed;inset:0 auto 0 0;width:246px;background:#172f2b;padding:27px 20px;z-index:30;overflow-y:auto}.preview-sidebar .cb-brand{margin:0 0 46px 4px}.preview-nav{display:flex;flex-direction:column;gap:5px}.preview-nav a{display:flex;align-items:center;gap:14px;padding:13px 15px;color:#c6d6c9;text-decoration:none;border-radius:4px;font-size:13px}.preview-nav a.active{background:#dce8cd;color:#193c30}.preview-nav a:hover{background:#264336}.preview-nav a.active:hover{background:#dce8cd}.preview-sidebar .cb-sidebar-section{margin-bottom:15px}.preview-sidebar .cb-sidebar-note{margin-top:40px}.preview-legal-nav{border-top:1px solid #365046;padding-top:20px;margin-top:23px;display:flex;flex-direction:column;gap:16px}.preview-legal-nav a{color:#a9beb0;font-size:11px;text-decoration:none}.preview-main{margin-left:246px;padding:30px 40px 22px;max-width:1600px}.preview-page{display:none}.preview-page.active{display:block}.preview-overview-line{display:flex;justify-content:space-between;align-items:center;margin:0 0 19px}.preview-overview-line>span{font-size:11px;color:#7b8575}.preview-button{display:inline-flex;align-items:center;justify-content:center;gap:10px;background:white;border:1px solid #ced8ca;color:#395540;border-radius:4px;padding:11px 15px;text-decoration:none;font-size:11px;font-weight:550;min-height:37px}.preview-button.primary{color:white;background:#245f50;border-color:#245f50}.preview-grid{display:grid;grid-template-columns:1.65fr 1fr;gap:18px}.preview-grid>.cb-card{min-width:0}.preview-recent{margin-top:20px}.preview-recent .cb-section-line>a{display:flex;gap:8px;align-items:center;font-size:11px;text-decoration:none}.preview-count{font-size:11px;color:#7b8475;margin:17px 0}.preview-tabs{display:flex;gap:28px;border-bottom:1px solid #dce3da;margin-bottom:24px;font-size:13px;align-items:center}.preview-tabs .selected{padding:0 0 15px;color:#245f50;border-bottom:2px solid #245f50}.preview-tabs button{border:0;background:transparent;font-size:12px;padding:0 0 15px;color:#9aa395}.preview-filters{display:grid;grid-template-columns:3fr 1fr;gap:18px}.preview-filters label{font-size:11px;color:#65755f;display:flex;flex-direction:column;gap:9px}.preview-filters input,.preview-filters select{padding:12px;border:1px solid #d7dfd0;border-radius:4px;background:#fff;color:#334c39;font-size:12px;width:100%;height:41px}.preview-directory{padding:0;overflow:hidden}.preview-directory .cb-table th{border-top:0}.preview-directory .cb-table td{padding-top:16px;padding-bottom:16px}.preview-actions{display:flex;align-items:center;gap:16px;margin-top:18px}.preview-actions span{font-size:11px;color:#838d7c}.preview-report-grid{display:grid;grid-template-columns:205px minmax(0,1fr);gap:25px}.preview-report-menu{display:flex;flex-direction:column;gap:8px}.preview-report-menu button{text-align:left;padding:13px 14px;background:white;border:1px solid #dce3da;border-radius:4px;font-size:12px;line-height:1.5;color:#4f654f}.preview-report-menu button span{display:block;font-size:9px;letter-spacing:1px;color:#8a947f;margin-bottom:4px}.preview-report-menu button.selected{background:#e7eedf;border-color:#adc29d;color:#2e5033}.preview-report-panel{display:none}.preview-report-panel.active{display:block}.preview-report-panel h2{font:normal 27px Georgia,serif;margin:0 0 10px}.report-description{font-size:12px;color:#70806c;margin:0 0 20px}.report-chart{margin-bottom:20px}.preview-report-panel details{margin-top:24px;background:#fff;border:1px solid #dce3da;border-radius:4px;padding:15px}.preview-report-panel summary{cursor:pointer;font-size:12px}.preview-report-panel pre{font-size:11px;line-height:1.7;overflow:auto;color:#52634a}.preview-legal{max-width:900px;font-size:13px;color:#586951;line-height:1.8;padding:30px}.preview-legal h3{font-size:16px;margin-top:26px}.preview-legal p{margin:0 0 17px}#menu-toggle{display:none}.cb-page-heading{margin-top:12px}.cb-topline{padding-bottom:21px}.cb-footer{margin-top:30px}@media(max-width:1100px){.preview-main{padding-left:25px;padding-right:25px}.preview-report-grid{grid-template-columns:160px minmax(0,1fr)}.preview-tabs{gap:16px}}@media(max-width:850px){.preview-sidebar{display:none}.preview-sidebar.open{display:block}.preview-main{margin-left:0;padding:20px}.preview-grid{grid-template-columns:1fr}.preview-overview-line{gap:15px}.preview-report-grid{grid-template-columns:1fr}.preview-report-menu{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}#menu-toggle{display:inline-flex;margin-bottom:20px}.preview-filters{grid-template-columns:1fr}.preview-actions{align-items:flex-start;flex-direction:column}.preview-tabs{gap:15px;overflow:auto;white-space:nowrap}.cb-topline{gap:8px}.cb-page-heading h1{font-size:33px}.cb-data-note{font-size:11px}.preview-recent .cb-section-line{align-items:flex-start;gap:16px}.preview-recent .cb-section-line>a{white-space:nowrap}.preview-grid>.cb-card{padding:21px}.preview-legal{padding:20px}}'''
    javascript=r'''function navigate(){let route=location.hash.replace('#','')||'dashboard';if(!document.getElementById(route))route='dashboard';document.querySelectorAll('.preview-page').forEach(p=>p.classList.toggle('active',p.id===route));document.querySelectorAll('[data-nav]').forEach(n=>{n.classList.toggle('active',n.dataset.nav===route);if(n.dataset.nav===route)n.setAttribute('aria-current','page');else n.removeAttribute('aria-current')});document.querySelector('.preview-sidebar').classList.remove('open');document.title=(route==='dashboard'?'Academic overview':route.charAt(0).toUpperCase()+route.slice(1))+' | Coursebook preview';window.scrollTo(0,0)}
window.addEventListener('hashchange',navigate);navigate();
document.getElementById('menu-toggle').addEventListener('click',()=>document.querySelector('.preview-sidebar').classList.toggle('open'));
function filter(entity){let search=document.querySelector('[data-search="'+entity+'"]').value.toLowerCase().trim();let status=document.querySelector('[data-filter="'+entity+'"]').value;let count=0;document.querySelectorAll('[data-table="'+entity+'"] tr[data-record]').forEach(row=>{let visible=row.textContent.toLowerCase().includes(search)&&(!status||row.dataset.status===status);row.style.display=visible?'':'none';if(visible)count++});document.querySelector('[data-count="'+entity+'"]').textContent=count+' matching sample record(s)'}
document.querySelectorAll('[data-search]').forEach(input=>input.addEventListener('input',()=>filter(input.dataset.search)));
document.querySelectorAll('[data-filter]').forEach(input=>input.addEventListener('change',()=>filter(input.dataset.filter)));
function report(id){document.querySelectorAll('[data-report]').forEach(button=>button.classList.toggle('selected',button.dataset.report===id));document.querySelectorAll('[data-panel]').forEach(panel=>panel.classList.toggle('active',panel.dataset.panel===id))}document.querySelectorAll('[data-report]').forEach(button=>button.addEventListener('click',()=>report(button.dataset.report)));report('BR-01');
document.querySelectorAll('[data-export]').forEach(button=>button.addEventListener('click',()=>{let table=document.querySelector('[data-table="'+button.dataset.export+'"] table');let lines=[...table.querySelectorAll('tr')].filter(row=>row.style.display!=='none').map(row=>[...row.children].map(cell=>{let value=cell.textContent.trim();if(/^[=+\-@]/.test(value))value="'"+value;return '"'+value.replaceAll('"','""')+'"'}).join(','));let blob=new Blob(['\uFEFF'+lines.join('\n')],{type:'text/csv;charset=utf-8'});let url=URL.createObjectURL(blob);let link=document.createElement('a');link.href=url;link.download='sample-'+button.dataset.export+'.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}));'''
    javascript=javascript.replace("'\\uFEFF'","'\uFEFF'").replace("join('\\n')","join('\n')")
    favicon=(ROOT/"assets/favicon.svg").read_text()
    import base64
    icon_data=base64.b64encode(favicon.encode()).decode()
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Coursebook | Interface preview</title><link rel="icon" href="data:image/svg+xml;base64,{icon_data}"><style>{stylesheet}\n{extra_css}</style></head><body>
    <aside class="preview-sidebar">{brand_html()}<div class="cb-sidebar-section">WORKSPACE</div><nav class="preview-nav" aria-label="Main navigation">{links}</nav><div class="cb-sidebar-note"><strong>Read-only interface preview</strong><p>Browse the sample records here. Run the Streamlit application to connect to MySQL and edit records.</p></div><nav class="preview-legal-nav"><a href="#terms">Terms &amp; Conditions</a><a href="#privacy">Privacy policy</a><span style="color:#79947e;font-size:10px">Coursebook / v1.0</span></nav></aside>
    <main class="preview-main"><button id="menu-toggle" class="preview-button">Menu</button><div class="cb-topline"><strong>Learning &amp; Training Institute</strong><span>READ-ONLY INTERFACE PREVIEW</span></div><div class="cb-data-note"><strong>Fictional sample dataset</strong>This preview is not connected to MySQL. Figures are calculated from the supplied training records.</div>{''.join(pages)}<footer class="cb-footer">Coursebook / Academic records workspace<br>Interface design preview. The working application starts with <code>python -m streamlit run app.py</code>.</footer></main><script>{javascript}</script></body></html>'''
    (ROOT/"application_preview.html").write_text(html,encoding="utf-8")
    db.close()
    print(ROOT/"application_preview.html")


if __name__=="__main__":main()
