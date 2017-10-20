function signInCallback(authResult) {
    if (authResult['code']) {
        // Hide sign in button as user is authorized

        $('#signinButton').attr("style", 'display: none')
        $('#content_panel').html('logging in please wait')
        /* Send the one-time-use code to the server, if the server responds,
        write a 'login successful message to the web page and then redirect
        back to the main restaurants page*/
        $.ajax({
            type: 'POST',
            url: '/gconnect?state=' + STATE,
            processData: false,
            data: authResult['code'],
            contentType: 'application/octet-stream; charset=utf-8',
            success: function (result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    location.reload()
                } else if (authResult['error']) {
                    console.log('There was an error: ' + authResult['error']);
                    $('#content_panel').html('login failed')
                } else {
                    $('#content_panel').html(
                        'Failed to make a server-side call');
                }
            }
        });
    }
}
function signOutGoogleAcc() {
        // Hide sign in button as user is authorized

        $('#logout').attr("style", 'display: none')
        $('#content_panel').html('logging out please wait')
        /* Send the one-time-use code to the server, if the server responds,
        write a 'login successful message to the web page and then redirect
        back to the main restaurants page*/
        $.ajax({
            type: 'POST',
            url: '/gdisconnect/',
            success: function (result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    location.reload()
                } else if (authResult['error']) {
                    console.log('There was an error: ' + authResult['error']);
                    $('#content_panel').html('login failed')
                } else {
                    $('#content_panel').html(
                        'Failed to make a server-side call');
                }
            }
        });
}

// hide or show category menu list
function hide_show_menu(){
  $("nav").toggle();
  $("section").toggle();
}

// restoring effect on normal size
$(document).ready(function () {
$(window).on('resize', function (e) {
        if ($(window).width() > 1284) {
            $('nav').show();
            $('section').show();
        }
        else {
          $('nav').hide();
          $('section').show();
        }
  });
});
