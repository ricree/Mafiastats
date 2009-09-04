# Create your views here.
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from models import Site, Game, Team, Category,Player,Role
from forms import AddGameForm,TeamFormSet,TeamFormSetEdit,AddTeamForm,RoleFormSet
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage,EmptyPage
from django.core.urlresolvers import reverse
from itertools import chain
from django.views.decorators.cache import cache_page
import json
from postmarkup import render_bbcode
from sortMethods import *
from mafiaStats.signalHandlers import getSiteImage

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


def index(request):
	site_list = Site.objects.all()[:5]
	newest = Game.objects.order_by('-end_date')[0]
	largest = max( ( (len(g.players()),g) for g in  Game.objects.all()))[1]
	totalPlayed = Game.objects.count()
	numPlayers = Player.objects.count()
	mostMod = max( ( (p.modded(),p) for p in Player.objects.all()))[1]
	mostPlayed = Player.objects.order_by('-played')[0]
	stats= [('Newest Game',newest),('Largest Game',largest),('Games Played',totalPlayed),('Number of Players',numPlayers),('Most Prolific Mod',mostMod),('Most Games Played',mostPlayed)]
	return render_to_response('index.html',{'stats':stats,'site_list' : site_list},context_instance=RequestContext(request))
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
	return render_to_response('site.html', {'stats':stats,'site' : p, 'page' : gamesPage,'newest':newest,'catImg':imgLink},context_instance=RequestContext(request))
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
	roles=Role.objects.filter(game=game)
	return render_to_response('game.html', {'game':game, 'teams':teams, 'num_players' : numPlayers, 'length':length, 'next':reverse('mafiastats_game',args=[int(game_id)]),'players':players,'winners':winners,'roles':roles},context_instance=RequestContext(request))

