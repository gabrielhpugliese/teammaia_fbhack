from django.forms.models import model_to_dict
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
import random
from django.core import serializers

def update_logged_friends_list(access_token):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    
    logged_friends = []
    if sessions: 
        pks = [s.get_decoded().get('_auth_user_id') for s in sessions]  
        users = [User.objects.get(pk=p) for p in pks if p != None]
        
        client = FacebookClient(access_token)
        my_friends = client.get_my_friends()
        my_friends_uids = [friend.get('uid') for friend in my_friends]
        
        for user in users:
            if int(user.username) in my_friends_uids:
                logged_friends.append(user)
    return logged_friends
    


@facebook_auth_required
def canvas(request):
    logged_friends = update_logged_friends_list(request.access_token)
    template_context = {'logged_friends': logged_friends}
    return render_to_response('index.html', template_context,
                              context_instance=RequestContext(request))

@facebook_auth_required
def ajax_update_logged_friends(request):
    logged_friends = update_logged_friends_list(request.access_token)
    
    users = []
    for user in logged_friends:
        user_name = '{0} {1}'.format(user.first_name, user.last_name)
        users.append({'friend_id': user.pk, 'name': user_name, 'pic_square': user.get_profile().pic_square})
 
    
    data = simplejson.dumps(users)    
    return HttpResponse(data)
        
    
@login_required
def keep_alive(request):
    request.session.set_expiry(60)
    
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
        game = Game(player1 = u1, player2 = u2, status='w', turn=None).save()
    except Exception, e:
        logging.warn(e)
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
        if random.randint(1,2) == 1:
            game.turn = game.player1
        else:
            game.turn = game.player2
        game.save()
    
    if game.player1 == request.user:
        opponent_user = game.player2
    else:
        opponent_user = game.player1
        
    template_context = {'game_pk': game_pk, 'me': request.user, 
                        'opponent': opponent_user}
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

def return_order(card):
    return card.order

@login_required
def get_next_card(request):
    game_pk = request.GET.get('game_pk')
    deck = Card.objects.filter(player=request.user, game=game_pk)
    my_deck_len = len(deck)
    card = min(deck, key=return_order)
    
    card_attrs = {'name': card.name,
                  'pic_square': card.pic_square,
                  'attr1': card.attr1,
                  'attr2': card.attr2,
                  'my_deck_len': my_deck_len}
    return HttpResponse(simplejson.dumps(card_attrs))
    
@login_required
def get_turn(request, game_pk):
    turn = Game.objects.get(pk=game_pk).turn
    if turn == request.user:
        return HttpResponse('OK')
    return HttpResponse('Nao')
        
@login_required
def resolve_round(request):
    attr = request.GET.get('attr')
    game_pk = request.GET.get('game_pk')
    game = Game.objects.get(pk=game_pk)
    if game.turn != request.user or game.lock == True:
        return HttpResponse(simplejson.dumps({'status': 'Falha'}))
    my_deck = Card.objects.filter(player=request.user, game=game)
    opponent_user = None
    if game.player1 == request.user:
        opponent_user = game.player2
    else:
        opponent_user = game.player1
    opponent_deck = Card.objects.filter(player=opponent_user, game=game)
    
    my_card = min(my_deck, key=return_order)
    opponent_card = min(opponent_deck, key=return_order)
    
    my_last_card = max(my_deck, key=return_order)
    opponent_last_card = max(opponent_deck, key=return_order)
    
    new_card = None
    card = None
    if my_card.__getattribute__(attr) >= opponent_card.__getattribute__(attr):
        
        my_card.order = my_last_card.order + 2
        my_card.save()
        logging.debug('MY_CARD_ORDER = %s' % my_card.order)
        new_card = Card(player=request.user,order=my_last_card.order + 1,
                        attr1=opponent_card.attr1, attr2=opponent_card.attr2,
                        name=opponent_card.name,pic_square=opponent_card.pic_square,
                        game=game) 
        new_card.save()
        opponent_card.delete()
        logging.debug('OPPONENT_CARD_ORDER = %s' % new_card.order)
        game.turn = request.user
        card = {'name': new_card.name,
            'pic_square': new_card.pic_square,
            'attr1': new_card.attr1,
            'attr2': new_card.attr2}
    else:
        opponent_card.order = opponent_last_card.order + 1
        opponent_card.save()
        new_card = Card(player=opponent_user,order=opponent_last_card.order + 2,
                        attr1=my_card.attr1, attr2=my_card.attr2,
                        name=my_card.name,pic_square=my_card.pic_square,
                        game=game)
        new_card.save()
        logging.debug('OPPONENT_CARD_ORDER = %s' % opponent_card.order)
        my_card.delete()
        logging.debug('MY_CARD_ORDER = %s' % new_card.order)
        game.turn = opponent_user
        card = {'name': opponent_card.name,
            'pic_square': opponent_card.pic_square,
            'attr1': opponent_card.attr1,
            'attr2': opponent_card.attr2}
        
    game.last_turn = request.user    
    game.lock = True
    game.save()
    
    my_deck = Card.objects.filter(player=request.user, game=game)
    
    if len(my_deck) == 30:
        game.status = 'f'
        game.save()
        return HttpResponse(simplejson.dumps({'status': 'Ganhei', 'card': card}))
    
    
    return HttpResponse(simplejson.dumps({'status': 'OK', 'card': card}))
    
@login_required
def get_lock(request):
    game_pk = request.GET.get('game_pk')
    game = Game.objects.get(pk=game_pk)
    if game.last_turn != request.user and game.lock == True:
        game.lock = False
        game.save()
        my_deck = Card.objects.filter(player=request.user, game__pk=game_pk)
        new_card = None
        opponent_user = None
        if game.player1 == request.user:
            opponent_user = game.player2
        else:
            opponent_user = game.player1
        if game.turn != request.user:
            new_card = max(Card.objects.filter(player=opponent_user, game__pk=game_pk), key=return_order)
        else:
            new_card = max(Card.objects.filter(player=request.user, game__pk=game_pk), key=return_order)
            
        card = {'name': new_card.name,
                'pic_square': new_card.pic_square,
                'attr1': new_card.attr1,
                'attr2': new_card.attr2}
        if len(my_deck) == 10:
            return HttpResponse(simplejson.dumps({'status': 'Perdi', 'card': card}))
        return HttpResponse(simplejson.dumps({'status': 'OK', 'card': card}))
    
    return HttpResponse(simplejson.dumps({'status': 'AindaNao'}))
      
