from postmarkup import render_bbcode
from coffin import template

register = template.Library()

@register.filter()
def bbcode(text):
	return render_bbcode(text)
