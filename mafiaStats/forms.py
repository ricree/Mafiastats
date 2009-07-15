from django import forms
from mafiastats.mafiaStats.widgets import AutoTextBox, JQueryDateWidget
from mafiastats.mafiaStats.models import Site
from django.contrib.admin.widgets import AdminDateWidget

class AddGameForm(forms.Form):
	title = forms.CharField(max_length=50, initial="Stuff")
	url = forms.URLField(max_length=75)
	moderator = forms.CharField(max_length=50, widget=AutoTextBox())
	start_date = forms.DateField(widget = JQueryDateWidget())
	end_date = forms.DateField(widget = JQueryDateWidget())
	#site = forms.ModelChoiceField(Site)
