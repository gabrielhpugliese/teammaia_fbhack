from django.http import HttpResponse
from django_fukinbook.decorators import facebook_auth_required
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import logging
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from facebook_client import FacebookClient
from django.views.decorators.csrf import csrf_exempt
from models import Game
import simplejson

@facebook_auth_required
def canvas(request):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    pks = [s.get_decoded().get('_auth_user_id') for s in sessions]
    users = [User.objects.get(pk=p) for p in pks]
    
    client = FacebookClient(request.access_token)
    my_friends = client.get_my_friends()
    my_friends_uids = [friend.get('uid') for friend in my_friends]
    
    logged_friends = []
    for user in users:
        if int(user.username) in my_friends_uids:
            logged_friends.append(user)
    
    template_context = {'logged_friends': logged_friends}
    return render_to_response('index.html', template_context,
                              context_instance=RequestContext(request))
    
@login_required
def keep_alive(request):
    request.session.set_expiry(6000)
    
    return HttpResponse('OK')

@csrf_exempt
@login_required
def game_request(request):
    friend_id = request.POST["friend"]
    logging.info(friend_id)
    
    playerOnGame = len(Game.objects.filter(player1__pk=friend_id, status='p'))
    playerOnGame += len(Game.objects.filter(player2__pk=friend_id, status='p'))
    
    if playerOnGame != 0:
        return HttpResponse('Falha')
    
    logging.info("usuario disponivel")
    
    u1 = request.user
    u2 = User.objects.filter(pk=friend_id)[0]

    try:
        game = Game(player1 = u1, player2 = u2, status='w').save()
    except:
        return HttpResponse('Falha')
        
    return HttpResponse('OK')

@login_required
def refresh_games(request):
    games_waiting = Game.objects.filter(player2=request.user, status='w')
    if games_waiting:
        opponent = games_waiting[0].player1
        opponent_name = '%s %s' % (opponent.first_name, opponent.last_name)
        game = {'opponent_name': opponent_name,
                'game_pk': games_waiting[0].pk}
        
        return HttpResponse(simplejson.dumps(game))
    return HttpResponse('NaoTem')

@login_required
def play(request):
    
    return render_to_response('play.html', template_context,
                              context_instance=RequestContext(request))





