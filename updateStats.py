from Mafiastats.mafiaStats.models import Site,SiteStats
def update():
	for s in Site.objects.all():
		stats, created = SiteStats.objects.get_or_create(site=s)
		stats.update()

