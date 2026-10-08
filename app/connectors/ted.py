from datetime import datetime,timedelta
import httpx
from app.core import Tender
from app.cpv import active_codes
URL='https://api.ted.europa.eu/v3/notices/search';LANGS=('eng','en','pol','ukr','uk','spa','deu','fra','ita')
def first(v):
 if isinstance(v,dict):
  for k in LANGS:
   if v.get(k):return first(v[k])
  return first(next(iter(v.values()),''))
 if isinstance(v,list):return first(v[0]) if v else ''
 return str(v or '')
def dt(v):
 try:return datetime.fromisoformat(first(v)[:10])
 except:return None
def flat(v):
 if isinstance(v,list):return [first(x) for x in v]
 return [first(v)] if v else []
async def fetch(countries=None,limit=150):
 now=datetime.utcnow();cut=(now-timedelta(days=90)).strftime('%Y%m%d');codes=active_codes();cpv=' OR '.join(f'classification-cpv={c}' for c in codes);terms='FT~"SSD" OR FT~"NVMe" OR FT~"DDR4" OR FT~"DDR5" OR FT~"memory card" OR FT~"flash drive"';q=f'({terms} OR {cpv}) AND PD>={cut} SORT BY publication-date DESC'
 fields=['publication-number','notice-title','buyer-name','buyer-country','publication-date','deadline','description-proc','form-type','classification-cpv','total-value','total-value-cur'];payload={'query':q,'fields':fields,'page':1,'limit':limit,'scope':'ACTIVE','paginationMode':'PAGE_NUMBER','onlyLatestVersions':True}
 async with httpx.AsyncClient(timeout=50) as c:r=await c.post(URL,json=payload)
 if r.status_code!=200:raise RuntimeError(f'TED HTTP {r.status_code}: {r.text[:800]}')
 out=[]
 for x in r.json().get('notices',[]):
  co=first(x.get('buyer-country'))[:3] or 'EU';ddl=dt(x.get('deadline'));form=first(x.get('form-type')).lower()
  if countries and co not in countries or not ddl or ddl<now or any(z in form for z in ('result','award','completion')):continue
  n=first(x.get('publication-number'));url=f'https://ted.europa.eu/en/notice/-/detail/{n}'
  out.append(Tender('ted:'+n,'ted',co,first(x.get('notice-title')) or n,first(x.get('buyer-name')),deadline=ddl,published=dt(x.get('publication-date')),url=url,description_original=first(x.get('description-proc')),procurement_id=n,cpv=flat(x.get('classification-cpv')),source_language='multilingual'))
 return out
