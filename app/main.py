from datetime import datetime
import asyncio
from fastapi import FastAPI,Form,Request,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.core import store,is_active,analytics
from app.i18n import tr
from app.sources import COUNTRIES,plan
from app.cpv import load,save
from app.translate import ensure
app=FastAPI(version='1.0.0');app.mount('/static',StaticFiles(directory='app/static'),name='static');tpl=Jinja2Templates(directory='app/templates')
def lang(r):return r.cookies.get('lang') or settings.app_language
def ctx(r,x=None):return {'request':r,'t':tr(lang(r)),'lang':lang(r),**(x or {})}
@app.get('/health')
def health():return {'status':'ok','version':'1.0.0','tenders':len(store.data)}
@app.get('/lang/{code}')
def language(code,request:Request):
 r=RedirectResponse(request.headers.get('referer') or '/',303);r.set_cookie('lang',code if code in ('uk','pl','en','es') else 'uk');return r
@app.get('/')
async def home(request:Request,q:str='',country:str='',active_only:int=1):
 rows=[x for x in store.data.values() if (not active_only or is_active(x)) and (not country or x.country==country) and (not q or q.lower() in (x.title_original+x.buyer+x.description_original+' '.join(x.cpv)).lower())];rows.sort(key=lambda x:x.deadline or datetime.max);await ensure(rows,lang(request));return tpl.TemplateResponse('index.html',ctx(request,{'rows':rows,'runs':store.runs,'available':COUNTRIES,'countries':sorted({x.country for x in store.data.values()}),'q':q,'country':country,'active_only':active_only}))
@app.post('/refresh')
async def refresh(countries:list[str]=Form(default=[])):
 async def one(src,scope):
  try:
   if src=='ted':from app.connectors.ted import fetch
   elif src=='prozorro':from app.connectors.prozorro import fetch
   else:from app.connectors.germany import fetch
   return src,await asyncio.wait_for(fetch(scope),80),None
  except Exception as e:return src,[],e
 results=await asyncio.gather(*(one(a,b) for a,b in plan(countries or list(COUNTRIES))))
 for src,rows,error in results:store.error(src,error) if error else store.add(src,rows)
 return RedirectResponse('/',303)
@app.get('/tenders/{tid:path}')
async def detail(tid:str,request:Request,view:str='translated'):
 x=store.data.get(tid)
 if not x:raise HTTPException(404)
 await ensure([x],lang(request));return tpl.TemplateResponse('detail.html',ctx(request,{'x':x,'view':view}))
@app.get('/cpv')
def cpv_page(request:Request):return tpl.TemplateResponse('cpv.html',ctx(request,{'rows':load()}))
@app.post('/cpv/add')
def cpv_add(code:str=Form(),name:str=Form(),active:bool=Form(False)):
 rows=load();rows.append({'code':code.strip(),'name':name.strip(),'active':active});save(rows);return RedirectResponse('/cpv',303)
@app.post('/cpv/update')
def cpv_update(code:list[str]=Form(default=[]),name:list[str]=Form(default=[]),active:list[str]=Form(default=[])):
 enabled=set(active);save([{'code':c,'name':n,'active':c in enabled} for c,n in zip(code,name)]);return RedirectResponse('/cpv',303)
@app.get('/analytics')
def analytics_page(request:Request,country:str='',source:str='',date_from:str='',date_to:str=''):
 rows=list(store.data.values())
 if country:rows=[x for x in rows if x.country==country]
 if source:rows=[x for x in rows if x.source==source]
 if date_from:rows=[x for x in rows if (x.published or x.deadline) and (x.published or x.deadline).date()>=datetime.fromisoformat(date_from).date()]
 if date_to:rows=[x for x in rows if (x.published or x.deadline) and (x.published or x.deadline).date()<=datetime.fromisoformat(date_to).date()]
 a=analytics(rows);data={k:dict(v.most_common(12)) for k,v in a.items()};return tpl.TemplateResponse('analytics.html',ctx(request,{'data':data,'count':len(rows),'countries':sorted({x.country for x in store.data.values()}),'sources':sorted({x.source for x in store.data.values()}),'country':country,'source':source,'date_from':date_from,'date_to':date_to}))
@app.get('/sources')
def sources_page(request:Request):return tpl.TemplateResponse('sources.html',ctx(request,{'countries':COUNTRIES}))
