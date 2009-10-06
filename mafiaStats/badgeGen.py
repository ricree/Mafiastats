import Image,ImageFont,ImageDraw
import pyggy
import os
import logging
#from django.conf import settings


if __name__ == "__main__":
	class FakeSettings(object):
		FONT_DIRECTORY = "/usr/share/fonts/truetype/ttf-dejavu/"
		MEDIA_ROOT = '/home/rareed/projects/Mafiastats/static'
		SITE_ROOT = '/home/rareed/projects/Mafiastats'
	settings = FakeSettings()
	import sys
	sys.path+=[settings.SITE_ROOT]
else:
	from django.conf import settings

LOGGING_FILE = settings.SITE_ROOT + '/debug_log'
logging.basicConfig(filename=LOGGING_FILE,level=logging.ERROR)
LINE_SPACE=3
HBORDER = 10
fontBase = settings.FONT_DIRECTORY
fontDirs = {'BOLD':fontBase+'DejaVuSans-Bold.ttf','ITALIC':fontBase + 'DejaVuSansCondensed-Oblique.ttf','NORMAL':fontBase + 'DejaVuSans.ttf'}
baseDefaults ={'background':'gradient', 'colors':['#010085','#1b5af6'],'text_color':'#FFFFFF','size':10,'weight':'NORMAL'}
defaultSize = 10



#####
#Callbacks for getting user stats
#
def sumStat(user,players,stat):
	def getField(user,players,stat):
		for p in players.all():
			if hasattr(p,stat):
				attr = getattr(p,stat)
				if hasattr(attr,'__call__'):
					yield attr()
				else:
					yield attr
	return sum(getField(user,players,stat))
	


######
#Code to parse the format string
#
def findSym(node,stack,sym,all=None):
	"""does a bfs on the tree until it finds a node whose sym is sym"""
	if((type(node.sym)== tuple) and (node.sym[0] == sym)):
		retval =  node
	elif (node.sym == sym):
		retval =  node
	else:
		 retval = []
	if len(node.possibilities)>0:
		stack.extend(node.possibilities[0].elements)
	if len(stack)<1:
		if all and retval:
			return [retval]
		else:
			return retval
	next = stack[0]
	del stack[0]
	if all:
		if retval:
			retval = [retval] 
		return findSym(next,stack,sym,all=all)+retval
	else:
		if retval:
			return retval
		else:
			return findSym(next,stack,sym)
def replaceIf(dict,key,val,index):
	if val:
		if type(val) is list:
			print val
			dict[key]= [(v.sym[index] if type(v.sym) is tuple else v.sym) for v in val]
		elif type(val.sym) is tuple:
			dict[key]=val.sym[index]
		else:
			dict[key]=val.possibilities[0].elements[0].sym
def buildBadgeData(node,fields):
	defaults = dict(baseDefaults)
	header = findSym(node,[],'HEADER')
	description = findSym(header,[],'DESCRIPTION')
	if header:
		if description:
			for key,field,index in [('size','SIZE',1),('weight','DECORATION',0),('text_color','COLOR',1)]:
				replaceIf(defaults,key,findSym(description,[],field),index)
		headerint = findSym(header,[],'HEADERINT')
		if headerint:
			replaceIf(defaults,'background',findSym(headerint,[],'BACKGROUND'),1)
			replaceIf(defaults,'colors',findSym(headerint,[],'COLOR',all=True),1)
	defaults['lines'] = buildStack(node,fields,defaults)
	return defaults

def buildStack(node,fields,defaults):
	if (node.sym == 'TOKEN'):
		return pushToken(node,fields,defaults)
	if(node.sym == 'STRINGP'):
		return pushString(node,defaults)
	retval = []
	if len(node.possibilities)<1:
		return None
	for n in node.possibilities[0].elements:
		r = buildStack(n,fields,defaults)
		if r:
			if (node.sym == "LINE"):
				retval.append(r)
			else:
				retval.extend(r)
	return retval

def pushToken(node,fields,defaults):
	field = findSym(node,[],'FIELD').possibilities[0].elements[0].sym[0]
	dec = findSym(node,[],'DECORATION')
	size = findSym(node,[],'SIZE')
	color = findSym(node,[],'COLOR')
	rel = findSym(node,[],"RELSIZE")
	if rel:
		rel = int(rel.sym[1])
	else:
		rel = 0
	if color:
		color = color.sym[1]
	else:
		color = defaults['text_color']
	if size:
		size = int(size.sym[1])
	else:
		size= defaults['size']
	size += rel
	if dec:
		font = ImageFont.truetype(fontDirs[dec.possibilities[0].elements[0].sym[0]],int(size))
	else:
		font = ImageFont.truetype(fontDirs[defaults['weight']],int(size))
	return [(str(fields[field]),font,color)]

