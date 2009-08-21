from django import forms
from django.forms.formsets import formset_factory
from Mafiastats.mafiaStats.widgets import AutoTextBox, JQueryDateWidget,NameBox
from Mafiastats.mafiaStats.widgets import NameList
from Mafiastats.mafiaStats.models import Site,Category
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.safestring import mark_safe

class AddGameForm(forms.Form):
	title = forms.CharField(max_length=50)
	url = forms.URLField(max_length=75,required=False)
	moderator = forms.CharField(max_length=50, widget=AutoTextBox())
	start_date = forms.DateField(widget = JQueryDateWidget())
	end_date = forms.DateField(widget = JQueryDateWidget())
	type = forms.ChoiceField([(u'full','Full Game'),
        (u'mini','Mini Game'), (u'irc','IRC Game')])
	#site = forms.ModelChoiceField(Site)
class AddTeamForm(forms.Form):
	title = forms.CharField(max_length=50)
	won = forms.BooleanField(required=False)
	type = forms.MultipleChoiceField(choices=[(cat.title,cat.title) for cat in Category.objects.all()])
#	players = forms.MultipleChoiceField(choices=[('1','Febo'),('2','ricree'),('3','Apeiron')])
	players = NameList(choices=[],widget=NameBox)
TeamFormSetParent = formset_factory(AddTeamForm)
class TeamFormSet(TeamFormSetParent):
	def as_p(self):
		"""Just the as_table with as_p instead.  no idea why this doesn't already exist."""
		forms = u' '.join([form.as_p() for form in self.forms])
		return mark_safe(u'\n'.join([unicode(self.management_form), forms]))
