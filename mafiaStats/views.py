# Create your views here.
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from Mafiastats.mafiaStats.models import Site, Game, Team, Category,Player
from Mafiastats.mafiaStats.forms import AddGameForm,TeamFormSet,AddTeamForm
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from itertools import chain
import json

def index(request):
	site_list = Site.objects.all()[:5]
	return render_to_response('index.html',{'site_list' : site_list},context_instance=RequestContext(request))
def site(request,site_id,page=1):
	try:
		p = Site.objects.get(pk=site_id)
	except Site.DoesNotExist:
		raise Http404
	games = Game.objects.filter(site=p)
	return render_to_response('site.html', {'site' : p, 'games_list' : games},context_instance=RequestContext(request))
#	return HttpResponse("Not yet implemented")
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
	return render_to_response('game.html', {'game':game, 'teams':teams, 'num_players' : numPlayers, 'length':length, 'players':players,'winners':winners},context_instance=RequestContext(request))

def player(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	played = player.team_set.all()
	won = player.team_set.filter(won=True)
	lost = player.team_set.filter(won=False)
	moderated = player.moderated_set.all()
	return render_to_response('player.html',{'player':player,'played':played,'moderated':moderated, 'won':won,'lost':lost},context_instance=RequestContext(request))
def playerPlayed(request,player_id):
	return HttpResponse("Not yet implemented")
def playerModerated(request,player_id):
	return HttpResponse("Not yet implemented")
def get_bounds(perPage,page,num):
	if (page <1):
		return -1
	if ((perPage*(page-1)) > num):
		return -1
	if ((perPage * page)>num):
		return num
	return perPage*page
def games(request, site_id,page=1):
	gamesPerPage = 10
	page = int(page)
	numGames = Game.objects.count
	last = get_bounds(gamesPerPage,page,numGames)
	if (last<0):
		raise Http404("Page out of bounds")
	site = get_object_or_404(Site,id=site_id)
	pageGames = Game.objects.filter(site=site)[gamesPerPage*(page-1):last]
	return render_to_response("games.html",{'games':pageGames,'site':site},context_instance=RequestContext(request))
def scoreboard(request, site_id,page=1):
	site = get_object_or_404(Site, pk=site_id)
	players = Player.objects.filter(site=site)
	players = zip(list(players),[player.score() for player in players])
	players.sort(cmp=(lambda (x,xs),(y,ys): (1 if xs< ys else -1)))
	players,scores = zip(*players)
	for player in players:
		totalGames = player.losses() + player.wins()
		if(totalGames >0):
			player.win_pct = (100* player.wins())/(player.losses() + player.wins())
		else:
			player.win_pct = "N/A"
	return render_to_response('scoreboard.html', {'site':site,'players':players},context_instance=RequestContext(request))
def moderators(request,site_id,page=1):
	page=int(page)
	modsPerPage=20
	moderators = list(set([game.moderator for game in Game.objects.filter(site=site_id)]))
	site = get_object_or_404(Site,id=site_id)
	last = get_bounds(modsPerPage,page,len(moderators))
	if(last<0):
		raise Http404("Page out of bounds")
	return render_to_response("moderators.html",{'moderators':moderators,'site':site},context_instance=RequestContext(request))
	return HttpResponse("Not yet implemented")
@login_required()
def add(request, site_id=None):
	if request.method=='POST':
		form = AddGameForm(request.POST)
		formset = TeamFormSet(request.POST)
		if(form.is_valid() and formset.is_valid()):
			#return HttpResponse(formset.forms[0].cleaned_data['players'])
			site = Site.objects.get(pk=site_id)
			name = formset.forms[0].cleaned_data['players']
			moderator,created = Player.objects.get_or_create(name=form.cleaned_data['moderator'],site=site)
			if(created):
				moderator.save()
			game = Game(title=form.cleaned_data['title'],moderator=moderator,start_date = form.cleaned_data['start_date'], end_date=form.cleaned_data['end_date'],site=site,gameType=form.cleaned_data['type'])
			game.save()
			for tForm in formset.forms:
				title = tForm.cleaned_data['title']
				category = Category.objects.get(title=tForm.cleaned_data['type'][0])
#				category = tForm.cleaned_data['type']
				won = tForm.cleaned_data['won']
				players = [Player.objects.get_or_create(name=p,site=site)[0] for p in tForm.cleaned_data['players']]
				for p in players:
					p.save()
				team = Team(title=title,category=category,site=site,won=won,game=game)
				team.save()
				for p in players:
					team.players.add(p)
				team.save()
				game.team_set.add(team)
			game.save()
			return HttpResponseRedirect('/game/'+str(game.id)+'/')
			return HttpResponse("Not yet implemented "+ str(name)+str(request.POST['form-0-players']))
	else:
		form =  AddGameForm()
		formset = TeamFormSet()	
	def boxIfString(val):#render either returns an iterable or
		if type(val) is str: #a string.  a string screws with the template
			retval = [val,] #so we must box strings up in a list
		else:
			retval = val
		return retval
	sheets = boxIfString((form.media + formset.media).render_css())
	bodyscripts = boxIfString((form.media+formset.media).render_js())
	if (site_id):
		site = Site.objects.get(pk=site_id)
	else:
		site = None
	left_attrs = [("Team Name:","title"),('Team Type:','type'),('Won:','won')]
	for tform in formset.forms:
		tform.left_attrs = [(label,tform[property],property) for label,property in left_attrs]
	return render_to_response('addGame.html',{'game_form':form,'formset': formset,'bodyscripts':bodyscripts,'sheets':sheets,'site':site,'id':site_id,},context_instance=RequestContext(request))
def nameLookup(request):
	if 'text' not in request.GET:
		return HttpResponse("[]")
	filterAttrs = {'name__istartswith':request.GET['text']}
	if 'site' in request.GET:
		filterAttrs['site'] = request.GET['site']
	#This probably ought to be replaced with something more efficient
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
