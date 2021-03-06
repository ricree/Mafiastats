# Create your views here.
import logging
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import get_object_or_404#render_to_response, get_object_or_404
from coffin.shortcuts import render_to_response,render_to_string
from models import Site, Game, Team, Category,Player,Role,Badge,SiteStats
from forms import AddGameForm,TeamFormSet,TeamFormSetEdit,AddTeamForm,RoleFormSet,LinkForm,BadgeForm
from signals import profile_link,profile_unlink
from tasks import build_badge
from django.db import transaction
from django.template import RequestContext
#from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,permission_required,user_passes_test
from django.core.paginator import Paginator, InvalidPage,EmptyPage
from django.core.urlresolvers import reverse
from django.core.cache import cache
from itertools import chain
from django.views.decorators.cache import cache_page
from collections import defaultdict
import json
import extensions
from postmarkup import render_bbcode
from sortMethods import *
from mafiaStats.signalHandlers import getSiteImage
from django.conf import settings
import datetime
from django.contrib.comments.templatetags.comments import get_comment_list
from coffin import template
import marshal
from multiprocessing import Process, Queue

count = 0
#register = template.Library()
#register.tag('get_comment_list',get_comment_list)

LOGGING_FILE = settings.SITE_ROOT+'/debug_log'
logging.basicConfig(filename=LOGGING_FILE,level=logging.ERROR)

urlT = '<a href="%s">%s</a>'

def andJoin(l):
	llength = len(l)
	if llength == 0:
		return ""
	if llength == 1:
		return l[0]
	if llength == 2:
		return ' and '.join(l)
	start = ', '.join(l[:-1])
	return ', and '.join([start,l[-1]])

def foo(q):
	q.put("hello")
	q.get()
queue = Queue()
p = Process(target=foo,args=(queue,))


def getPage(request,paginator,default=1,indexRange=2):
	try:
		pNum = int(request.GET.get('page',str(default)))
	except ValueError:
		pNum = 1
	try:
		retval = paginator.page(pNum)
	except (EmptyPage,InvalidPage):
		retval = paginator.page(paginator.num_pages)
	retval.pre_list = []
	retval.post_list=[]
	if(pNum>1):
		retval.pre_list += paginator.page_range[pNum-1-indexRange:pNum-1]
		if 1 not in retval.pre_list:
			retval.pre_list.insert(0,1)
	if(pNum<paginator.num_pages):
		retval.post_list+=paginator.page_range[pNum:pNum+indexRange]
		if paginator.num_pages not in retval.post_list:
			retval.post_list+=[paginator.num_pages]
	return retval

#def tFroms(start):
#	return ((datetime.datetime.now()-start).microseconds / 1000)

def index(request):
	site_list = Site.objects.all()[:5]
	stats = [site.sitestats for site in Site.objects.all()]
	newest = max((stat.newest_game.end_date,stat.newest_game) for stat in stats)[1]#Game.objects.order_by('-end_date')[0]
	largest = max((stat.largest_game.num_players(),stat.largest_game) for stat in stats)[1]
	smallest = min((stat.smallest_game.num_players(),stat.smallest_game) for stat in stats)[1]
	totalPlayed = Game.objects.count()
	numPlayers = Player.objects.count()
	win_list = [p for w,p in sorted(((p.wins(),p) for stat in stats for p in stat.winningest.all()),reverse=True)[0:5]]
	loss_list = [p for l,p in sorted(((p.losses(),p) for stat in stats for p in stat.losingest.all()),reverse=True)[0:5]]
	mostMod = max( ( (stat.most_modded.modded(),stat.most_modded) for stat in stats))[1]
	mostPlayed = max( (stat.most_played.played,stat.most_played) for stat in stats)[1]
	stats= {'win_list':win_list,'loss_list':loss_list,'sidebar':[('Newest Game',newest),('Largest Game',largest),('Smallest Game',smallest),('Games Played',totalPlayed),('Number of Players',numPlayers),('Most Prolific Mod',mostMod),('Most Games Played',mostPlayed)]}
	return render_to_response('index.html',{'site':None,'stats':stats,'site_list' : site_list},context_instance=RequestContext(request))
