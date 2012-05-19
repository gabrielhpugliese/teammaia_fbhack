from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    PLAYING='p'
    WAITING='w'
    FINISHED='f'
    STATUS = ((PLAYING, u'Playing'), (WAITING, u'Waiting'), 
              (FINISHED, u'Finished'),)
    
    player1 = models.ForeignKey(User, related_name='player1')
    player2 = models.ForeignKey(User, related_name='player2')
    turn = models.ForeignKey(User, related_name='turn', default=None, null=True)
    status = models.CharField(max_length=1, choices=STATUS, verbose_name='Game status')
    lock = models.BooleanField(default=False)
    
class Round(models.Model):
    game = models.ForeignKey(Game)
    active_player = models.OneToOneField(User, related_name='active_player')
    active_player_card = models.CharField(max_length=50)
    opponent_player_card = models.CharField(max_length=50)
    winner = models.OneToOneField(User, related_name='winner')

class Card(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(User)
    order = models.IntegerField()
    name = models.CharField(max_length=150)
    attr1 = models.IntegerField()
    attr2 = models.IntegerField()
    pic_square = models.URLField()
    
    
    