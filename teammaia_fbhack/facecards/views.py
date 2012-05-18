# Create your views here.
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

@login_required
def keep_alive(request):
    request.session.set_expiry(60)
    
    return HttpResponse('OK')

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
    
    



