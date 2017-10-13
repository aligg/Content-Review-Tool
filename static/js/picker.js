function displayMessage() {

    $('#status-area').show();
    $('#pickerhandler').hide();
    $('#subreddit-area').hide();
 
 }

function displaySubreddits() {
        
        $('#subreddit-area').show();
    
}



//event listeners
$('#subreddit-area').hide()
$('#status-area').hide()
$('#gogo').on('click', displayMessage);
$('#inspire').on('click', displaySubreddits);