def player(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	played = player.team_set.all()
	won = player.team_set.filter(won=True)
	lost = player.team_set.filter(won=False)
	moderated = player.moderated_set.all()
	return render_to_response('player.html',{'player':player,'played':played,'moderated':moderated, 'won':won,'lost':lost},context_instance=RequestContext(request))
def playerPlayed(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	sortMethods = {'team':'title','game':teamsByGame,'length':teamsByLength,'won':'won','default':'title'}
	if (not request.is_ajax()):
		def getCats():
			for cat in Category.objects.all():
				teams = [t for t in player.team_set.all() if t.category==cat]
				total = len(teams)
				wins = len([t for t in teams if t.won])
				losses = total-wins
				yield (cat.title,wins,losses,total)
		cats = list(getCats())
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
	player = get_object_or_404(Player,pk=player_id)
	return render_to_response('modded.html',{'player':player},context_instance=RequestContext(request))
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
	print "I was called"
	gamesPerPage = 5
	if(site_id !=''):
		site = get_object_or_404(Site,id=site_id)
		funcArgs= {'site':site}
	else:
		funcArgs={}
	sortMethods = {'name':'title','moderator':'moderator','length':gamesByLength,'start':'start_date','end':'end_date','players':gamesByPlayers,'default':'end_date'}
	p = sortTable(request.GET,sortMethods,Game.objects.filter(**funcArgs))
	paginator = Paginator(p,gamesPerPage)
	page=getPage(request,paginator)
	respTemplate = "gamesListing.html" if request.is_ajax() else "games.html"
	sortMethods = sorted((key, (len(key)/3)+1) for key in sortMethods );
	args = {'games':page.object_list,'page':page,'sortMethods':sortMethods}
	args.update(funcArgs)
	return render_to_response(respTemplate,args,context_instance=RequestContext(request))

def sortTable(GET,methods,query,defaultDir='down'):
	reversals = {'up':False,'down':True}
	methodStr = GET['method'] if 'method' in GET else 'default'
	methodDir = GET['direction'] if 'direction' in GET else defaultDir
	if methodStr in methods:
		methodDir = methodDir if methodDir in ['up','down'] else defaultDir
	else:
		methodStr = 'default'
		methodDir = defaultDir
	return sortQuery(query,methods[methodStr],reversals[methodDir])

@cache_page(60*20)
def scoreboard(request, site_id=None):
	sortMethods={'score':'score','name':'name','wins':playersByWins,'losses':playersByLosses,'winPct':playersByWinPct,'modded':playersByModerated,'default':'score'}
	if((site_id is not None)and(site_id != '')):
		site = get_object_or_404(Site, pk=site_id)
		funcArgs={'site':site}
	else:
		funcArgs = {}
	print Player.objects.filter(played__gt=0,**funcArgs).count()
	players = sortTable(request.GET,sortMethods,Player.objects.filter(played__gt=0,**funcArgs))
#	players = [(player,player.score()) for player in players if player.played()>0]
#	players.sort(cmp=(lambda (x,xs),(y,ys): cmp(ys,xs)))
#	players,scores = zip(*players)
	paginator=Paginator(players,25)
	page=getPage(request,paginator)
	for player in page.object_list:
		player.win_pct = (100* player.wins())/(player.losses() + player.wins())
	if(request.is_ajax()):
		args = {'players':page.object_list,'page':page}
		args.update(funcArgs)
		return render_to_response('scoreBoardPresenter.html',args,context_instance=RequestContext(request))
	args = {'players':page.object_list,'page':page}
	args.update(funcArgs)
	print args
	return render_to_response('scoreboard.html',args,context_instance=RequestContext(request))
def moderators(request,site_id):
	sortMethods={'name':'name','modded':playersByModerated,'largest':modsByLargestGame,'default':'name'}
	page=int(page)
	modsPerPage=15
	if(site_id != ''):
		site = get_object_or_404(Site,id=site_id)
		funcArgs = {'site':site_id}
	else:
		funcArgs={}
	moderators = list(set([game.moderator for game in Game.objects.filter(**funcArgs)]))
	moderators = sortTable(request.GET,sortMethods,moderators)
	paginator=Paginator(moderators,modsPerPage,orphans=5)
	page = getPage(request,paginator)
	responseTemplate = "moderatorsListing.html" if request.is_ajax() else "moderators.html"
	args = {'page':page,'moderators':page.object_list}
	args.update(funcArgs)
	return render_to_response(responseTemplate,{'page':page,'moderators':page.object_list},context_instance=RequestContext(request))
def add(request, site_id=None):
	if request.method=='POST':
		form = AddGameForm(request.POST)
		teamFormset = TeamFormSet(request.POST,prefix='teamForm')
		roleFormset = RoleFormSet(request.POST,prefix='roleForm')
		if(form.is_valid() and teamFormset.is_valid() and roleFormset.is_valid()):
			#return HttpResponse(formset.forms[0].cleaned_data['players'])
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
			for tForm in teamFormset.forms:
				title = tForm.cleaned_data['title']
				print tForm.cleaned_data['type']
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
				print "RFORM: ", rForm.cleaned_data,', ', len(roleFormset.forms)
				if(rForm.has_changed()):
					title = rForm.cleaned_data['title']
					pName = rForm.cleaned_data['player']
					text = render_bbcode(rForm.cleaned_data['text'])
					player,created = Player.objects.get_or_create(name=pName,site=site,defaults={'firstGame':game,'lastGame':game})
					role,created = Role.objects.get_or_create(title=title,game=game,player=player,text=text)
					role.save()
			game.save()
			return HttpResponseRedirect(reverse('mafiastats_game',args=[game.id]))
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

def edit(request,game_id):
	if(request.method=="POST"):
		form = AddGameForm(request.POST)
		teamForm = TeamFormSetEdit(request.POST,prefix="teamForm")
		roleForm = RoleFormSet(request.POST,prefix="roleForm")
		if(form.is_valid() and teamForm.is_valid() and roleForm.is_valid()):
			game = Game.objects.get(pk=form.cleaned_data['game_id'])
			game.title = form.cleaned_data['title']
			print 'title is: ',form.cleaned_data['title']
			game.url = form.cleaned_data['url']
			game.gameType = form.cleaned_data['type']
			moderator,created = Player.objects.get_or_create(name=form.cleaned_data['moderator'],site=game.site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':0})
			if(created):
				moderator.save()
			game.moderator=moderator
			game.start_date = form.cleaned_data['start_date']
			game.end_date = form.cleaned_data['end_date']
			game.save()
			for t in Team.objects.filter(game=game):
				t.delete()
			for tForm in teamForm.forms:
				team = Team(game=game,title=tForm.cleaned_data['title'],category=Category.objects.get(title=tForm.cleaned_data['type']),site=game.site,won=tForm.cleaned_data['won'])
				team.save()
				for pName in tForm.cleaned_data['players']:
					p, created = Player.objects.get_or_create(name=pName,site=game.site,defaults={'firstGame':game,'lastGame':game,'score':0,'played':0})
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
		gameData = {'title':game.title,'url':game.url,'moderator':game.moderator.name,'start_date':game.start_date,'end_date':game.end_date,'type':game.gameType,'game_id':game.id}
		teamData = [{'title':team.title,'won':team.won,'type':team.category.title,'team_id':team.id,'players':[p.name for p in team.players.all()]} for team in teams]
		roleData = [{'title':role.title,'player':role.player.name,'text':role.text} for role in Role.objects.filter(game=game)]
		form = AddGameForm(gameData)
		teamForm = TeamFormSetEdit(initial=teamData, prefix="teamForm")
		roleForm = RoleFormSet(prefix="roleForm")
	left_attrs = [("Team Name:","title"),('Team Type:','type'),('Won:','won')]
	for tform in teamForm.forms:
		tform.left_attrs = [(label,tform[property],property) for label,property in left_attrs]
	sheets = (form.media+teamForm.media+roleForm.media).render_css()
	bodyscripts=(form.media+teamForm.media +roleForm.media).render_js()
	return render_to_response("addGame.html",{'game_form':form,'teamFormset':teamForm,'roleFormset':roleForm,'site':game.site,'sheets':sheets,'id':game.site.id,'bodyscripts':bodyscripts,'submit_link':reverse('mafiastats_edit',args=[int(game_id)])},context_instance=RequestContext(request))
