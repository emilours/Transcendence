from django.contrib import admin
from .models import Game, Match, PlayerMatch, CustomUser

class GameAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')

class MatchAdmin(admin.ModelAdmin):
	list_display = ('game', 'status', 'date')

class PlayerMatchAdmin(admin.ModelAdmin):
	list_display = ('player', 'score', 'is_winner')

class CustomUserAdmin(admin.ModelAdmin):
	list_display = ('display_name', 'email', 'is_online')


admin.site.register(Game, GameAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(PlayerMatch, PlayerMatchAdmin)
admin.site.register(CustomUser, CustomUserAdmin)

