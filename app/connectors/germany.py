import io,json,zipfile,httpx
from datetime import date,datetime,timedelta
from app.core import Tender
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(countries=None,days=3):
 out=[];now=datetime.utcnow()
 async with httpx.AsyncClient(timeout=65) as c:
  for i in range(1,days+1):
   day=(date.today()-timedelta(days=i)).isoformat();r=await c.get('https://oeffentlichevergabe.de/api/notice-exports',params={'pubDay':day,'format':'ocds.zip'})
   if r.status_code in (400,404):continue
   r.raise_for_status()
   with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    for fn in z.namelist():
     rel=(json.loads(z.read(fn)).get('releases') or [{}])[0];t=rel.get('tender') or {};ddl=dt((t.get('tenderPeriod') or {}).get('endDate'))
     if not ddl or ddl<now:continue
     ps=rel.get('parties') or [];buyer=next((p.get('name','') for p in ps if 'buyer' in p.get('roles',[])),'');ocid=rel.get('ocid') or rel.get('id') or fn;items=t.get('items') or [];cpv=[i.get('classification',{}).get('id','') for i in items if i.get('classification')];url=f'https://oeffentlichevergabe.de/ui/de/notices/{ocid}'
     out.append(Tender('de:'+ocid,'germany','DEU',t.get('title') or ocid,buyer,(t.get('value') or {}).get('amount'),(t.get('value') or {}).get('currency','EUR'),ddl,dt(rel.get('date')),t.get('status','active'),url,t.get('description',''),ocid,cpv,'de'))
 return out
