$(document).ready(function() {
    $('form#pregame').on('submit', function(event) {
        console.log($('#mafia').val());
        $.ajax('/process', {
            type: 'POST',  // http method
            data: { mafia: $('#mafia').val() },  // data to submit
            success: function () {
                console.log('Success')
            },
            error: function () {
                console.log('Error')
            }
        }).done(function(response){
            if (response.redirect) {
                console.log(response.redirect);
                window.location = '/' + response.redirect
            }
        });
        event.preventDefault();
        
    });
});