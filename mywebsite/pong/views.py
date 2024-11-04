from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from frontend.models import Game, Match, PlayerMatch, CustomUser, FriendRequest, FriendList
import json, asyncio
from asgiref.sync import sync_to_async
from django.db.models import Q

@login_required
def pong(request):
	context = {}
	if request.user.is_authenticated:
		username = request.user.display_name
		avatar = request.user.avatar.url
		print(f"username: {username}, avatar: {avatar}")
		context = {
			'username': username,
			'avatar': avatar
		}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', context, request=request)
		return JsonResponse({'html': html, 'username': username, 'avatar': avatar})
	return render(request, 'base.html')


@csrf_exempt
def SaveLocalPongMatch(request):
	if request.method == 'POST':
		try:
			print('--------HERE--------')
			if request.user.is_authenticated:
				user = request.user
				print(f"[PONG LOG] type of user: {type(user)}")

			data = json.loads(request.body)

			score = data.get('score')
			game_name = 'pong'
			status = 'completed'
			description = 'pong local'

			print('user_id', user.id, 'score', score, 'game_name', game_name)

			if user and score is not None:
				game, _ = Game.objects.get_or_create(name=game_name, description=description)
				match = Match.objects.create(game=game, status=status, details=description)
				PlayerMatch.objects.create(player=user, match=match, score=score, is_winner=True)

				# TODO: Add score or remove to CustomUser
				return JsonResponse({'status': 'success'})
			return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
	return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# needs the CustomUser
@sync_to_async
def get_user_friend_list(user):
    try:
        friendlist = FriendList.objects.get(user=user)
        if friendlist.exists():
            return [
                friend.channel_name
                for friend in friendlist
            ]
    except FriendList.DoesNotExist:
        return []

@sync_to_async
def get_user_channel_name(user):
    return ([user.channel_name])

@sync_to_async
def update_channel_name(user, channel_name):
      user.channel_name = channel_name
      user.save(update_fields=['channel_name'])

@sync_to_async
def session_close(user):
    user.active_sessions -= 1

    if user.active_sessions == 0:
        user.is_online = False

    user.save(update_fields=['active_sessions', 'is_online'])

@sync_to_async
def session_open(user):
    user.active_sessions += 1
    user.is_online = True
    user.save(update_fields=['active_sessions', 'is_online'])

@sync_to_async
def check_friend_request_update(user):
    pending_requests = FriendRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status__in=['accepted', 'declined', 'pending']
    )

    if pending_requests.exists():
        return [
            {
                "id": friend_request.id,
                "sender": friend_request.sender.channel_name,
                "receiver": friend_request.receiver.channel_name,
                "status": friend_request.status
            }
            for friend_request in pending_requests
        ]
    return []

@sync_to_async
def check_friendlist_update(user):
    try:
        friendlist = FriendList.objects.get(user=user)
        return friendlist.friend_count()
    except FriendList.DoesNotExist:
        return 0

@sync_to_async
def check_friends_statuses_update(user):
    try:
        user_friend_list = user.friend_list
        friends = user_friend_list.friends.all()

        friend_statuses = [
            {
                "id": friend.id,
                "display_name": friend.display_name,
                "channel_name": friend.channel_name,
                "is_online": friend.is_online,
                "avatar": friend.avatar.url
            }
            for friend in friends
        ]

        return friend_statuses

    except FriendList.DoesNotExist:
        return []
