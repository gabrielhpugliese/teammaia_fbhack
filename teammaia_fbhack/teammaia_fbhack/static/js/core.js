$(document).ready(function(){
	setTimeout('keep_alive()', 5*1000);
});
	
function keep_alive() {
	var remote_url = '/keep_alive';
	$.get(remote_url, function(data) { 
		setTimeout('keep_alive()', 5*1000);
	});
}

function refresh_my_challenge(){
	$.get('/refresh_my_challenge', function(data){
		setTimeout('refresh_my_challenge()', 1*1000);
		if(data != 'AindaNao'){
			self.location = data;
		}
	})
}

function refresh_games() {
	$.get('/refresh_games', function(data){
		setTimeout('refresh_games()', 1*1000);
		data = $.parseJSON(data);
		var list = $('#game_list ul')
		if(data.status != 'NaoTem'){
			var achou = false;
			list.find('li').each(function(i, l){
				if($(this).text().trim() == data.opponent_name){
					achou = true;
				}
			});
			if(achou == false){
				list.append('<li>'+data.opponent_name+'</li><a href="/play/'+data.game_pk+'">Accept</a>');
			}
		}
	});
}






