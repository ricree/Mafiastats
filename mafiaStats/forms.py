from django import forms
from mafiastats.mafiaStats.widgets import AutoTextBox

class AddGameForm(forms.Form):
	title = forms.CharField(max_length=50)
	game_url = forms.URLField(max_length=75)
	moderator = forms.CharField(max_length=50, widget=AutoTextBox())
