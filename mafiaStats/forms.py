from django import forms

class AddGameForm(forms.Form)
	title = forms.CharField(max_length=50)
	game_url = models.URLField(max_length=75)
