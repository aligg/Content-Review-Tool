

var currentReview = 1

//hide review objects 2-5
for (var i = 2; i<=5; i++){ 
    $('#reviewobject-'+i).hide();
    $('#formobject-'+i).hide();
}


//hide submit button until reviewobject 5,
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
function displayPriorReview() {
    if (currentReview > 1)  
    {   
        $('.back').show()
        $('#reviewobject-'+currentReview).hide();
        $('#formobject-'+currentReview).hide();
        currentReview--;
        $('#reviewobject-'+currentReview).show();
        $('#formobject-'+currentReview).show();
        $('.back').show()
    }
    
}

$('.next').on('click', displayNextReview);
$('.back').on('click', displayPriorReview);


$(document).keypress(function(e) {
    if($(".notes").is(":focus")) return;
    {
        if(e.which == 103) 
        { 
        $('.next').trigger('click');
        }
    }
});

