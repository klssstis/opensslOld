import os
import requests
import time
import re
import csv
import datetime

folderName = '/tmp/works/'
gitUrl = 'https://github.com/openssl/openssl'
fileTagList = '/tmp/listTag'
os.system('rm -rm '+folderName)
os.system("git clone "+gitUrl+' '+folderName)
os.system('cd '+folderName+'&&git tag -l>>'+fileTagList)

tagTover = dict()
with open(fileTagList,'r') as file:
    for line in file:
        line1 = line.lower()        
        if not 'openssl' in line1 or 'openssl-fips' in line1 or 'openssl-engine' in line1:
            continue
        if 'openssl_' in line1:
            line1 = line1.replace('openssl_','openssl-')
        if '_' in line1:
            line1 = line1.replace('_','.')
        tagTover[line.splitlines()[0]]=line1.splitlines()[0]


def checkCPE(vendor,product,version,update,edition):
    urlCPE='https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:a:'+vendor+':'+product+':'+version+':'+update+':'+edition+':*:*:*:*:*'
    count = 20
    while True:
        count -=1
        if count==0:
            break
        time.sleep(13)
        r = requests.get(urlCPE)
        if r.status_code==200:
            return r
        else:
            print(r.status_code)
    return False

verTocve = dict()
cveTofun = dict()
for vi in tagTover.keys():
    vendor = 'openssl'
    edition = '*'
    product = tagTover[vi].split('-')[0]
    version = tagTover[vi].split('-')[1]
    if not tagTover[vi].endswith(version):
        update = tagTover[vi].split(version)[1][1:]
    else:
        update = '-'
    a = checkCPE('openssl',product,version,update,'*')
    if a==False:
        continue
    else:
        r = a
    for i in r.json()['vulnerabilities']:
        m = re.findall('[^\s]+\(\)', str(i))
        if tagTover[vi] in verTocve:
            if not i['cve']['id'] in verTocve[tagTover[vi]]:
                verTocve[tagTover[vi]].append(i['cve']['id'])
        else:
            verTocve[tagTover[vi]] = [i['cve']['id']]
        if len(m)==0:
            cveTofun[i['cve']['id']] = list()
            continue
        for j in range(len(m)):
            if '\\n' in m[j]:
                m[j]=m[j].split('\\n')[1]
            if '`' in m[j]:
                m[j]=m[j].split('`')[1]                
            if '()' in m[j]:
                m[j]=m[j].split('()')[0]
        if i['cve']['id'] in cveTofun:
            cveTofun[i['cve']['id']] = list(set(cveTofun[i['cve']['id']]).union(set(m)))
        else:
            cveTofun[i['cve']['id']] = list(set(m))


    a = checkCPE('openssl',product,version,"*",'*')
    if a==False:
        continue
    else:
        r = a
    for i in r.json()['vulnerabilities']:
        m = re.findall('[^\s]+\(\)', str(i))
        if tagTover[vi] in verTocve:
            if not i['cve']['id'] in verTocve[tagTover[vi]]:
                verTocve[tagTover[vi]].append(i['cve']['id'])
        else:
            verTocve[tagTover[vi]] = [i['cve']['id']]
        if len(m)==0:
            cveTofun[i['cve']['id']] = list()
            continue
        for j in range(len(m)):
            if '\\n' in m[j]:
                m[j]=m[j].split('\\n')[1]
            if '`' in m[j]:
                m[j]=m[j].split('`')[1]                
            if '()' in m[j]:
                m[j]=m[j].split('()')[0]
        if i['cve']['id'] in cveTofun:
            cveTofun[i['cve']['id']] = list(set(cveTofun[i['cve']['id']]).union(set(m)))
        else:
            cveTofun[i['cve']['id']] = list(set(m))


t = datetime.datetime.today()

fileOutdate = './results/'+t.strftime('%Y%m%d')+'.csv'
fileOutup = './results/now.csv'
with open(fileOutdate, "w") as fp:
    writer = csv.writer(fp, delimiter=",")
    writer.writerow(["tag", "version", "cve", "function"])
    for vi in tagTover:
        for ci in verTocve[tagTover[vi]]:
            if len(cveTofun[ci]) >0 :
                for fi in cveTofun[ci]:
                    writer.writerow([vi,tagTover[vi],ci,fi])
os.system('cp '+fileOutdate+' '+fileOutup)
