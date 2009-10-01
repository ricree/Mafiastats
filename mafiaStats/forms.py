from django import forms
from django.forms.formsets import formset_factory
from widgets import AutoTextBox, JQueryDateWidget,NameBox
from widgets import NameList
from models import Site,Category
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.safestring import mark_safe

class AddGameForm(forms.Form):
	title = forms.CharField(max_length=50)
	url = forms.URLField(max_length=75,required=False)
	moderator = forms.CharField(max_length=50, widget=AutoTextBox())
	start_date = forms.DateField(widget = JQueryDateWidget())
	end_date = forms.DateField(widget = JQueryDateWidget())
	game_id = forms.CharField(max_length=100,required=False,widget=forms.HiddenInput())
	type = forms.ChoiceField([(u'full','Full Game'),
        (u'mini','Mini Game'), (u'irc','IRC Game')])
	livedToEnd=NameList(choices=[],widget=NameBox, initial=[])

	#site = forms.ModelChoiceField(Site)
class AddRoleForm(forms.Form):
	title = forms.CharField(max_length=50)
	player = forms.CharField(max_length=75,widget=AutoTextBox())
	text = forms.CharField(max_length=3000, widget=forms.Textarea)
RoleFormSet = formset_factory(AddRoleForm)


class AddTeamForm(forms.Form):
	title = forms.CharField(max_length=50,required=False)
	won = forms.BooleanField(required=False)
	choices = [(cat.title,cat.title) for cat in Category.objects.all()]
	type = forms.ChoiceField(choices=choices)
	team_id = forms.CharField(max_length=100,required=False,widget=forms.HiddenInput())
#	players = forms.MultipleChoiceField(choices=[('1','Febo'),('2','ricree'),('3','Apeiron')])
	players = NameList(choices=[],widget=NameBox, initial=[])
TeamFormSet = formset_factory(AddTeamForm, extra=1)
TeamFormSetEdit  = formset_factory(AddTeamForm,extra=0)
class LinkForm(forms.Form):
	site = forms.ChoiceField(choices=[(site.id,site.title) for site in Site.objects.all()])
	player = forms.CharField(max_length=75,widget=AutoTextBox())
