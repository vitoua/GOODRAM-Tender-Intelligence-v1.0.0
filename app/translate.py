import hashlib,httpx
from app.config import settings
CACHE={}
LANG={'uk':'uk','pl':'pl','en':'en','es':'es'}
async def translate_text(text,target):
 if not text or not settings.libretranslate_url:return text
 key=(hashlib.sha256(text.encode()).hexdigest(),target)
 if key in CACHE:return CACHE[key]
 payload={'q':text,'source':'auto','target':LANG[target],'format':'text'}
 if settings.libretranslate_api_key:payload['api_key']=settings.libretranslate_api_key
 try:
  async with httpx.AsyncClient(timeout=25) as c:r=await c.post(settings.libretranslate_url.rstrip('/')+'/translate',data=payload);r.raise_for_status();value=r.json()['translatedText']
  CACHE[key]=value;return value
 except:return text
async def ensure(rows,lang):
 for x in rows:
  if lang not in x.translations:x.translations[lang]={'title':await translate_text(x.title_original,lang),'description':await translate_text(x.description_original,lang)}