def pushString(node,defaults):
	s = findSym(node,[],'STRING').sym[1]
	dec = findSym(node,[],'DECORATION')
	size = findSym(node,[],'SIZE')
	color = findSym(node,[],'COLOR')
	rel = findSym(node,[],'RELSIZE')
	if color:
		color = color.sym[1]
	else:
		color = defaults['text_color']
	if rel:
		rel = int(rel.sym[1])
	else:
		rel = 0
	if size:
		size = int(size.sym[1])
	else:
		size= defaults['size']
	size += rel
	if dec:
		font = ImageFont.truetype(fontDirs[dec.possibilities[0].elements[0].sym[0]],int(size))
	else:
		font = ImageFont.truetype(fontDirs[defaults['weight']],int(size))
	return [(s,font,color)]
def sizeLine(line):
	width,height = zip(*(font.getsize(text) for text,font,color in line))
	return (sum(width),max(height))

def buildGradient(size,colors):
	mask = Image.open(settings.MEDIA_ROOT + "/images/gradient_mask.png").resize(size)
	base_mask = Image.open(settings.MEDIA_ROOT + "/images/badgeMask.png").resize(size)
	bottom = Image.new("RGB",size,colors[1])
	top= Image.new("RGB",size,colors[0])
	img = Image.new("RGB",size)
	img.putalpha(0)
	img.paste(bottom,(0,0)+size,base_mask)
	img.paste(top,(0,0)+size,mask)
	return img

def buildTransparent(size,colors):
	img = Image.new("RGB",size)
	img.putalpha(0)
	return img


def build_badge(badge):
	#pyggy uses a hackish way of loading the generated lexer.
	#and the .pyl and .pyg seem to have to be in the current directory
	bgGens = {'gradient':buildGradient,'transparent':buildTransparent}
	startDir = os.getcwd()
	os.chdir(settings.SITE_ROOT)
	print os.getcwd()
	r = settings.SITE_ROOT
	l,ltab=  pyggy.getlexer("badge.pyl")
	parser,ptab = pyggy.getparser("badge.pyg")
	print badge.format
	fmt = badge.format
	l.setinputstr(fmt)
	while True:
		x = l.token()
		if x is None:
			break
		print x,l.value
	l.setinputstr(badge.format)
	parser.setlexer(l)
	tree = parser.parse()
	os.chdir(startDir)
	sstat = lambda stat:sumStat(badge.user,badge.players,stat)
	fields = {'WINS':sstat('wins'),'LOSSES':sstat('losses'),'TOTAL':sstat('played'),'MODERATED':sstat('modded'),'NAME':badge.user.username,'PMODERATED':sstat('totalPlayersModded')}
	badgeData = buildBadgeData(tree,fields)
	lines = badgeData['lines']
	print badgeData
	sizes = [sizeLine(line) for line in lines]
	zsizes = zip(*sizes)
	width = 2*HBORDER + max(zsizes[0])
	height = LINE_SPACE + sum((LINE_SPACE + h for h in zsizes[1]))
	base = Image.open(settings.MEDIA_ROOT + "/images/badgeBase.png").resize((width,height))
	mask = Image.open(settings.MEDIA_ROOT + "/images/badgeMask.png").resize((width,height),Image.ANTIALIAS)
	print "Background: ", badgeData['background']
	img = bgGens[badgeData['background']]((width,height),badgeData['colors'])
#	img = Image.new("RGB",(width,height))
#	img.putalpha(0)
#	img.paste(base,(0,0,width,height),mask)
	d = ImageDraw.Draw(img)
	cur_y = LINE_SPACE
	for line,size in zip(lines,sizes):
		cur_x = HBORDER
		for text,font,color in line:
			entry_size = font.getsize(text)
			line_offset = size[1] - entry_size[1]
			d.text((cur_x,cur_y+line_offset),text,font=font,fill=color)
			cur_x+=entry_size[0]
		cur_y+=size[1]+LINE_SPACE
	print badge.url
	img.save(settings.MEDIA_ROOT +"/"+ badge.url)
class PlayerHarness(object):
	def __init__(self,site,name):
		self.name = name
		self.site = site
	def wins(self):
		return 3
	moderated = 2
	losses = 1
	played = 5

class UserHarness(object):
	class Fake(object):
		def all(self):
			return [PlayerHarness(1,'ricree'),PlayerHarness(2,'ricree')]
	players = Fake()
	username = 'ricree'

class BadgeHarness(object):
	class FakePlayers(object):
		def all(self):
			return [PlayerHarness(1,'ricree')]
	user = UserHarness()
#	format = "( )%nb18\n(Mafia Stats )i14%w14( Wins in )14%t14( Games)14\n"
#	format = "Test\n(Mafia Stats: )12b%w Wins\n"
	format = "Test %nb\n"
	players =FakePlayers()
	url = "/images/test.png"

if __name__ == '__main__':
	build_badge(BadgeHarness())
