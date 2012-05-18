$(document).ready(function(){
	setTimeout('keep_alive()', 40);
});
	
function keep_alive() {
	var remote_url = '/keepalive';
	$.get(remote_url, function(data) { 
		setTimeout('keep_alive()', 40); 
	});
}