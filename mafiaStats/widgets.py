from django import forms

class ClassedTextInput(forms.TextInput):
	"""A widget that will add an additional class to the rendered html
	Must define _init_class in classes that inherit from this"""
	_init_class = None
	def __init__(self, attrs={}):
		if self._init_class == None:
			raise NotImplementedError, "Child class did not define _init_class"
		if 'class' in attrs:
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
			'/static/js/widget/nameBox.js',)
	def render(self, name, value,attrs={},choices=()):
		if (attrs is not None) and ('id'in attrs):
			id = attrs['id']
		else:
			id = None
		if (atts is not None) and ('class' in attrs):
			classes = attrs['class']
		else:
			classes=None
		return render_to_string("widgets/nameBox.html",{'id':id ,'class':classes})
			

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
	
