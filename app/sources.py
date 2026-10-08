COUNTRIES={'AUT':'Austria','BEL':'Belgium','BGR':'Bulgaria','CZE':'Czechia','DEU':'Germany','ESP':'Spain','EST':'Estonia','FRA':'France','HRV':'Croatia','HUN':'Hungary','ITA':'Italy','LTU':'Lithuania','LVA':'Latvia','NLD':'Netherlands','POL':'Poland','PRT':'Portugal','ROU':'Romania','SVK':'Slovakia','SVN':'Slovenia','SWE':'Sweden','UKR':'Ukraine'}
DIRECT={'DEU':'germany','UKR':'prozorro'}
# Poland remains selectable and is covered by TED; direct BZP is paused because its WAF blocks the deployment host.
def plan(countries):
 c=set(countries);out=[];eu=sorted(c-{'UKR'})
 if eu:out.append(('ted',eu))
 if 'UKR' in c:out.append(('prozorro',['UKR']))
 if 'DEU' in c:out.append(('germany',['DEU']))
 return out
