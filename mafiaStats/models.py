from django.db.models.query import QuerySet
from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User
from postmarkup import render_bbcode


# Create your models here.

def cacheResult(fn):
	def functionCache(*args,**kwargs):
		self = args[0]
		cName = '%s_%s_%s'%(type(self).__name__,self.id,fn.func_name)
		result = cache.get(cName)
		if(result is not None):#as opposed to something else evaluating to False
			return result
		calcResult =  fn(*args,**kwargs)
		cache.set(cName,calcResult)
		return calcResult
	functionCache.needsCleaning = "%s_%s_%s"%('%s','%s',fn.func_name)
	functionCache.func_name=fn.func_name
	return functionCache

def makeClearCache():
	def clearCache(self):
		for selfKey in dir(self):
			try:
				selfAttr = getattr(self,selfKey)
			except:
				selfAttr = None#we can't access certain attributes
			if hasattr(selfAttr,'needsCleaning'):
				cache.delete(selfAttr.needsCleaning%(type(self).__name__,self.pk))
	return clearCache

class Site(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=50, blank = False)
	url = models.CharField(max_length=250, blank=True)
	shortName = models.CharField(max_length=10,blank=False)
	description = models.CharField(max_length=1000, blank = True)
class Category(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=75, blank=False)
	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'
	@cacheResult
	def avgWinPct(self):
		wins = Team.objects.filter(category=self,won=True).count()
		total = Team.objects.filter
		if (total>0):
			return (wins*100)/total
		else:
			 return "N/A"
	def games_won(self, site):
		return Team.objects.filter(site=site, category = self, won=True).count()
	def games_lost(self, site):
		return Team.objects.filter(site=site, category = self, won=False).count()
	def win_score(self, site):
		totalWins = float(len(Team.objects.filter(site=site,won=True)))
		totalLosses = float(len(Team.objects.filter(site=site, won=False)))
		selfWins = float(self.games_won(site))
		selfLost = float(self.games_lost(site))
		score = (1.0-selfWins/totalWins) * ((selfWins +selfLost)/(totalWins+totalLosses))
		return score
	def loss_score(self, site):
		totalWins = float(len(Team.objects.filter(site=site,won=True)))
		totalLosses = float(len(Team.objects.filter(site=site, won=False)))
		selfWins = float(self.games_won(site))
		selfLost = float(self.games_lost(site))
		score = (-1.0 + selfLost/totalLosses) * .5 *((selfWins + selfLost) / (totalWins + totalLosses))
		return score


class Player(models.Model):
	def __unicode__(self):
		return self.name
	name = models.CharField(max_length=50)
	site = models.ForeignKey(Site)
	firstGame = models.ForeignKey("Game",related_name="firstGame_set",null=True,blank=True)
	lastGame = models.ForeignKey("Game",related_name="lastGame_set",null=True,blank=True)
	score = models.FloatField()
	played = models.IntegerField(default=0)
	clearCache = makeClearCache()
	user = models.ForeignKey(User,related_name="players",null=True,blank=True)

	@cacheResult
	def lived(self):
		return self.game_set.count()
	@cacheResult
	def wins(self):
		#cName = '%s_%s_wins'%(self.site.id,self.name)
		#wins = cache.get(cName)
		#if(wins):
		#	return wins
		#else:
		return Team.objects.filter(players=self,won=True).count()
	@cacheResult
	def losses(self):
		return Team.objects.filter(players=self,won=False).count()
	@cacheResult
	def winPct(self):
		if(self.played>0):
			return (100*Team.objects.filter(players=self,won=True).count())/self.played
		else:
			return 0
	@cacheResult
	def largestModded(self):
		return max(Game.objects.filter(moderator=self))
	@cacheResult
	def largestModdedCount(self):
		return len(self.largestModded().players())
	@cacheResult
	def modded(self):
		return self.moderated_set.count()
	def playedCalc(self):
		return Team.objects.filter(players=self).count()
	def freshScore(self):
		wins = float(self.wins())
		total = float(wins + self.losses())
		if total<1:
			return -1
		return wins**2/total
	def save(self ,force_insert=False, force_update=False):
		self.score=self.freshScore()
		self.played=self.playedCalc()
		super(Player,self).save(force_insert,force_update)
	def updateDates(self,game):
		if(not self.firstGame):
			self.firstGame = game
		if(not self.lastGame):
			self.lastGame = game
		if(game.start_date < self.firstGame.start_date):
			self.firstGame =game
		if(self.lastGame.end_date < game.end_date):
			self.lastGame = game
		self.save()
	
	def oldScore(self):#currently too slow.  needs caching.  might do later
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
		#args is the argument dictionary passed to the filter function
		args = {'site':site,'players':self}
#if won was actually assigned a value, it will be a factor in the query
		if won!=None:
			args['won']=won
		if type(category) is QuerySet:
			numScores = [Team.objects.filter(category=cat,**args).count() for cat in category]
		else:
			numScores = Team.objects.filter(category=category,**args).count()
		return numScores
class Game(models.Model):
	def __unicode__(self):
		return self.title
	title = models.CharField(max_length=50, blank = False)
	url = models.URLField(max_length=250, blank=True)
	moderator = models.ForeignKey(Player, related_name='moderated_set')
	#moderator = models.CharField(max_length=50)
	start_date = models.DateField()
	end_date = models.DateField()
	timestamp = models.DateField(auto_now_add = True)
	gameType = models.CharField(max_length=25,choices = [(u'full','Full Game'),
		(u'mini','Mini Game'), (u'irc','IRC Game')])
	livedToEnd = models.ManyToManyField(Player, blank=True)
	site = models.ForeignKey(Site)
	clearCache = makeClearCache()
	@cacheResult
	def length(self):
		return self.end_date - self.start_date
	def winningTeams(self):
		return self.team_set.filter(won=True)
	def players(self):
		return [player for team in self.team_set.all() for player in team.players.all()]
	@cacheResult
	def num_players(self):
		return sum((team.players.count() for team in self.team_set.all()))
	def save(self, force_insert=False, force_update=False):
		super(Game,self).save(force_insert,force_update)
		for p in self.players():
			p.save()
		self.moderator.save()
class Team(models.Model):
	def __unicode__(self):
		return ''.join([self.game.title,':',self.title])
	title = models.CharField(max_length=75)
	category = models.ForeignKey(Category)
	players = models.ManyToManyField(Player)
	game = models.ForeignKey(Game)
	site = models.ForeignKey(Site)
	won = models.BooleanField()
	def save(self, force_insert=False, force_update=False):
		super(Team,self).save(force_insert,force_update)
		for p in self.players.all():
			p.save()
class Role(models.Model):
	game = models.ForeignKey(Game)
	player = models.ForeignKey(Player)
	title = models.CharField(max_length=50)
	text = models.CharField(max_length=5000)
	def displayText(self):
		return render_bbcode(self.text)

class Badge(models.Model):
	user = models.ForeignKey(User)
	format=models.CharField(max_length=500)
	players = models.ManyToManyField(Player)
	url = models.CharField(max_length=200,blank=True)
	title = models.CharField(max_length=50)
