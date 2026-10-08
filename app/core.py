from dataclasses import dataclass,field
from datetime import datetime
from collections import Counter
@dataclass
class Tender:
 id:str;source:str;country:str;title_original:str;buyer:str='';value:float|None=None;currency:str='';deadline:datetime|None=None;published:datetime|None=None;status:str='active';url:str='';description_original:str='';procurement_id:str='';cpv:list[str]=field(default_factory=list);source_language:str='auto';translations:dict=field(default_factory=dict);source_links:dict=field(default_factory=dict)
 def title(self,lang):return self.translations.get(lang,{}).get('title') or self.title_original
 def description(self,lang):return self.translations.get(lang,{}).get('description') or self.description_original
class Store:
 def __init__(self):self.data={};self.runs=[];self.idx={}
 def add(self,src,rows):
  from app.dedupe import keys
  added=dupes=0
  for x in rows:
   x.source_links=x.source_links or ({src:x.url} if x.url else {});ks=keys(x);hit=next((self.idx[k] for k in ks if k in self.idx),None)
   if hit is None:
    self.data[x.id]=x;added+=1
    for k in ks:self.idx[k]=x.id
   else:
    old=self.data[hit];primary=x if x.source!='ted' and old.source=='ted' else old;primary.source_links={**old.source_links,**x.source_links};self.data[hit]=primary;dupes+=1
  self.runs.insert(0,{'source':src,'status':'ok','count':len(rows),'added':added,'duplicates':dupes,'error':''})
 def error(self,src,e):self.runs.insert(0,{'source':src,'status':'error','count':0,'added':0,'duplicates':0,'error':str(e)[:500]})
store=Store()
def is_active(x):return (x.status or '').lower() not in {'complete','completed','awarded','cancelled','closed'} and (not x.deadline or x.deadline>=datetime.utcnow())
def analytics(rows):
 countries=Counter(x.country for x in rows);sources=Counter(x.source for x in rows);cpv=Counter(c for x in rows for c in x.cpv);buyers=Counter(x.buyer for x in rows if x.buyer);days=Counter((x.published or x.deadline).strftime('%Y-%m-%d') for x in rows if x.published or x.deadline)
 return {'countries':countries,'sources':sources,'cpv':cpv,'buyers':buyers,'days':days}
