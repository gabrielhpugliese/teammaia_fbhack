$(document).ready(function(){
	setTimeout('keep_alive()', 5*1000);
});
	
function keep_alive() {
	var remote_url = '/keep_alive';
	$.get(remote_url, function(data) { 
		setTimeout('keep_alive()', 5*1000);
	});
}