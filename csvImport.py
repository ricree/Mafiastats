from Mafiastats.mafiaStats.models import Site,Category,Player,Team,Game
import csv
import datetime
import re

categoryNames = {'Town':'T','Mafia':'M','Survivor':'Su','Serial Killer':'SK','Cult':'C','Other':'O'}



csvColumns = {'GName':1,'TWin':2,'TLoss':3,'MWin':4,'MLoss':5,'SuWin':6,'SuLoss':7,'SKWin':8,'SKLoss':9,'CWin':10,'CLoss':11,'OWin':12,'OLoss':13,'Type':14,'SDate':17,'EDate':18,'Mod':19}

dateFormat = "%m/%d/%Y"

optFields = ['url','description']

def cleanNameString(name):
	return name.replace(' ','').lower()

def getNames(nameString):
	ns = cleanNameString(nameString)
	retval =  ns.split(',')
	retval = [st for st in retval if st !='']
	return retval

def normLength(lists):
	maxLen=0
	for line in lists:
		maxLen = maxLen if (len(line) < maxLen) else len(line)
	counter=0
	for line in lists:
		diff = maxLen - len(line)
		lists[counter] = lists[counter]+['']*diff
		counter+=1
	return lists	


def makeTeam(game,dline,category,prefix,site):
	cat = Category.objects.get(title=category)
	for suff,title,won in [('Win',' Winners',True),('Loss',' Losers',False)]:
		players = getNames(dline[prefix+suff])
		if players:
			team,created = Team.objects.get_or_create(title=(category+title),game=game,site=site,defaults={'won':won,'category':cat})
			team.save()
			for pName in players:
				p,created = Player.objects.get_or_create(name=pName,site=site)
				if created:
					p.save()
				team.players.add(p)
				team.save()

def importCsv(siteDetails,fileName):
	for k in optFields:
		if not(k in siteDetails):
			siteDetails[k] = ''
	for cat in categoryNames.keys():
		categ,created = Category.objects.get_or_create(title=cat)
		if created:
			categ.save()
	(site,created) = Site.objects.get_or_create(title=siteDetails['title'],defaults={'url':siteDetails['url'],'description':siteDetails['description']})
	site.save()
	with open(fileName) as cFile:
		reader = csv.reader(cFile)
		reader.next()#skip col titles
		reader.next()
		data = normLength([line for line in reader])
		for line in data:
			dln = dict(((n,line[csvColumns[n]]) for n in csvColumns.keys()))
			start=datetime.datetime.strptime(dln['SDate'],dateFormat).date()
			end = datetime.datetime.strptime(dln['EDate'],dateFormat).date()
			modName = cleanNameString(dln['Mod'])
			moderator,created = Player.objects.get_or_create(name=modName,site=site)
			if(created):
				moderator.save()
			game,created = Game.objects.get_or_create(title=dln['GName'],defaults={'url':'','moderator':moderator,'start_date':start,'end_date':end,'gameType':dln['Type'],'site':site})
			game.save()
			for category in categoryNames:
				prefix=categoryNames[category]
				makeTeam(game,dln,category,prefix,site)
			print "Added %s, modded by %s" %(dln['GName'],modName)
