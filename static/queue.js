

var currentReview = 1


//hide review objects 2-5
for (var i = 2; i<=5; i++){ 
    $('#reviewobject-'+i).hide();
    $('#formobject-'+i).hide();
}


//hide submit button until reviewobject 5,
    $('#submit').hide();
    $('.back').hide();
   

//if nothing left to review
function checkBatchSize(){
    if (batchsize == 0) 
    {
    alert("You've booted the queue! Redirecting home.");
    window.location.href = "/"
    }
}

//blurs image
function blurImage(){
    console.log("We got here ya yayaya");
    $('.imageforreview').blur();
}

//iterate through objects and hide previous display next one
function displayNextReview() {
    checkBatchSize()
    if (currentReview < batchsize)
    {
        $('#reviewobject-'+currentReview).hide();
        $('#formobject-'+currentReview).hide();
        currentReview++;  
        $('#reviewobject-'+currentReview).show();
        $('#formobject-'+currentReview).show();
        $('.next').show();
        $('#submit').hide();

    }
    if (currentReview == batchsize) {
        $('.next').hide();
        $('#submit').show();
    }
    $('.back').show()

}

//Same as displayNext but allows for prior button
function displayPriorReview() {
    checkBatchSize()
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
    else {
        $('.back').hide()
    }
}

//event listeners
$(document).ready(checkBatchSize);
$('.switch').on('click', blurImage);
$('.next').on('click', displayNextReview);
$('.back').on('click', displayPriorReview);


//hotkeys while in queue
$(document).keypress(function(e) {
    if($(".notes").is(":focus")) return;
    {
        if(e.which == 103) //g
        { 
        $('.next').trigger('click');
        }
        if(e.which == 112) //p
        { 
        $('.submit').trigger('click');
        }
        if(e.which == 99)  //c
        { 
        $('.back').trigger('click');
        }
        if(e.which == 113) //q
        {
        $('.navbutton-home').trigger('click');
        }
    }
});



