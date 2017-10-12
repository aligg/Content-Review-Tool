function displayMessage() {
    $('#status-area').flash_message({
        text: 'We\'re going as fast as we can!',
        how: 'append'
    });
}


$('#gogo').click(displayMessage);

//still need to work on this, not functional

