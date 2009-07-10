from django.db import models

# Create your models here.

class Site(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=50, blank = False)
	url = models.CharField(max_length=50, blank=True)
	description = models.CharField(max_length=1000, blank = True)
class Category(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=75, blank=False)
	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'
	def games_won(self, site):
		return len(Team.filter(site=site, category = self, won=True))
	def games_lost(self, site):
                return len(Team.filter(site=site, category = self, won=False))
	def win_score(self, site):
		totalWins = len(Team.objects.filter(site=site,won=True))
		totalLosses = len(Team.objects.filter(site=site, won=False))
		selfWins = games_won(self, site_id)
		selfLost = games_lost(self, site_id)
		score = (1-selfWins/totalWins) * ((selfWins +selfLost)/(totalWins+totalLosses))
		return score
	def loss_score(self, site):
		totalWins = len(Team.objects.filter(site=site,won=True))
                totalLosses = len(Team.objects.filter(site=site, won=False))
                selfWins = games_won(self, site_id)
                selfLost = games_lost(self, site_id)
		score = (-1 + selfLost/totalLosses) * .5 *((selfWins + selfLost) / (totalWins + totalLosses))
		return score


class Player(models.Model):
	def __unicode__(self):
		return self.name
	name = models.CharField(max_length=50)
	site = models.ForeignKey(Site)
	def score(self):
		site = self.site
		categories = Category.objects.all()
		wins = self.scores(site, categories, True)
		losses = self.scores(site, categories, False)
		score = 0
		for index in range(0,len(categories)):
			score+= categories[index].win_score(site) * wins[index] + categories[index].loss_score(site)*losses[index]
		return score
	def scores(self, site, category, won=None):
		"""get the number of times this player has scored in one or more categories"""
		numScores = 0
		def findScore(cat):
			if won==None:
				#print cat
				#print Team.objects.filter(site=site,category=cat)
				results = [x for x in Team.objects.filter(site=site,category=cat) if (len(x.players.filter(pk=self.pk)))]
				#print results
				return len(results)
			else:
				results = len([x for x in Team.objects.filter(site=site,category=cat, won=won) if (len(x.players.filter(pk=self.pk)))])
				return results
		if type(category) is list:
			numScores = [findScore(cat) for cat in category]
		else:
			numScores = findScore(category)
		return numScores
class Game(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=50, blank = False)
	url = models.URLField(max_length=75, blank=True)
	moderator = models.ForeignKey(Player, related_name='moderated_set')
	#moderator = models.CharField(max_length=50)
	start_date = models.DateField()
	end_date = models.DateField()
	timestamp = models.DateField(auto_now_add = True)
	gameType = models.CharField(max_length=25,choices = [(u'full','Full Game'),
		(u'mini','Mini Game'), (u'irc','IRC Game')])
	livedToEnd = models.ManyToManyField(Player, blank=True)
	site = models.ForeignKey(Site)
class Team(models.Model):
	def __unicode__(self):
		return ''.join([self.game.title,':',self.title])
	title = models.CharField(max_length=75)
	category = models.ForeignKey(Category)
	players = models.ManyToManyField(Player)
	game = models.ForeignKey(Game)
	site = models.ForeignKey(Site)
	won = models.BooleanField()
	
