from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Score
import json

@csrf_exempt
def save_score(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		user = data.get('user')
		score = data.get('score')
		if user and score is not None:
			Score.objects.create(user=user, score=score)
			return JsonResponse({'status': 'success'})
		return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
	return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
