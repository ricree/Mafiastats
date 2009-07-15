# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from mafiastats.mafiaStats.models import Site, Game, Team, Category,Player
from mafiastats.mafiaStats.forms import AddGameForm
import json

def index(request):
	site_list = Site.objects.all()[:5]
	return render_to_response('index.html',{'site_list' : site_list})
def site(request,site_id):
	try:
		p = Site.objects.get(pk=site_id)
	except Site.DoesNotExist:
		raise Http404
	games = Game.objects.filter(site=p)[:10]
	return render_to_response('site.html', {'site' : p, 'games_list' : games})
#	return HttpResponse("Not yet implemented")
def game(request, game_id):
	game = get_object_or_404(Game, pk=game_id)
	teams = Team.objects.filter(game=game).order_by('-won')
	players = []
	for team in teams:
		players += team.players.all()
	numPlayers = len(players)
	length = game.end_date - game.start_date
	winners = teams.filter(won=True)
	numWinners =teams.filter(won=True).count()
	return render_to_response('game.html', {'game':game, 'teams':teams, 'num_players' : numPlayers, 'length':length, 'players':players,'winners':winners})

def player(request,player_id):
	player = get_object_or_404(Player, pk=player_id)
	played = player.team_set.all()
	won = player.team_set.filter(won=True)
	lost = player.team_set.filter(won=False)
	moderated = player.moderated_set.all()
	return render_to_response('player.html',{'player':player,'played':played,'moderated':moderated, 'won':won,'lost':lost})
def playerPlayed(request,player_id):
	return HttpResponse("Not yet implemented")
def playerModerated(request,player_id):
	return HttpResponse("Not yet implemented")
def games(request, site_id,page):
	return HttpResponse("Not yet implemented")
def scoreboard(request, site_id,page):
	site = get_object_or_404(Site, pk=site_id)
	players = Player.objects.filter(site=site)
	players = zip(list(players),[player.score() for player in players])
	players.sort(cmp=(lambda (x,xs),(y,ys): (1 if xs< ys else -1)))
	players,scores = zip(*players)
	return render_to_response('scoreboard.html', {'site':site,'players':players})
def add(request, site_id=None):
	if request.method=='POST':
		return HttpResponse("Not yet implemented")
	else:
		form =  AddGameForm(initial={'title':'Test 2'})
		bodyscripts = form.media.render_js()
		sheets = form.media.render_css() #it either returns an iterable or 
		if type(sheets) is str:#a string.  a string screws with the template
			sheets = [sheets,] #so we must box strings up in a list
		if type(bodyscripts) is str:
			bodyscripts = [bodyscripts,]
		if (site_id):
			site = Site.objects.get(pk=site_id)
		else:
			site = None
	return render_to_response('addGame.html',{'form':form,'bodyscripts':bodyscripts,'sheets':sheets,'site':site,'id':site_id})
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

