from django_fukinbook.graph_api import GraphAPI


class FacebookClient(GraphAPI):
    def get_my_friends(self):
        fql = '''SELECT uid FROM user WHERE 
        uid IN (SELECT uid2 FROM friend WHERE uid1 = me())'''
        
        my_friends = self.get(path='fql', fql=fql)
        return my_friends
    
    def get_my_deck(self, limit=20):
        fql = '''SELECT uid, name, friend_count, likes_count, pic_square
        FROM user WHERE uid 
        IN (SELECT uid2 FROM friend WHERE uid1 = me())'''
        my_friends = self.get(path='fql', fql=fql)
        
        my_deck = []
        for friend in my_friends:
            if limit > 0 and friend.get('friend_count') and friend.get('likes_count'):
                my_deck.append(friend)
                limit -= 1
        
        return my_deck