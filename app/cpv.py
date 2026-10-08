import json
from pathlib import Path
PATH=Path('data/cpv.json')
def load():
 try:return json.loads(PATH.read_text())
 except:return []
def save(rows):PATH.write_text(json.dumps(rows,ensure_ascii=False,indent=2))
def active_codes():return [x['code'] for x in load() if x.get('active')]
