from datetime import datetime
import httpx
from app.core import Tender
B='https://public-api.prozorro.gov.ua/api/2.5/tenders'
def dt(v):
 try:return datetime.fromisoformat(str(v).replace('Z','+00:00')).replace(tzinfo=None)
 except:return None
async def fetch(countries=None,limit=35):
 out=[];now=datetime.utcnow()
 async with httpx.AsyncClient(timeout=50) as c:
  f=await c.get(B,params={'limit':limit,'descending':1});f.raise_for_status()
  for row in f.json().get('data',[]):
   r=await c.get(f"{B}/{row['id']}");r.raise_for_status();x=r.json().get('data',{});ddl=dt((x.get('tenderPeriod') or {}).get('endDate'))
   if not ddl or ddl<now:continue
   n=x.get('tenderID',row['id']);url=f'https://prozorro.gov.ua/tender/{n}';cpv=[i.get('classification',{}).get('id','') for i in x.get('items',[]) if i.get('classification')]
   out.append(Tender('prozorro:'+n,'prozorro','UKR',x.get('title') or n,(x.get('procuringEntity') or {}).get('name',''),(x.get('value') or {}).get('amount'),(x.get('value') or {}).get('currency',''),ddl,dt(x.get('dateModified')),x.get('status','active'),url,x.get('description',''),n,cpv,'uk'))
 return out
