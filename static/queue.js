

var currentReview = 1

//hide review objects 2-5
for (var i = 2; i<=5; i++){ 
    $('#reviewobject-'+i).hide();
    $('#formobject-'+i).hide();
}
//hide submit button until reviewobject 5
    $('#submit').hide()

//iterate through objects and hide previous display next one
function displayNextReview() {
    if (currentReview < 5)
    {
        $('#reviewobject-'+currentReview).hide();
        $('#formobject-'+currentReview).hide();
        currentReview++;  
        $('#reviewobject-'+currentReview).show();
        $('#formobject-'+currentReview).show();
        $('.next').show();
        $('#submit').hide();

    }
    if (currentReview == 5) {
        $('.next').hide();
        $('#submit').show();
    }

}
//call function on next button click
$('.next').on('click', displayNextReview);


$(document).keypress(function(e) {
    if(e.which == 103) { 
        $('.next').trigger('click');
    }
});

