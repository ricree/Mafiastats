from mafiastats.mafiaStats.models import Site, Game, Category, Player,Team
from django.contrib import admin

class TeamInline(admin.StackedInline):
	model = Team
	extra = 2

class GameAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, {'fields': ['title','url','moderator','site','start_date','end_date','livedToEnd']})]
	inlines = [TeamInline]

admin.site.register(Site)
admin.site.register(Game, GameAdmin)
admin.site.register(Category)
admin.site.register(Player)
admin.site.register(Team)
