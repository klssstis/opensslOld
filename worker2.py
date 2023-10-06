import csv
import os
import requests

try:
    token = sys.argv[1]
except IndexError:
    print("not all parameters")
    os._exit(0)

os.system('apt-get update&& apt-get install -y python3-pip python3-setuptools python3-pandas python3-yaml python3-requests&& apt-get install -y git curl psmisc p7zip-full wget')
os.system('apt-get install -y gh')
dataVersion = requests.get('https://github.com/github/codeql-cli-binaries/releases/latest')
dataVerIns = dataVersion.text.split('<title>Release v')[1].split(' · github/codeql-cli-binaries')[0]

os.system("cd /opt/&&sudo mkdir codeqlmy&&cd codeqlmy&&sudo git clone https://github.com/github/codeql.git codeql-repo")
os.system("cd /opt/codeqlmy&&sudo wget https://github.com/github/codeql-cli-binaries/releases/download/v"+dataVerIns+"/codeql-linux64.zip&&sudo unzip codeql-linux64.zip&&sudo rm codeql-linux64.zip")

fileTagList = '/tmp/listTag'
fileOutup = './results/now.csv'
folderName = '/tmp/works/'
folderNameDB = '/tmp/worksDB/'
resultFile = '/tmp/1.csv'
prebuildLine = './config'
foldDBtmp = '/tmp/dbtmp/'

os.system('git tag -l>>'+fileTagList)

os.system('rm -rm '+folderName)
os.system("git clone https://github.com/openssl/openssl.git "+folderName)
os.system('rm -rm '+folderNameDB)
os.system("git clone https://github.com/openssl/openssl.git "+folderNameDB)

def readCSV(fileName):
    with open(fileName) as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        data_read = [row for row in reader]
    return data_read
workList = readCSV(fileOutup)
workList.pop(0)

with open(fileTagList) as f:
    listTags = f.read().splitlines()

def createDBcodeql(folderName,gitCommit,prebuildLine,foldDBtmp):
    fileExitCode = '/tmp/check123'
#    os.system('cd '+folderName+'&&git clean  -d  -f .')
    os.system('cd '+folderName+'&&git checkout '+gitCommit)
    os.system('cd '+folderName+'&&'+prebuildLine)
    os.system('rm -rf '+foldDBtmp)
    os.system("rm -rf "+folderName+"_lgtm*")
    os.system("sudo echo 321 > "+fileExitCode)
    os.system("timeout 60m /opt/codeqlmy/codeql/codeql database create --language=cpp --source-root="+folderName+" -- "+foldDBtmp+" &&sudo echo $? > "+fileExitCode)
    echoCode = open(fileExitCode, 'r').read()
    if echoCode.startswith("0"):
        return True
    else:
        return False

def replTXT(fileName,funName):
    outFile = '/opt/codeqlmy/codeql-repo/cpp/ql/examples/snippets/1.ql'
    with open(fileName, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('bbbaaaddd', funName)
    os.system('rm -rf '+outFile)
    with open(outFile, 'w') as file:
        file.write(filedata)
def queryRun(foldDBtmp):
    os.system('rm -rf /tmp/1.bqrs')
    os.system('/opt/codeqlmy/codeql/codeql query run   --database='+foldDBtmp+' --output=/tmp/1.bqrs -- /opt/codeqlmy/codeql-repo/cpp/ql/examples/snippets/1.ql')
    os.system('rm -rf /tmp/1.csv')
    os.system('/opt/codeqlmy/codeql/codeql bqrs decode --output=/tmp/1.csv -- /tmp/1.bqrs')
    if os.path.exists('/tmp/1.csv'):
        return True
    else:
        return False
def insert(file, line, column, text):
    ln, cn = line - 1, column - 1         # offset from human index to Python index
    count = 0                             # initial count of characters
    with open(file, 'r+') as f:           # open file for reading an writing
        for idx, line in enumerate(f):    # for all line in the file
            if idx < ln:                  # before the given line
                count += len(line)        # read and count characters
            elif idx == ln:               # once at the line
                f.seek(count + cn)        # place cursor at the correct character location
                remainder = f.read()      # store all character afterwards
                f.seek(count + cn)        # move cursor back to the correct character location
                f.write(text + remainder) # insert text and rewrite the remainder
                return                    # You're finished!



nameDB = ''
for i in workList:
####
    if '0_9' in i[0]:
        continue
####
    if i[0]+'_'+i[2]+'_'+i[3] in listTags:
        continue
    if nameDB != i[0]:
        os.system('rm -rm '+folderNameDB)
        os.system("git clone https://github.com/openssl/openssl.git "+folderNameDB)
        if not createDBcodeql(folderNameDB,'tags/'+i[0],prebuildLine,foldDBtmp):
            print('bbbaaaddd: build error '+i[0])
            continue
        else:
            nameDB = i[0]
    os.system('rm -rm '+folderName)
    os.system("git clone https://github.com/openssl/openssl.git "+folderName)                
    os.system('cd '+folderName+'&&git checkout tags/'+i[0])
    replTXT('./results/1.ql',i[3])
    if queryRun(foldDBtmp)==True:
        tmpCSV = readCSV(resultFile)
        if len(tmpCSV)>2:
            resQL=tmpCSV[2][0].split('|')[2].split('file://')[1].split(':')
            insert(resQL[0].replace(folderNameDB,folderName), int(resQL[1]), int(resQL[2])+1, 'while(1){}')
            os.system('zip -r /tmp/'+i[0]+'_'+i[2]+'_'+i[3]+'.zip '+folderName)
            os.system('echo '+token+'| gh auth login -h github.com --with-token')
            os.system('gh release create '+i[0]+'_'+i[2]+'_'+i[3]+' --notes \"insert while(1){}\" \''+'/tmp/'+i[0]+'_'+i[2]+'_'+i[3]+'.zip#download\'')
