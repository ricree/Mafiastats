from mafiaStats.models import Site,Game,Team,Category
from django.db.models.signals import post_save, post_delete,pre_save,pre_delete
from django.conf import settings
from django.core.cache import cache
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from signals import profile_link,profile_unlink
from badgeGen import build_badge
import Image,ImageDraw,ImageFont
import pyggy


def saveSiteStats(sender, **kwargs):
	inst = kwargs['instance']
	key = "site_saveSiteStats_%s"%inst.pk
	if sender is Game:
		site = inst.site
	else:
		site =inst
	cat_nums = [(cat.title,Team.objects.filter(site=site,category=cat,won=True).count()) for cat in Category.objects.all()]
	total = sum((c[1] for c in cat_nums))
	cache.set(key,{'cats':cat_nums,'total':total,'clean':False})

post_save.connect(saveSiteStats,sender=Game)
post_delete.connect(saveSiteStats,sender=Game)

def setColorBadge():
	normFont = settings.FONT_DIRECTORY + "DejaVuSans.ttf"
	boldFont = settings.FONT_DIRECTORY + "DejaVuSans-Bold.ttf"
	fontUname = ImageFont.truetype(boldFont,13)
	fontText = ImageFont.truetype(normFont,11)
	fontTitle = ImageFont.truetype(boldFont,11)
	base = Image.open(settings.MEDIA_ROOT+"/images/badgeBase.png")
	mask = Image.open(settings.MEDIA_ROOT + "/images/badgeMask.png")
	img = Image.new("RGB",base.size)
	img.putalpha(0)
	img.paste(base, (0,0)+base.size,mask)
	return (img,{'name':fontUname,'title':fontTitle,'text':fontText})
def buildColorBadgeForPlayer(player,image_base,fonts):
	img = image_base.copy()
	textString = "%s Wins In %s Games"
	drawing = ImageDraw.Draw(img)
	drawing.text((2,18),"Mafia Stats",font=fonts['title'],fill="white")
	drawing.text((5,2),player.name,font=fonts['name'],fill="white")
	drawing.text((84,18),textString%(player.wins(),player.playedCalc()),font=fonts['text'],fill="white")
	img.save(settings.MEDIA_ROOT+"/images/badges/badge_norm_%s_%s.png"%(player.site.id,player.id))


def buildColorBadge(sender, **kwargs):
	print 'badge start'
	inst = kwargs['instance']
	if sender is Game:
		players = inst.players()
	else:
		players = []
	img,fonts = setColorBadge()
	for p in players:
		buildColorBadgeForPlayer(p,img,fonts)


post_save.connect(buildColorBadge,sender=Game)
post_delete.connect(buildColorBadge,sender=Game)

def buildBadges(sender,**kwargs):
	print "handler was called"
	user= kwargs['user']
	for b in user.badge_set.all():
		build_badge(b)
profile_unlink.connect(buildBadges)
profile_link.connect(buildBadges)

def buildBadgesForGame(sender,**kwargs):
	game = kwargs['instance']
	players = inst.players()
	for badge in (b for p in players for b in  p.user.badge_set.all()):
		build_badge(b)
post_save.connect(buildBadgesForGame,sender=Game)
post_delete.connect(buildBadgesForGame,sender=Game)

def clearAll(sender, **kwargs):
	inst = kwargs['instance']
	if sender is Game:
		players = inst.players()
		if hasattr(inst,'clearCache'):
			inst.clearCache()
		if hasattr(inst.site,'clearCache'):
			inst.site.clearCache()
		for p in players:
			if hasattr(p,'clearCache'):
				p.clearCache()

#clear beforehand so anything with a post handler is getting clear data
pre_save.connect(clearAll,sender=Game)
pre_delete.connect(clearAll,sender=Game)


def siteUpdater(sender, **kwargs):
	inst = kwargs['instance']
	if sender is Game:
		site = inst
		site.sitestats.update()
	else:
		for site in Site.objects.all():
			site.sitestats.update()

post_save.connect(siteUpdater,sender=Game)
post_delete.connect(siteUpdater,sender=Game)

def imageBuilder(callback):
	def returning_dec(fn):
		def new_func(inst,*args,**kwargs):
			cacheString = "site_%s_%s"%(callback.__name__,inst.pk)
			if(not cache.get(cacheString)):
				callback(type(inst),instance=inst)
			settings = cache.get(cacheString)
			if(not settings['clean']):
				retval = fn(inst,settings,*args,**kwargs)
				settings['path'] = retval
				settings['clean'] = True
				cache.set(cacheString,settings)
			else:
				retval  =settings['path']
			return retval
		return new_func
	return returning_dec

@imageBuilder(saveSiteStats)
def getSiteImage(site,catSettings=None):
	fig = Figure(figsize=(4.5,3.5))
	fig.patch.set_alpha(0)
	canvas = FigureCanvas(fig)
	titleProp = FontProperties(size=20,family='sans-serif',weight='heavy')
	chart = fig.add_subplot(1.3,1.2,1)
	chart.patch.set_alpha(.0)
	data = [cat[1] for cat in catSettings['cats']]
	total = float(catSettings['total'])
	labels = [(cat[0] if ((float(cat[1])/float(total))>.01) else '') for cat in catSettings['cats']]
	legLabels = [cat[0] for cat in catSettings['cats']]
	explode = [(.2 if (((float(cat[1])/total)<.1) and ((float(cat[1])/total)>.01)) else 0.0) for cat in catSettings['cats']]
	chart.pie(data,shadow=True, labels=labels,explode=explode)
	#chart.legend(legLabels,loc="right",columnspacing=.5,prop=prop,ncol=3,bbox_to_anchor=(1.2,-.22))
	chart.set_title("Win rates for %s"%site.shortName,family='sans-serif',size=16,weight='heavy')
	canvas.print_figure("%s/images/site_cat_totals_%s.png"%(settings.MEDIA_ROOT,site.id))
	return ("/images/site_cat_totals_%s.png"%site.id)
