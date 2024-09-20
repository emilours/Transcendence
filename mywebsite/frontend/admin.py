from django.contrib import admin
from .models import Game, Match, PlayerMatch, CustomUser

class CustomUserAdmin(admin.ModelAdmin):
	list_display = ('display_name', 'email', 'is_staff', 'is_active')

class PlayerMatchInline(admin.TabularInline):  # O StackedInline
	model = PlayerMatch
	extra = 1
	fields = ('player', 'score', 'is_winner')

class MatchAdmin(admin.ModelAdmin):
	list_display = ('game', 'date', 'status', 'details', 'get_players_with_scores', 'get_winner')

	inlines = [PlayerMatchInline]

	def get_players_with_scores(self, obj):
		return ", ".join([f"{player_match.player.display_name} ({player_match.score})" for player_match in obj.playermatch_set.all()])
	get_players_with_scores.short_description = 'Players with Scores'

	def get_winner(self, obj):
		winners = obj.playermatch_set.filter(is_winner=True)
		if winners.exists():
			return ", ".join([winner.player.display_name for winner in winners])
		return 'No winner'
	get_winner.short_description = 'Winner'

class GameAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')
	search_fields = ('name',)

admin.site.register(Game, GameAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