def site(request,site_id):
	try:
		p = Site.objects.get(pk=site_id)
	except Site.DoesNotExist:
		return HttpResponse("PROBLEMS")
		#raise Http404
	games = Game.objects.filter(site=p).order_by('-end_date')
	stats = {'played': games.count(),'players':Player.objects.filter(site=p).count()}
	if (games.count()>0):
		stats['mostRecent'] = games[0]
	else:
		stats['mostRecent']=None
	stats['largest'] = max(((len(g.players()),g) for g in  Game.objects.filter(site=p)))[1]
	stats['winningest'] = max(((g.wins(),g) for g in Player.objects.filter(site=p)))[1]
	paginator = Paginator(games,15)
	gamesPage = getPage(request,paginator,1)
	newest= None
	count=0
	while not newest:
		game = games[count]
		if (game.firstGame_set.count() >0):
			newest = game.firstGame_set.all()[0]
		count+=1
	imgLink = getSiteImage(Site.objects.get(pk=site_id))
	cat_nums,cat_legends,cat_hrefs = zip(*sorted([(cat.avgWinPct(p.id),"%% "+str(cat.title),str(reverse('mafiastats_scoreboard_typed',args=[p.id,cat.id]))) for cat in Category.objects.all()],reverse=True))
	cat_nums = list(cat_nums)
	cat_legends = list(cat_legends)
	cat_hrefs = list(cat_hrefs)
	cat_wins,cat_names = zip(*sorted([ (cat.pctWins(p.id),str(cat.title)) for cat in Category.objects.all()],reverse=True))
	cat_wins = list(cat_wins)
	cat_names = list(cat_names)
	cat_losses = [100 - x for x in cat_wins]
	cat_blanks = ['']*len(cat_names)
	return render_to_response('site.html', {'stats':stats,'site' : p, 'page' : gamesPage,'pageArgs':{},'newest':newest,'cat_nums': cat_nums,'cat_legends':cat_legends,'cat_names':cat_names,'cat_blanks':cat_blanks,'cat_hrefs':cat_hrefs,'cat_bar_pcts':[cat_wins,cat_losses],'catImg':imgLink},context_instance=RequestContext(request))
def game(request, game_id):
	game = get_object_or_404(Game, pk=game_id)
	teams = Team.objects.filter(game=game).order_by('-won')
	players = []
	for team in teams:
		players += team.players.all()
	players = sorted(players,(lambda x,y:cmp(x.name,y.name)))
	numPlayers = len(players)
	length = game.end_date - game.start_date
	winners = teams.filter(won=True)
	numWinners =teams.filter(won=True).count()
	teams=[(team,team.players.all().order_by('name')) for team in teams]
	roles=dict(((role.player.name,role) for role in Role.objects.filter(game=game)))
	roleOrder = dict(((role[1].pk,index) for role,index in zip(roles.items(),range(len(roles)))))
	can_edit = request.user.has_perm('mafiaStats.game')
	return render_to_response('game.html', {'can_edit':can_edit,'game':game, 'teams':teams, 'num_players' : numPlayers, 'roleOrder':roleOrder,'length':length, 'next':reverse('mafiastats_game',args=[int(game_id)]),'players':players,'winners':winners,'roles':roles},context_instance=RequestContext(request))
def game_lookup(request):
	if 'game' in request.GET:
		name = request.GET['game']
	else:
		raise Http404, "Game not fount"
	if 'site' in request.GET and request.GET['site']:
		search_args = {'title':name, 'site':int(request.GET['site'])}
	else:
		search_args = {'title':name}
	try:
		pl = Game.objects.filter(**search_args)[0]
	except:
		raise Http404, "player not found"
	return HttpResponseRedirect(reverse("mafiastats_game", args=[pl.id]))


def player_lookup(request):
	if 'name' in request.GET:
		name = request.GET['name']
	else:
		raise Http404, "Name not found"
	if 'site' in request.GET and request.GET['site']:
		search_args = {'name':name,'site':int(request.GET['site'])}
	else:
		search_args = {'name':name}
	try:
		pl = Player.objects.filter(**search_args)[0]
	except:
		raise Http404, "player not found"
	if request.is_ajax():
		return HttpResponse(reverse("mafiastats_player",args=[pl.id]))
	else:
		return HttpResponseRedirect(reverse("mafiastats_player",args=[pl.id]))
		
		

