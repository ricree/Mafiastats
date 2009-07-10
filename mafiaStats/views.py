# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from mafiastats.mafiaStats.models import Site, Game, Team, Category,Player

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
	teams = Team.objects.filter(game=game).order_by('won')
	numPlayers = 0
	for team in teams:
		numPlayers += len(team.players.all())
	length = game.end_date - game.start_date
	winners = teams.filter(won=True)
	numWinners = len(winners)
	return render_to_response('game.html', {'game':game, 'teams':teams, 'num_players' : numPlayers, 'length':length, 'winners':winners, 'num_winners':numWinners})

def player(request, site_id,player_id):
	player = get_object_or_404(Player, pk=player_id)
	played = player.team_set.all()
	won = player.team_set.filter(won=True)
	lost = player.team_set.filter(won=False)
	moderated = player.moderated_set.all()
	return render_to_response('player.html',{'player':player,'played':played,'moderated':moderated, 'won':won,'lost':lost})

def games(request, site_id):
	return HttpResponse("Not yet implemented")
def scoreboard(request, site_id):
	site = get_object_or_404(Site, pk=site_id)
	players = Player.filter(site=site).orderby
	return HttpResponse("Not yet implemented")
def add(request):
	return HttpResponse("Not yet implemented")

