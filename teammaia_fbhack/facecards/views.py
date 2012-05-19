from django.http import HttpResponse
from django_fukinbook.decorators import facebook_auth_required
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
import logging
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from facebook_client import FacebookClient
from django.views.decorators.csrf import csrf_exempt
from models import Game, Card
import simplejson

@facebook_auth_required
def canvas(request):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    
    logged_friends = []
    if sessions: 
        pks = [s.get_decoded().get('_auth_user_id') for s in sessions]  
        users = [User.objects.get(pk=p) for p in pks]
        
        client = FacebookClient(request.access_token)
        my_friends = client.get_my_friends()
        my_friends_uids = [friend.get('uid') for friend in my_friends]
        
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
        return HttpResponse('FalhaOnGame')
    
    player_waiting = len(Game.objects.filter(player1=request.user, status='w'))
    
    if player_waiting != 0:
        return HttpResponse('FalhaOnWait')
    
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
                'game_pk': games_waiting[0].pk,
                'status': 'OK'}
        
        return HttpResponse(simplejson.dumps(game))
    return HttpResponse(simplejson.dumps({'status': 'NaoTem'}))

@login_required
def refresh_my_challenge(request):
    my_challenge = Game.objects.filter(player1=request.user, status='p')
    if my_challenge:
        return HttpResponse('/play/{0}'.format(my_challenge[0].pk))
    
    return HttpResponse('AindaNao')
    
@facebook_auth_required
def play(request, game_pk):
    client = FacebookClient(request.access_token)
    my_deck = client.get_my_deck()
    for i, card in enumerate(my_deck):
        new_card = Card()
        new_card.game = Game.objects.get(pk=game_pk)
        new_card.player = request.user
        new_card.order = i
        new_card.attr1 = card.get('friend_count')
        new_card.attr2 = card.get('likes_count')
        new_card.name = card.get('name')
        new_card.pic_square = card.get('pic_square')
        new_card.save()
    
    game = Game.objects.get(pk=game_pk)
    logging.debug(game)
    if game.status != 'p':
        logging.debug('ENTREI')
        game.status = 'p'
        game.save()
    
    template_context = {'game_pk': game_pk}
    return render_to_response('play.html', template_context,
                              context_instance=RequestContext(request))

@csrf_exempt
@login_required
def finish_game(request):
    game_pk = request.POST.get('game_pk')
    if game_pk:
        game = Game.objects.get(pk=game_pk)
        game.status = 'f'
        game.save()
        return HttpResponse('OK')
    return HttpResponse('Falha')

@login_required
def check_finish(request, game_pk):
    game = Game.objects.get(pk=game_pk)
    if game.status == 'f':
        return HttpResponse('OK')
    return HttpResponse('Nao')
    
@login_required
def get_next_card(request):
    game_pk = request.GET.get('game_pk')
    deck = Card.objects.filter(player=request.user, game=game_pk)
    deck_len = len(deck)
    def return_order(card):
        return card.order
    card = min(deck, key=return_order)
    
    card_attrs = {'name': card.name,
                  'pic_square': card.pic_square,
                  'attr1': card.attr1,
                  'attr2': card.attr2,
                  'deck_len': deck_len}
    return HttpResponse(simplejson.dumps(card_attrs))
    
    
        


