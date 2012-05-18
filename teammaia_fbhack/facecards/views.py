# Create your views here.
from django.http import HttpResponse
from django_fukinbook.decorators import facebook_auth_required
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django_fukinbook.graph_api import GraphAPI
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import logging
import datetime
from django.utils import timezone

@facebook_auth_required
def canvas(request):
    request.session.set_expiry(60)
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    pks = [s.get_decoded().get('_auth_user_id') for s in sessions]
    users = [User.objects.get(pk=p) for p in pks]
    
    api = GraphAPI(request.access_token)
    fql = '''SELECT uid FROM user WHERE 
    uid IN (SELECT uid2 FROM friend WHERE uid1 = me())'''
    my_friends = api.get(path='fql', fql=fql)
    
    my_friends_uids = [friend.get('uid') for friend in my_friends]
    
    logged_friends = []
    for user in users:
        if int(user.username) in my_friends_uids:
            logged_friends.append(user)
    
    template_context = {'logged_friends': logged_friends}
    return render_to_response('index.html', template_context,
                              context_instance=RequestContext(request))