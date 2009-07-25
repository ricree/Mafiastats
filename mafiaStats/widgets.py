from django import forms
from django.template.loader import render_to_string

class ClassedTextInput(forms.TextInput):
	"""A widget that will add an additional class to the rendered html
	Must define _init_class in classes that inherit from this"""
	_init_class = None
	def __init__(self, attrs={}):
		if self._init_class == None:
			raise NotImplementedError, "Child class did not define _init_class"
		if ('class' in attrs):
			if (self._init_class not in attrs['class']):
				attrs['class'] = ' '.join([attrs['class'],self._init_class])
		else:
			attrs['class'] = self._init_class
		super(forms.TextInput,self).__init__(attrs=attrs)

class AutoTextBox(ClassedTextInput):
	_init_class = 'AutoSuggestBox'
	class Media:
		css= {'all':('/static/js/JSONSuggestBox/jsonSuggest.css',)}
		js = ('/static/js/jquery-1.3.2.min.js',
				'/static/js/JSONSuggestBox/json2.js',
				'/static/js/JSONSuggestBox/jquery.jsonSuggest-dev.js',
				'/static/js/widget/suggest.js',
				'/static/js/JSONSuggestBox/testData/testData.js')
class JQueryDateWidget(ClassedTextInput):
	_init_class = 'DateInput'
	class Media:
		css={'all':('/static/css/redmond/jquery-ui-1.7.2.custom.css',)}
#'http://jqueryui.com/latest/themes/ui-lightness/ui.all.css',)}
#/statis/css/ui-lightness/jquery-ui-1.7.2.custom.css',)}
		js= ('/static/js/jquery-1.3.2.min.js',
			'/static/js/jquery-ui-1.7.2.custom.min.js',
			'/static/js/widget/datePicker.js')

class NameBox(forms.SelectMultiple):
	class Media:
		js=('/static/js/jquery-1.3.2.min.js',
			'/static/js/widget/nameBox.js',
			'/static/js/jquery.contextMenu.js')
		css={'all':('/static/css/jquery.contextMenu.css',)}
	def render(self, name, value,attrs={},choices=()):
		if (attrs is not None) and ('id'in attrs):
			id = attrs['id']
		else:
			id = ""
		if (attrs is not None) and ('class' in attrs):
			classes = attrs['class']
		else:
			classes=""
		return render_to_string("nameBoxWidget.html",{'box_id':id+"_box" ,'box_class':classes+" NameBox",'box_name':name+"_box",'result_name':name,'text_name':name+"_text",'text_id':id+'_text','text_class':classes+" NameBoxText"})
			

class NameEntryBox(forms.MultiWidget):
	_init_class='NameChooser'
	def __init__(self, attrs={}):
		widgets = (forms.TextInput(), forms.SelectMultiple(choices=[]))
		if 'class' in attrs:
			attrs['class'] = ' '.join([attrs['class'],self._init_class])
		else:
			attrs['class'] = self._init_class
		super(forms.TextInput,self).__init__(attrs=attrs)
	class Media:
		js=('/static/js/jquery-1.3.2.min.js',)
	
class NameList(forms.MultipleChoiceField):
	def clean(self,value):
		value = unicode(value[0])
		if((type(value) is str) or(type(value) is unicode)):
			value = value.split(',')
		return value
