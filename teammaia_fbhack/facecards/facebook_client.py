from django_fukinbook.graph_api import GraphAPI


class FacebookClient(GraphAPI):
    def get_my_friends(self):
        fql = '''SELECT uid FROM user WHERE 
        uid IN (SELECT uid2 FROM friend WHERE uid1 = me())'''
        
        my_friends = self.get(path='fql', fql=fql)
        return my_friends