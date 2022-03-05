$(function() {
    new ClipboardJS('.clipboard');

    is_run = is_run=='True' ? true : false
    $('#parser-form').on('submit', function() {
        event.preventDefault();
        run_parser();
    });

    $('input[name=spreadsheet]').on('input', function() {
        if($('input[name=spreadsheet]').val() != '' && is_run) {
            show_start_bt('Update Parser');
        }
    })

    $('#spreadsheet-clear-bt').on('click', function() {
        event.preventDefault();
        if($('input[name=spreadsheet').val() != '' && is_run) {
            show_start_bt('Update Parser');
        }
        $('input[name=spreadsheet').val('');
    })

    $('#parser-form-stop').on('click', function() {
        event.preventDefault();
        $('.load_screen').css("display", "block");
        $.ajax({
            url: 'stop-parser/',
            type: 'get',
            success: function (data) {
                console.log('response data: ', data)
                if (data['success'] == true) {
                    is_run = false
                    $('#parser-form-stop').css("display", "none");
                    $('#parser-status').css("display", "none");
                    $('.load_screen').css("display", "none");
                    show_start_bt('Start Parser');
                }
            }
        });
    })

    function run_parser() {
        $('.load_screen').css("display", "block");
        var name = $('input[name=name]').val();
        var spreadsheet = $('input[name=spreadsheet]').val();
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        url = 'run-parser/';
        data = {
            'parser_name': name,
            'spreadsheet': spreadsheet,
        }
        $.ajax({
            url: url,
            type: 'post',
            headers: { 'X-CSRFToken': csrftoken },
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (data) {
                console.log('response data: ', data)
                if (data['success'] == false) {
                    var html = '<p>' + data['message'] + '</p>' + data['link']
                    $('#modal-dialog-parser .modal-body').html(html);
                    $('#modal-dialog-parser').modal('show');
                } else {
                    is_run = true
                    $('#parser-form-submit').css("display", "none");
                    $('#parser-form-stop').css("display", "inline-block");
                    $('#parser-status').css("display", "block");
                    $('#spreadsheet-link').attr("href", spreadsheet);
                    $('.load_screen').css("display", "none");
                }
            }
        });
    }

    function show_start_bt(text) {
        $('#parser-form-submit').html(text);
        $('#parser-form-submit').css("display", "inline-block");
    }
});

//function copyToClipboard() {
//  var copyText = document.getElementById("id_app_link");
//
//  /* Select the text field */
//  copyText.select();
//  copyText.setSelectionRange(0, 99999); /* For mobile devices */
//
//  navigator.clipboard.writeText(copyText.value);
//}
//
//function copySpreadsheetLink(id) {
//  var copyText = document.getElementById(id).href;
//  console.log(copyText)
//  navigator.clipboard.writeText(copyText);
//}
