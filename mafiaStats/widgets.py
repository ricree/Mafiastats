from django import forms

class AutoTextBox(forms.TextInput):
	def __init__(self,attrs={}):
		if 'class' in attrs:
			attrs['class'] = ' '.join([attrs['class'], 'AutoSuggestBox'])
		else:
			attrs['class'] = 'AutoSuggestBox'
		super(AutoTextBox,self).__init__(attrs=attrs)
	class Media:
		css= {'all':('/static/js/JSONSuggestBox/jsonSuggest.css')}
		js = ('/static/js/jquery-1.3.2.min.js',
				'/static/js/JSONSuggestBox/json2.js',
				'/static/js/JSONSuggestBox/jquery.jsonSuggest-dev.js',
				'/static/js/widget/suggest.js',
				'/static/js/JSONSuggestBox/testData/testData.js')
