from django.test import TransactionTestCase, TestCase
from django.core.urlresolvers import reverse
from Mafiastats.mafiaStats.models import Game, Site,Player
from Mafiastats.mafiaStats.signalHandlers import siteUpdater
from django.core.management import call_command
from time import sleep
class BasicViews(TransactionTestCase):
	fixtures = ['auto_backup_2010_2_22.json']
	def setUp(self):
		siteUpdater(self, **{'instance':None})
	def test_views(self):
		"""Tests a number of pages to make sure that they are rendered with no server errors"""
		def test_exists(url):
			response = self.client.get(url)
			self.assertEqual(response.status_code,200, msg=url)
		#test index views exist
		for s in ['/','/stat/site/scoreboard/','/stat/site/scoreboard/?page=4&direction=down&method=wins', '/stat/site/games/','/stat/site/games/?page=10&direction=down&method=length','/stat/site/moderators/','/stat/site/moderators/?page=2&method=largest&direction=down']:
			test_exists(s)
		#test that views for one site render without errors
		for s in ['/stat/site/2/','/stat/site/scoreboard/2/?page=1','/stat/site/scoreboard/2/?page=2&direction=down&method=wins','/stat/site/games/2/','/stat/site/games/2?page=3&direction=undefined&method=players','/stat/site/moderators/2', '/stat/game/add/2']:
			test_exists(s)
class AddTest(TransactionTestCase):
	fixtures = ['auto_backup_2010_2_22.json']
	def test_add(self):
		response = self.client.post('/stat/game/add/1/',{'moderator': 'febo','end_date': '12/23/2009', 'title': 'Test3', 'type': 'full', 'start_date': '12/10/2009', 'livedToEnd': 'alexbutterfield,black_magic','game_id': '', 'url': '','livedToEnd_text': '',
		'teamForm-1-title': 'Scum', 'teamForm-1-type': 'Mafia','teamForm-1-team_id': '','teamForm-1-players': 'ricree,NewPlayer','teamForm-1-players_text': '', 'teamForm-1-won': 'on',
		'teamForm-0-title': 'Team 1', 'teamform-0-players_text': '', 'teamForm-0-players': 'alexbutterfield,Croger,black_magic','teamForm-0-team_id': '','teamForm-0-type': 'Town',
		'roleForm-0-title': '','roleForm-0-player': '','roleForm-0-text': '',
		'teamForm-TOTAL_FORMS': '2',  'roleForm-INITIAL_FORMS': '0',  'teamForm-INITIAL_FORMS': '0',  'roleForm-TOTAL_FORMS': '1' 
		})
		self.assertEquals(response.status_code,302)
		self.assertEquals(len(Game.objects.filter(title="Test3")),1)
		self.assertEquals(len(Player.objects.filter(name="NewPlayer")),1)
