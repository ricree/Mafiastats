from mafiaStats.models import Site,Game,Team,Category
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.core.cache import cache
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

def saveSiteStats(sender, **kwargs):
	inst = kwargs['instance']
	key = kwargs['key']
	if sender is Game:
		site = inst.site
	else:
		site =inst
	cat_nums = [(cat.title,Team.objects.filter(site=site,category=cat,won=True).count()) for cat in Category.objects.all()]
	total = sum((c[1] for c in cat_nums))
	cache.set(key,{'cats':cat_nums,'total':total,'clean':False})

post_save.connect(saveSiteStats,sender=Game)
post_delete.connect(saveSiteStats,sender=Game)

def imageBuilder(callback):
	def returning_dec(fn):
		def new_func(inst,*args,**kwargs):
			cacheString = "site_%s_%s"%(fn.__name__,inst.pk)
			if(not cache.get(cacheString)):
				callback(type(inst),instance=inst,key=cacheString)
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