def player(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	played = player.team_set.all()
	won = player.team_set.filter(won=True)
	lost = player.team_set.filter(won=False)
	moderated = player.moderated_set.all()
	stats = {'width':20,'columns':[{'width':5,'contents'
		:[('Games Played',played.count()),('Games Won',won.count()),('Games Lost',lost.count())]},
	{'width':9,'contents':
		[('Games Moderated',moderated.count()),('First Game',urlT%(reverse('mafiastats_game',args=[player.firstGame.id]),player.firstGame.title)),('Last Game',urlT%(reverse('mafiastats_game',args=[player.lastGame.id]),player.lastGame.title))]}]}
	return render_to_response('player.html',{'stats':stats,'player':player,'played':played,'moderated':moderated, 'won':won,'lost':lost},context_instance=RequestContext(request))
def getPlayerGraph(player,depth,caller):
	return {'id':'p'+str(player.id), 'name':player.name,'data':{},'children':([getTeamGraph(t,depth-1,player) for t in player.team_set.all() if t!=caller] if depth else [])}
def getTeamGraph(team,depth,caller):
	return {'id':'t'+str(team.id), 'name':"<center>%s<br/>%s</center>"%(team.game.title,team.title),'data':{},'children':([getPlayerGraph(p,depth-1,team) for p in team.players.all() if p != caller] if depth else [])}
@cache_page(60*15)
def teamGraph(request,team_id):
	team = get_object_or_404(Team,pk=team_id)
	nodes = getTeamGraph(team,4,None)
	#for player in team.players.all():
	#	adjacencies = [{'nodeTo':'t'+str(team.id),'data':{'weight':3}}]
	#	nodes.append({'id':'p' + str(player.id),'name':player.name,'data':{"$dim":15.0},'adjacencies':adjacencies})
	return HttpResponse(json.dumps(nodes))
def buildTeamGraph(team,playerset,teamset):
	if team.id in teamset:
		return
	node = cache.get('mafiastats_team_graph_'+str(team.id))
	teamset.add(team.id)
	players = team.players.all()
	if not node:
		templatePlayers = [(player,player.role_set.filter(game=team.game)) for player in players]
		adj = [{'nodeTo':'p'+str(player.id), 'data':{}} for player in team.players.all()]
		node = {'id':'t'+str(team.id),'name':team.title,'data':{'infobox':render_to_string("teamGraphInfo.html",{'team':team,'players':templatePlayers})},'adjacencies':adj}
		cache.set('mafiastats_team_graph_'+str(team.id),node,60*30)
	yield node
	for player in players:
		for n in buildPlayerGraph(player,playerset,teamset):
			yield n
	
	
def buildPlayerGraph(player,playerset,teamset):
	if player.id in playerset:
		return
	playerset.add(player.id)
	node =  cache.get('mafiastats_player_graph_'+str(player.id))
	teams = player.team_set.all()
	if not node:
		wonlist = [t for t in teams if t.won]
		lostlist = [t for t in teams if not t.won]
		adj = [{'nodeTo':'t'+str(team.id), 'data':{}} for team in teams]
		node={'id':'p'+str(player.id),'name':player.name,'data':{'infobox':render_to_string("playerGraphInfo.html",{'player':player,'wonlist':wonlist,'lostlist':lostlist})},'adjacencies':adj}
		cache.set('mafiastats_player_graph_'+str(player.id), node,30*60)
	yield node
	for team in teams:
		for n in buildTeamGraph(team,playerset,teamset):
			yield n
	
@cache_page(60*15)
def playerGraph(request, player_id):
	player = get_object_or_404(Player,id=player_id)
	playerset = set()
	teamset = set()
	nodes = list(buildPlayerGraph(player,playerset,teamset))
	nodes = {'data':nodes,'initial':0}
	#nodes = getPlayerGraph(player,4,None)
	#for team in player.team_set.all():
		#adjacencies = [{'nodeTo':'p'+str(player.id),'data':{'weight':3}} for w in team.players.all()]
	#	adjacencies = [{'nodeTo':'p'+str(player.id),'data':{'weight':3}}]
	#	nodes.append({'id':'t' + str(team.id),'name':team.title,'data':{"$dim":11.0},'adjacencies':adjacencies})
	return HttpResponse(json.dumps(nodes))
	
def playerPlayed(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	sortMethods = {'team':'title','game':teamsByGame,'length':teamsByLength,'won':'won','default':'title'}
	if (not request.is_ajax()):
		totalCat = defaultdict(lambda:0)
		wonCat = defaultdict(lambda:0)
		total = 0
		won = 0
		for team in player.team_set.all():
			totalCat[team.category]+=1
			total+=1
			if team.won:
				won+=1
				wonCat[team.category]+=1
		cats = [(cat.title,wonCat[cat],totalCat[cat]-wonCat[cat],totalCat[cat]) for cat in totalCat]
		cats.append( ("Total",won,total-won,total))
	else:
		cats=[]
	if(player.played >0):
		survivalPercentage = (player.lived() *100)/player.played
	else:
		survivalPercentage = "N/A"
	games = sortTable(request.GET,sortMethods,player.team_set.all())
	paginator = Paginator(games,5)
	page=getPage(request,paginator)
	if request.is_ajax():
		return render_to_response("playerGamesListing.html",{'player':player,'teams':page.object_list},context_instance=RequestContext(request))
	sortMethods = sorted((key, (len(key)/3)+1) for key in sortMethods );
	stats={'survivalPercentage':survivalPercentage}
	return render_to_response('played.html',{'stats':stats,'sortMethods':sortMethods,'page':page,'player':player,'teams':page.object_list,'categories':cats},context_instance=RequestContext(request))
def playerModerated(request,player_id):
	includedFactions = defaultdict(lambda:0)
	wonFactions = defaultdict(lambda:0)
	player = get_object_or_404(Player,pk=player_id)
	games = Game.objects.filter(moderator=player)
	for game in games:
		factions = defaultdict(lambda:False)
		won = defaultdict(lambda:False)
		for team in game.team_set.all():
			if team.won:
				if not won[team.category]:
					wonFactions[team.category]+=1
					won[team.category] = True
			if not factions[team.category]:
				includedFactions[team.category] +=1
				factions[team.category] = True
	games = [(game,andJoin([t.title for t in game.team_set.filter(won=True)])) for game in games]
	cats = [(cat, wonFactions[cat], includedFactions[cat]) for cat in includedFactions]
	return render_to_response('modded.html',{'player':player,'games':games,'cats':cats},context_instance=RequestContext(request))
	return HttpResponse("Not yet implemented")
def get_bounds(perPage,page,num):
	if (page <1):
		return -1
	if ((perPage*(page-1)) > num):
		return -1
	if ((perPage * page)>num):
		return num
	return perPage*page
@cache_page(60*20)
def games(request, site_id):
	gamesPerPage = 5
	query = Game.objects
	if(site_id !=''):
		site = get_object_or_404(Site,id=site_id)
		query = query.filter(site=site)
		funcArgs= {'site':site}
	else:
		funcArgs={'site':None}
		query = query.all()
	sortMethods = {'name':'title','moderator':'moderator','length':gamesByLength,'start':'start_date','end':'end_date','players':gamesByPlayers,'default':'end_date'}
	dirs = {'up':'down','down':'up'}
	dir = dirs[request.GET['direction']] if ('direction' in request.GET and request.GET['direction'] in dirs) else 'up'
	meth = request.GET['method'] if 'method' in request.GET else sortMethods['default']
	p = sortTable(request.GET,sortMethods,query)
	paginator = Paginator(p,gamesPerPage)
	page=getPage(request,paginator)
	respTemplate = "gamesListing.html" if request.is_ajax() else "games.html"
	sortMethods = sorted((key, (len(key)/3)+1) for key in sortMethods );
	args = {'games':page.object_list,'page':page,'sortMethods':sortMethods,'direction':dir,'pageArgs':{'direction':dir,'method':meth}}
	args.update(funcArgs)
	return render_to_response(respTemplate,args,context_instance=RequestContext(request))

def sortTable(GET,methods,query,defaultDir='down',category=None):
	reversals = {'up':False,'down':True}
	methodStr = GET['method'] if 'method' in GET else 'default'
	methodDir = GET['direction'] if 'direction' in GET else defaultDir
	if methodStr in methods:
		methodDir = methodDir if methodDir in ['up','down'] else defaultDir
	else:
		methodStr = 'default'
		methodDir = defaultDir
	return sortQuery(query,methods[methodStr],reversals[methodDir],category)

@cache_page(60*20)
def scoreboard(request, site_id=None,category=None):
	sortMethods={'score':'score','name':'name','wins':playersByWins,'losses':playersByLosses,'winPct':playersByWinPct,'modded':playersByModerated,'default':'score'}
	nextDir = {'up':'down','down':'up'}
	if (('direction' in request.GET) and (request.GET['direction'] in nextDir)):
		direction = nextDir[request.GET['direction']]
	else:
		direction = 'up'
	query = Player.objects
	if((site_id is not None)and(site_id != '')):
		site = get_object_or_404(Site, pk=site_id)
		funcArgs={'site':site}
		query = query.filter(played__gt=0,site=site)
	else:
		query = query.filter(played__gt=0)
		funcArgs = {'site':None}
	if((category is not None) and (category != '')):
		category = get_object_or_404(Category, pk=category)
		funcArgs['type']=category
		players = sortTable(request.GET,sortMethods,[x for x in query if x.playedCalc(category) >0],category=category)
	else:
		players = sortTable(request.GET,sortMethods,query)
#	players = [(player,player.score()) for player in players if player.played()>0]
#	players.sort(cmp=(lambda (x,xs),(y,ys): cmp(ys,xs)))
#	players,scores = zip(*players)
	paginator=Paginator(players,25)
	page=getPage(request,paginator)
	if 'method' in request.GET:
		meth = request.GET['method']
	else:
		meth = sortMethods['score']
	if(request.is_ajax()):
		args = {'players':page.object_list,'page':page,'direction':direction,'pageArgs':{'method':meth,'direction':direction}}
		args.update(funcArgs)
		return render_to_response('scoreBoardPresenter.html',args,context_instance=RequestContext(request))
	args = {'players':page.object_list,'categories':Category.objects.all(),'page':page,'direction':direction,'pageArgs':{'method':meth,'direction':direction}}
	args.update(funcArgs)
	return render_to_response('scoreboard.html',args,context_instance=RequestContext(request))
def moderators(request,site_id):
	sortMethods={'name':'name','modded':playersByModerated,'largest':modsByLargestGame,'default':'name'}
	modsPerPage=15
	query = Game.objects
	if(site_id != ''):
		site = get_object_or_404(Site,id=site_id)
		funcArgs = {'site':site}
		query= query.filter(site=site_id)
	else:
		funcArgs={'site':None}
		query = query.all()
	moderators = list(set([game.moderator for game in query]))
	moderators = sortTable(request.GET,sortMethods,moderators)
	paginator=Paginator(moderators,modsPerPage,orphans=5)
	page = getPage(request,paginator)
	responseTemplate = "moderatorsListing.html" if request.is_ajax() else "moderators.html"
	args = {'page':page,'pageArgs':{},'moderators':page.object_list}
	args.update(funcArgs)
	return render_to_response(responseTemplate,args,context_instance=RequestContext(request))
@transaction.commit_on_success
def add(request, site_id=None):
	if request.method=='POST':
		form = AddGameForm(request.POST)
		teamFormset = TeamFormSet(request.POST,prefix='teamForm')
		roleFormset = RoleFormSet(request.POST,prefix='roleForm')
		if(form.is_valid() and teamFormset.is_valid() and roleFormset.is_valid()):
			try:
			#return HttpResponse(formset.forms[0].cleaned_data['players'])
				print "adding game to site", site_id
				print "Sites are", Site.objects.all()
				print "Players are",Player.objects.all()
				site = Site.objects.get(pk=site_id)
				name = teamFormset.forms[0].cleaned_data['players']
				moderator,created = Player.objects.get_or_create(name=form.cleaned_data['moderator'],site=site)
				if(created):
					moderator.save()
				else:
					moderator.clearCache()
				game = Game(title=form.cleaned_data['title'],moderator=moderator,start_date = form.cleaned_data['start_date'], end_date=form.cleaned_data['end_date'],site=site,gameType=form.cleaned_data['type'])
					
				if (form.cleaned_data['url'] is not ''):
					game.url = form.cleaned_data['url']
				game.save()
				for pName in form.cleaned_data['livedToEnd']:
					player,created = Player.objects.get_or_create(name=pName,site=site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':1})
					player.save()
					game.livedToEnd.add(player)
				for tForm in teamFormset.forms:
					if ('title' in tForm.cleaned_data) and (tForm.cleaned_data['title'] != ""):
						title = tForm.cleaned_data['title']
					else:
						title = tForm.cleaned_data['type'].title()
					category = Category.objects.get(title=tForm.cleaned_data['type'])
	#				category = tForm.cleaned_data['type']
					won = tForm.cleaned_data['won']
					players = [Player.objects.get_or_create(name=p,site=site,defaults={'firstGame':game,'lastGame':game})[0] for p in tForm.cleaned_data['players']]
					for p in players:
						p.save()
					team = Team(title=title,category=category,site=site,won=won,game=game)
					team.save()
					for p in players:
						team.players.add(p)
						p.updateDates(game)
						p.clearCache()
					team.save()
					game.team_set.add(team)
				for rForm in roleFormset.forms:
					if(rForm.has_changed()):
						title = rForm.cleaned_data['title']
						pName = rForm.cleaned_data['player']
						text = rForm.cleaned_data['text']
						player,created = Player.objects.get_or_create(name=pName,site=site,defaults={'firstGame':game,'lastGame':game})
						role,created = Role.objects.get_or_create(title=title,game=game,player=player,text=text)
						role.save()
				game.save()
				return HttpResponseRedirect(reverse('mafiastats_game',args=[game.id]))
			except Exception as e:
				logging.exception(e.args[0])
				raise#let the default behavior handle the error, we just want to log it
	else:
		form =  AddGameForm()
		teamFormset = TeamFormSet(prefix='teamForm')	
		roleFormset = RoleFormSet(prefix='roleForm')
	def boxIfString(val):#render either returns an iterable or
		if type(val) is str: #a string.  a string screws with the template
			retval = [val,] #so we must box strings up in a list
		else:
			retval = val
		return retval
	sheets = boxIfString((form.media + teamFormset.media).render_css())
	bodyscripts = boxIfString((form.media+teamFormset.media).render_js())
	if (site_id):
		site = Site.objects.get(pk=site_id)
	else:
		site = None
	left_attrs = [("Team Name:","title"),('Team Type:','type'),('Won:','won')]
	for tform in teamFormset.forms:
		tform.left_attrs = [(label,tform[property],property) for label,property in left_attrs]
	return render_to_response('addGame.html',{'game_form':form,'roleFormset':roleFormset,'teamFormset': teamFormset,'bodyscripts':bodyscripts,'sheets':sheets,'site':site,'id':site_id,'submit_link':reverse('mafiastats_add',args=[site_id])},context_instance=RequestContext(request))

def game_name_lookup(request):
	if 'text' not in request.GET:
		return HttpResponse("[]")
	if ('site' in request.GET) and (request.GET['site']):
		filter_query = {'title__istartswith':request.GET['text'],'site':int(request.GET['site'])}
	else:
		filter_query = {'title__istartswith':request.GET['text']}
	games = Game.objects.filter(**filter_query)
	response = [{'id':game.id,'text':game.title} for game in games]
	print response
	response = json.dumps(response)
	print response
	return HttpResponse(response)

def nameLookup(request):
	if 'text' not in request.GET:
		return HttpResponse("[]")
	filterAttrs = {'name__istartswith':request.GET['text']}
	if 'site' in request.GET:
		filterAttrs['site'] = request.GET['site']
	#This probably ought to be replaced with something more efficient
	#like a trie or something
	#Then again, game entries aren't that common, so might not be worth it
	players = Player.objects.filter(**filterAttrs)
	response = [{'id':player.id,'text':player.name} for player in players]
	response = json.dumps(response)
	return HttpResponse(response)
def register(request):
	if (request.method=='POST'):
		form = UserCreationForm(request.POST)
		if( form.is_valid()):
			username = form.cleaned_data['username']
			email = ''
			password = form.cleaned_data['password1']
			user = User.objects.create_user(username,email,password)
			user.save()
			return HttpResponseRedirect("/")
	else:
		form=UserCreationForm()
	return render_to_response("register.html",{'form':form},context_instance=RequestContext(request))

#@permission_required('mafiaStats.game')
@login_required
@transaction.commit_on_success
def edit(request,game_id):
	game = get_object_or_404(Game,pk=game_id)
	if(request.method=="POST"):
		form = AddGameForm(request.POST)
		teamForm = TeamFormSetEdit(request.POST,prefix="teamForm")
		roleForm = RoleFormSet(request.POST,prefix="roleForm")
		if(form.is_valid() and teamForm.is_valid() and roleForm.is_valid()):
			game = Game.objects.get(pk=form.cleaned_data['game_id'])
			game.title = form.cleaned_data['title']
			game.url = form.cleaned_data['url']
			game.gameType = form.cleaned_data['type']
			moderator,created = Player.objects.get_or_create(name=form.cleaned_data['moderator'],site=game.site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':0})
			if(created):
				moderator.save()
			game.moderator=moderator
			game.start_date = form.cleaned_data['start_date']
			game.end_date = form.cleaned_data['end_date']
			game.save()
			game.livedToEnd.clear()
			for pName in form.cleaned_data['livedToEnd']:
				player, created = Player.objects.get_or_create(name=pName,site=game.site,defaults={'firstGame':game,'lastGame':game})
				if created:
					player.save()
				game.livedToEnd.add(player)
			for t in Team.objects.filter(game=game):
				t.delete()
			for tForm in teamForm.forms:
				if ('title' in tForm.cleaned_data) and (tForm.cleaned_data['title'] != ""):
					title = tForm.cleaned_data['title']
				else:
					title = tForm.cleaned_data['type'].title()
				team = Team(game=game,title=title,category=Category.objects.get(title=tForm.cleaned_data['type']),site=game.site,won=tForm.cleaned_data['won'])
				team.save()
				for pName in tForm.cleaned_data['players']:
					p, created = Player.objects.get_or_create(name=pName,site=game.site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':0})
					p.updateDates(game)
					p.save()
					team.players.add(p)
				team.save()
			for role in Role.objects.filter(game=game):
				role.delete()
			for rForm in roleForm.forms:
				if(rForm.has_changed()):
					p,created = Player.objects.get_or_create(name=rForm.cleaned_data['player'],site=game.site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':0})
					role = Role(game=game,player=p,text=rForm.cleaned_data['text'],title=rForm.cleaned_data['title'])
					role.save()
			game.save()
			return HttpResponseRedirect(reverse('mafiastats_game',args=[game.id]))
	else:
		game = get_object_or_404(Game,pk=game_id)
		teams = Team.objects.filter(game=game)
		dateFormat = "%m/%d/%Y"
		gameData = {'title':game.title,'url':game.url,'livedToEnd':[p.name for p in game.livedToEnd.all()],'moderator':game.moderator.name,'start_date':game.start_date.strftime(dateFormat),'end_date':game.end_date.strftime(dateFormat),'type':game.gameType,'game_id':game.id}
		teamData = [{'title':team.title,'won':team.won,'type':team.category.title,'team_id':team.id,'players':[p.name for p in team.players.all()]} for team in teams]
		roleData = [{'title':role.title,'player':role.player.name,'text':role.text} for role in Role.objects.filter(game=game)]
		form = AddGameForm(gameData)
		teamForm = TeamFormSetEdit(initial=teamData, prefix="teamForm")
		roleForm = RoleFormSet(initial=roleData,prefix="roleForm")
	left_attrs = [("Team Name:","title"),('Team Type:','type'),('Won:','won')]
	for tform in teamForm.forms:
		tform.left_attrs = [(label,tform[property],property) for label,property in left_attrs]
	sheets = (form.media+teamForm.media+roleForm.media).render_css()
	bodyscripts=(form.media+teamForm.media +roleForm.media).render_js()
	return render_to_response("addGame.html",{'game_form':form,'teamFormset':teamForm,'roleFormset':roleForm,'site':game.site,'sheets':sheets,'id':game.site.id,'bodyscripts':bodyscripts,'submit_link':reverse('mafiastats_edit',args=[int(game_id)])},context_instance=RequestContext(request))

@transaction.commit_on_success
@login_required
def link(request):
	form = LinkForm()
	if (request.method == "POST"):
		form = LinkForm(request.POST)
		if (form.is_valid()):
			site = get_object_or_404(Site,pk=int(form.cleaned_data['site']))
			player = get_object_or_404(Player,name=form.cleaned_data['player'],site=site)
			player.user = request.user
			player.save()
			try:
				profile_link.send(User,user=request.user,player=player)
			except Exception as e:
				logging.exception(e.args[0])
				raise Http404
			return HttpResponseRedirect(reverse('account_profile'))
	bodyscripts= form.media.render_js()
	sheets = form.media.render_css()
	defaultSite = form.fields['site'].choices[0][0]
	return render_to_response("link.html",{'form':form,'default_site':defaultSite,'sheets':sheets,'bodyscripts':bodyscripts},context_instance=RequestContext(request))

def profile(request,pk=""):
	if((not request.user.is_authenticated()) and (pk =="")):
		raise Http404
	if ((request.user.is_authenticated() and (pk == request.user.pk)) or (pk =="")):
		user = request.user
		ownPage = True
	else:
		user = get_object_or_404(User, pk=pk)
		ownPage=False
	if user.players.count():
		played = 0
		won = 0
		lost = 0
		modded = 0
		firsts = []
		lasts = []
		for player in user.players.all():
			played+=player.played
			won+=player.wins()
			lost+=player.losses()
			modded+=player.modded()
			firsts+=[(player.firstGame.start_date,player.firstGame)]
			lasts +=[(player.lastGame.end_date,player.lastGame)]
		first = min(firsts)[1]
		last = max(lasts)[1]
		stats = {'width':18,'columns':[
			{'width':4,'contents':
				[('Games Played',played),('Games Won',won),('Games Lost',lost)]},
			{'width':9,'contents':
				[('Games Moderated',modded),('First Game',urlT%(reverse('mafiastats_game',args=[first.id]),first.title)),('Last Game',urlT%(reverse('mafiastats_game',args=[last.id]),last.title))]}
			]}
	else:
		stats = {}
	return render_to_response("profile.html",{'profile_user':user,'own_page':ownPage,'stats':stats},context_instance=RequestContext(request))



@transaction.commit_on_success
@login_required
def badge(request,pk=""):
	choices = [(p.id,p.name + ' - ' + p.site.title) for p in request.user.players.all()]
	if (request.method == 'POST'):
		form = BadgeForm(request.POST)
		form.fields['players'].choices = choices
		if(form.is_valid()):
			players = [get_object_or_404(Player,pk=int(p)) for p in form.cleaned_data['players']]
			if pk:
				badge = get_object_or_404(Badge,pk=int(pk))
				badge.players.clear()
				badge.title = form.cleaned_data['title']
				badge.format = form.cleaned_data['config']
				badge.is_custom = form.custom_format
			else:
				config = form.cleaned_data['config'].replace(r'\n','\n')
				badge = Badge(user=request.user,is_custom = form.custom_format,format=config,title=form.cleaned_data['title'])
				badge.save()
			for p in players:
				badge.players.add(p)
			badge.save()
			badge.url = "images/badges/badge_custom_%s_%s.png"%(request.user.pk,badge.pk)
			badge.save()	
			try:
				build_badge.delay(badge)
			except Exception as e:
				logging.exception(e.args[0])
				raise e
			return HttpResponseRedirect(reverse("account_profile"))
	else:
		if pk:
			badge = get_object_or_404(Badge,pk=pk)
			if badge.is_custom:
				params = eval(badge.format)
				formData = {'title':badge.title,'players':[p.id for p in badge.players.all()],'preset':params['template'],'background':params['background'],'top_color':params['color1'],'bottom_color':params['color2'],'text_color':params['text'],'font_size':params['size']}
			else:
				config = badge.format.replace('\n','\\n')
				formData = {'title':badge.title,'config':config,'players':[(p.id,p.name + ' - ' + p.site.title) for p in badge.players.all()]}
			form = BadgeForm(initial=formData)
		else:
			#form  = BadgeForm({'players':players})
			form  = BadgeForm()
		form.fields['players'].choices = choices
	return render_to_response("badge.html",{'form':form,'pk':pk},context_instance=RequestContext(request))

@login_required
def badge_delete(request,pk):
	badge = get_object_or_404(Badge,pk=int(pk))
	if(request.user.pk != badge.user.pk):
		return render_to_response("badge_delete.html",{'can_delete':False,'message':'You cannot unlink this account'},context_instance=RequestContext(request))
	if(request.method=="POST"):
		badge.delete()
		return HttpResponseRedirect(reverse("account_profile"))
	return render_to_response("badge_delete.html",{'can_delete':True,'pk':pk},context_instance=RequestContext(request))
@login_required
def unlink(request,pk):
	player = get_object_or_404(Player,pk=int(pk))
	if(request.user.pk != player.user.pk):
		return render_to_response("unlink.html",{'can_unlink':False,'message':'You cannot unlink this account'},context_instance=RequestContext(request))	
	if (request.method=="POST"):
		player.user = None
		for badge in player.badge_set.all():
			badge.players.remove(player)
		player.save()
		profile_unlink.send(User,user=request.user,player=player)
		return HttpResponseRedirect(reverse('account_profile'))
	return render_to_response("unlink.html",{'can_unlink':True,'message':'This message should not show up','pk':pk},context_instance=RequestContext(request))
@login_required
def badge_preview(request):
	choices = [(p.id,p.name + ' - ' + p.site.title) for p in request.user.players.all()]
	url = "images/badges/badge_temp_%s.png"%hash(request.META["REMOTE_ADDR"])
	if (request.method =="POST"):
		form = BadgeForm(request.POST)
		form.fields['players'].choices = choices
		if (form.is_valid()):
			class Temp(object):
				pass
			badge = Temp()
			players = [get_object_or_404(Player,pk=int(p)) for p in form.cleaned_data['players']]
			badge.players = Temp()
			badge.players.all = lambda : players
			badge.title = form.cleaned_data['title']
			badge.format = form.cleaned_data['config']
			badge.is_custom = form.custom_format
			badge.url = url
			badge.user = request.user
			build_badge.delay(badge)
		else:
			print form.errors
	return HttpResponse(url+"?"+str(hash(datetime.datetime.now())))
			
