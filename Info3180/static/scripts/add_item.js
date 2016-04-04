var imgs;
$(document).ready(function() {
    
    $('#url').focusout(function() {
        var regex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
            $.ajax(
               {
                   url: '/api/thumbnail/process?url=' + $('#url').val(),
                   method: 'GET',
               })
               .done(function(response) {
                   imgs = response['response']['data']['thumbnails'];
                   $('.imgs').empty();
                   if (response['response']['error'] != null) {
                       $('.imgheading').text('No images could be found. Try another url or a default image will be used');
                   } else {
                       console.log('lel' + response['response']['data']['thumbnails']);
                       $('.imgheading').text('Select Image To Use For Item Below');
                       var numOfRows = Math.ceil(imgs.length / 3);
                       for(var i = 1; i <= numOfRows; i++) {
                           $('.imgs').append(
                               '<label>' +
                            '<input type="radio" name="thumbnail" checked value="' + imgs[i] + '"/>' + 
                            '<img style="width: 180px; height: 180px;" class="img" src="' + imgs[1*i] + '"class="col s4"></img>' +
                  '</label>' +
                  '<label>' +
                    '<input type="radio" name="thumbnail" value="' + imgs[i] + '"/>' + 
                    '<img style="width: 180px; height: 180px;" class="img" src="' + imgs[2*i] + '"class="col s4"></img>' +
                  '</label>' +
                  '<label>' +
                    '<input type="radio" name="thumbnail" value="' + imgs[i] + '"/>' + 
                    '<img style="width: 180px; height: 180px;" class="img" src="' + imgs[3*i] + '"class="col s4"></img>' +
                  '</label>');
                       }
                   }
               })
               .fail(function(jqXHR, txt) {
                   
               });
        // } else {
        //     $('#url').addClass('red lighten-2');
        //     $('#url').val('Enter a valid url');
        // }
        
    });
    // $('#url').focus(function() {
    //     if ($('#url').hasClass('red')) {
    //         $('#url').removeClass('red lighten-2');
    //         $('#url').val('');
    //     }
    // });
    

});