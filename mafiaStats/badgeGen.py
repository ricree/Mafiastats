import Image,ImageFont,ImageDraw
import pyggy
#from django.conf import settings
if __name__ == "__main__":
	class FakeSettings(object):
		FONT_DIRECTORY = "/usr/share/fonts/truetype/ttf-dejavu/"
		MEDIA_ROOT = '/home/rareed/projects/Mafiastats/static'
	settings = FakeSettings()
else:
	from django.conf import settings

LINE_SPACE=3
HBORDER = 10
fontBase = settings.FONT_DIRECTORY
fontDirs = {'BOLD':fontBase+'DejaVuSans-Bold.ttf','ITALIC':fontBase + 'DejaVuSansCondensed-Oblique.ttf','NORMAL':fontBase + 'DejaVuSans.ttf'}
defaultSize = 10



#####
#Callbacks for getting user stats
#
def sumStat(user,sites,stat):
	def getField(user,sites,stat):
		for p in user.players.all():
			if p.site in sites:
				if hasattr(p,stat):
					attr = getattr(p,stat)
					if hasattr(attr,'__call__'):
						yield attr()
					else:
						yield attr
	return sum(getField(user,sites,stat))
	


######
#Code to parse the format string
#
def findSym(node,stack,sym):
	"""does a bfs on the tree until it finds a node whose sym is sym"""
	if((type(node.sym)== tuple) and (node.sym[0] == sym)):
		return node
	elif (node.sym == sym):
		return node
	if len(node.possibilities)>0:
		stack.extend(node.possibilities[0].elements)
	if len(stack)<1:
		return None
	next = stack[0]
	del stack[0]
	return findSym(stack[0],stack,sym)

def buildStack(node,fields):
	if (node.sym == 'TOKEN'):
		return pushToken(node,fields)
	if(node.sym == 'STRINGP'):
		return pushString(node)
	retval = []
	if len(node.possibilities)<1:
		return None
	for n in node.possibilities[0].elements:
		r = buildStack(n,fields)
		if r:
			if (node.sym == "LINE"):
				retval.append(r)
			else:
				retval.extend(r)
	return retval

def pushToken(node,fields):
	field = node.possibilities[0].elements[0].possibilities[0].elements[0].sym[0]
	dec = findSym(node,[],'DECORATION').possibilities[0].elements[0].sym[0]
	size = findSym(node,[],'SIZET').possibilities[0].elements[0]
	if size.sym[0] == 'SIZE':
		size = size.sym[1]
	else:
		size= defaultSize
	font = ImageFont.truetype(fontDirs[dec],int(size))
	return [(str(fields[field]),font)]

def pushString(node):
	s = findSym(node,[],'STRING').sym[1]
	dec = findSym(node,[],'DECORATION').possibilities[0].elements[0].sym[0]
	size = findSym(node,[],'SIZET').possibilities[0].elements[0]
	if size.sym[0] == 'SIZE':
		size = size.sym[1]
	else:
		size= defaultSize
	font = ImageFont.truetype(fontDirs[dec],int(size))
	return [(s,font)]
def sizeLine(line):
	width,height = zip(*(font.getsize(text) for text,font in line))
	return (sum(width),max(height))

def build_badge(badge):
	l,ltab=  pyggy.getlexer("badge.pyl")
	parser,ptab = pyggy.getparser("badge.pyg")
	print badge.format
	l.setinputstr(badge.format)
	parser.setlexer(l)
	tree = parser.parse()
	sstat = lambda stat:sumStat(badge.user,badge.sites.all(),stat)
	fields = {'WINS':sstat('wins'),'LOSSES':sstat('losses'),'TOTAL':sstat('played'),'MODERATED':sstat('modded'),'NAME':badge.user.username}
	lines = buildStack(tree,fields)
	print lines
	sizes = [sizeLine(line) for line in lines]
	zsizes = zip(*sizes)
	width = 2*HBORDER + max(zsizes[0])
	height = LINE_SPACE + sum((LINE_SPACE + h for h in zsizes[1]))
	base = Image.open(settings.MEDIA_ROOT + "/images/badgeBase.png").resize((width,height))
	mask = Image.open(settings.MEDIA_ROOT + "/images/badgeMask.png").resize((width,height),Image.ANTIALIAS)
	img = Image.new("RGB",(width,height))
	img.putalpha(0)
	img.paste(base,(0,0,width,height),mask)
	d = ImageDraw.Draw(img)
	cur_y = LINE_SPACE
	for line,size in zip(lines,sizes):
		cur_x = HBORDER
		for text,font in line:
			d.text((cur_x,cur_y),text,font=font,fill="white")
			cur_x+=font.getsize(text)[0]
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
	user = UserHarness()
	format = "( )%nb18\n(Mafia Stats )i14%w14( Wins in )14%t14( Games)14\n"
	sites = [1,2]
	url = "/images/test.png"

if __name__ == '__main__':
	build_badge(BadgeHarness())
