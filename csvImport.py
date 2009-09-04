from Mafiastats.mafiaStats.models import Site,Category,Player,Team,Game
import csv
import datetime
import re

categoryNames = {'Town':'T','Mafia':'M','Survivor':'Su','Serial Killer':'SK','Cult':'C','Other':'O'}


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
	for suff,title,won in [('Win','Winning ',True),('Loss','Losing ',False)]:
		players = getNames(dline[prefix+suff])
		if players:
			team,created = Team.objects.get_or_create(title=(title+category),game=game,site=site,defaults={'won':won,'category':cat})
			team.save()
			for pName in players:
				p,created = Player.objects.get_or_create(name=pName,site=site,defaults={'firstGame':game,'lastGame':game})
				if created:
					p.save()
				p.updateDates(game)
				team.players.add(p)
				team.save()

def importCsv(siteDetails,fileName,csvColumns):
	for k in optFields:
		if not(k in siteDetails):
			siteDetails[k] = ''
	for cat in categoryNames.keys():
		categ,created = Category.objects.get_or_create(title=cat)
		if created:
			categ.save()
	(site,created) = Site.objects.get_or_create(title=siteDetails['title'],defaults={'url':siteDetails['url'],'description':siteDetails['description'],'shortName':siteDetails['shortName']})
	site.save()
	with open(fileName) as cFile:
		reader = csv.reader(cFile)
		reader.next()#skip col titles
		reader.next()#and counts
		data = normLength([line for line in reader])
		for line in data:
			dln = dict(((n,line[csvColumns[n]]) for n in csvColumns.keys()))
			start=datetime.datetime.strptime(dln['SDate'],dateFormat).date()
			end = datetime.datetime.strptime(dln['EDate'],dateFormat).date()
			modName = cleanNameString(dln['Mod'])
			moderator,created = Player.objects.get_or_create(name=modName,site=site)
			if(created):
				moderator.save()
			game,gCreated = Game.objects.get_or_create(title=dln['GName'],defaults={'start_date':start,'end_date':end,'moderator':moderator,'gameType':dln['Type'],'site':site,'url':dln['url']})
			if(created):
				game.save()
			for category in categoryNames:
				prefix=categoryNames[category]
				makeTeam(game,dln,category,prefix,site)
			for pName in getNames(dln['lToEnd']):
				player,created = Player.objects.get_or_create(name=pName,site=site)
				if(created):
					player.save()
				player.updateDates(game)
				game.livedToEnd.add(player)
			game.save()
			print "Added %s, modded by %s to %s" %(dln['GName'],modName,siteDetails['title'])
