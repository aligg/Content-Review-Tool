function displayMessage() {
    
    $('#status-area').show();
    $('#pickerhandler').hide();
 
 }

function displaySubreddits() {
        
        $('#subreddit-area').show().delay(7000).fadeOut();
    

}



//event listeners
$('#subreddit-area').hide()
$('#status-area').hide()
$('#gogo').on('click', displayMessage);
$('#inspire').on('click', displaySubreddits);





