$(function () {
    $('.entry-background-img').removeClass('d-none');
    $('.entry-background-img').addClass('d-flex');

    $('#signin').on('click', function(){
        $('#entry-info').removeClass('d-flex');
        $('#entry-info').addClass('d-none');
        setTimeout(function(){
            $('#entry-form').removeClass('d-none');
            $('#entry-form').addClass('d-flex');
        }, 300);
    });

    $('#signup').on('click', function(){
        $('#entry-info').removeClass('d-flex');
        $('#entry-info').addClass('d-none');
        setTimeout(function(){
            $('#entry-signup-form').removeClass('d-none');
            $('#entry-signup-form').addClass('d-flex');
        }, 300);
    });

    $('button[name="entry-back"]').on('click', function(){
        $('#entry-form').removeClass('d-flex');
        $('#entry-form').addClass('d-none');
        $('#entry-signup-form').removeClass('d-flex');
        $('#entry-signup-form').addClass('d-none');
        $('#entry-callback').removeClass('d-flex');
        $('#entry-callback').addClass('d-none');
        $("#entry-signup-form")[0].reset();
        $('#entry-callback-list').html('');
        $("#entry-form")[0].reset();
        setTimeout(function(){
            $('#entry-info').removeClass('d-none');
            $('#entry-info').addClass('d-flex');
        }, 300);
    });

    $('#logout').on('click', function(){
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        url = '/user-logout/'
        $.ajax({
            url: url,
            type: 'post',
            headers: {'X-CSRFToken': csrftoken},
            dataType: 'json',
            success: function (data) {
                if(data['logout'] == true) {
                    $('#user-info-login-bt').removeClass('d-none');
                    $('#user-profile').addClass('d-none');
                    $('#not-user-profile').removeClass('d-none');
                    $('#user-info-img-not-profile').removeClass('d-none');
                    $('#user-info-img').addClass('d-none');
                    window.location.href = 'login';
                }
            }
        });
    });

   $("#entry-form").on("submit", function () {
        event.preventDefault();
        console.log('redirect url: ', redirect_url)
        var form = $(this);
        var username = $('input[name="login"]').val();
        var password = $('input[name="password"]').val();
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        if (username == '') {
            console.log('empty login string');
            return;
        } else if (password == '') {
            console.log('empty password string');
            return;
        }
        var url = 'user-auth/';
        console.log('url: ', url);
        data = {
            'username': username,
            'password': password,
        }
        console.log('data: ', data);
        $.ajax({
            url: url,
            type: 'post',
            headers: {'X-CSRFToken': csrftoken},
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (data) {
                console.log('response data: ', data)
                console.log(data['info'])
                if (data['passed'] == true) {
                    console.log(data['redirect'])
                    window.location.href = redirect_url
                } else {
                    $('.modal-body p').text(data['info'])
                    $('#entry-form').removeClass('d-flex');
                    $('#entry-form').addClass('d-none');
                    setTimeout(function(){
                        $('#entry-info').removeClass('d-none');
                        $('#entry-info').addClass('d-flex');
                    }, 300);
                }
            }
        });

   });

   $("#entry-signup-form").on("submit", function () {
        event.preventDefault();
        $('#entry-callback').removeClass('d-flex');
        $('#entry-callback').addClass('d-none');
        var form = $(this);
        var username = $('#entry-signup-form input[name="username"]').val();
        var email = $('#entry-signup-form input[name="email"]').val();
        var first_name = $('#entry-signup-form input[name="first_name"]').val();
        var last_name = $('#entry-signup-form input[name="last_name"]').val();
        var password = $('#entry-signup-form input[name="setup_password"]').val();
        var confirm = $('#entry-signup-form input[name="confirm_password"]').val();
        var privacy_check = $("#entry-signup-form input[type='checkbox']").is(':checked');
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        if (username == '') {
            console.log('empty login string');
            return;
        } else if (email == '') {
            console.log('empty email string');
            return;
        } else if (password == '') {
            console.log('empty password string');
            return;
        } else if (confirm == '') {
            console.log('empty password confirm string');
            return;
        } else if (privacy_check == false) {
            console.log('privacy checkbox not checked');
            return;
        }
        var url = 'user-signup/';
        console.log('url: ', url);
        data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'confirm': confirm,
            'privacy_check': privacy_check
        }
        console.log('data: ', data);
        $.ajax({
            url: url,
            type: 'post',
            headers: {'X-CSRFToken': csrftoken},
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (data) {
                console.log('response data: ', data);
                console.log(data['info']);
                if (data['created'] == true) {
                    $('#entry-callback').css('color', '#2dffb1');
                } else {
                    $('#entry-callback').css('color', '#ffc107');
                }
                info = '';
                for(var i = 0; i < data['info'].length; i++)
                    info += '<li>' + data['info'][i] + '</li>';
                $('#entry-callback-list').html(info);
                $('#entry-callback').removeClass('d-none');
                $('#entry-callback').addClass('d-flex');
            }
        });

   });

});