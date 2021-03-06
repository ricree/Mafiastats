from django import forms
from django.forms.formsets import formset_factory
from widgets import AutoTextBox, JQueryDateWidget,NameBox,BadgeConfig,ColorBox
from widgets import NameList
from models import Site,Category
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.safestring import mark_safe
from django.conf import settings
import os
import pyggy
import marshal

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
class BadgeForm(forms.Form):
	templates= {'original':"[%s%s%s]%s%s $n+2b\n(Mafia Stats: )b$w Wins in $t Games\n",'minimal':"[%s%s%s]%s%sMafia Record: $w-$l\n",'moderator':"[%s%s%s]%s%s$m Games Moderated\nWith $p Total Players\n"}
	tempChoices = [(k,k) for k in templates]
	title = forms.CharField(max_length=50,initial="Custom Badge")
	config = forms.CharField(max_length=200,label="Format String",required=False)
	players = forms.MultipleChoiceField(choices=[],label="Players to Track",required=False)
	preset = forms.ChoiceField(choices= tempChoices,required=False,initial="original")
	background = forms.ChoiceField(choices=[("transparent","transparent"),("gradient","gradient")],required=False,initial="gradient")
	font_size = forms.ChoiceField(choices=[(i,i) for i in range(8,25)],initial=11)
	text_color = forms.CharField(max_length=10,required=False,initial="#F5F5F5", widget=ColorBox())
	top_color = forms.CharField(max_length=10,required=False,initial="#010085", widget=ColorBox())
	bottom_color = forms.CharField(max_length=10,initial="#1b5af6", required=False,widget=ColorBox())
	#def __init__(self,*args,**kwargs):
	#	print self.base_fields['players']
	#	print self.base_fields['players'].choices
	#	choices = kwargs['choices']
	#	self.base_fields['players']  = forms.MultipleChoiceField(choices=choices)
	#	super(forms.Form,self).__init__(self,*args,**kwargs)
	def buildBadgeFromTemplate(self):
		templateName = self.cleaned_data['preset']
		template = BadgeForm.templates[templateName]
		background = self.cleaned_data['background']
		top  = self.cleaned_data['top_color']
		bottom = self.cleaned_data['bottom_color']
		text = self.cleaned_data['text_color']
		size = self.cleaned_data['font_size']
		params = {'template':templateName,'background':background,'color1':top,'color2':bottom,'text':text,'size':size}
		return str(params)
	def clean(self):
		if (('config' in self.cleaned_data) and (self.cleaned_data['config'])):
			value = self.cleaned_data['config']
			custom = False
		else:
			value = self.buildBadgeFromTemplate()
			custom = True
		self.cleaned_data['config'] = value
		self.custom_format = custom
		return self.cleaned_data
		
	def clean_players(self):
		if ('players' not in self.cleaned_data) or (not self.cleaned_data['players']):
			self.cleaned_data['players'] = [p[0] for p in self.fields['players'].choices]
		return self.cleaned_data['players']
	def clean_config(self):
		if (('config' in self.cleaned_data) and (self.cleaned_data['config'])):
			value = self.cleaned_data['config']
			value = value.replace(r'\n','\n')
			if(value[-1]!="\n"):#grammar requires a newline at end
				value = value+"\n"
			startDir = os.getcwd()
			os.chdir(settings.SITE_ROOT)
			l,ltab = pyggy.getlexer("badge.pyl")
			parser,ptab = pyggy.getparser("badge.pyg")
			l.setinputstr(value)
			parser.setlexer(l)
			os.chdir(startDir)
			try:
				parser.parse()
			except Exception:
				raise forms.ValidationError("Must be a valid config string")
			return value

