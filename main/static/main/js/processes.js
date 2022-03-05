$(function() {
    var timer = setInterval(() => update(), 60000); // update every 1 minute

    $('div.process > div.process-actions > div.process-actions-bts > button.process-actions-btn:nth-child(1)').on('click', function() {
        if ($(this).hasClass('btn-outline-secondary')) return;
        console.log('start click')
        id = $(this).parent().parent().parent().attr('id');
        action(id, 'start')
    })

    $('div.process > div.process-actions > div.process-actions-bts > button.process-actions-btn:nth-child(2)').on('click', function() {
        if ($(this).hasClass('btn-outline-secondary')) return;
        console.log('stop click')
        id = $(this).parent().parent().parent().attr('id');
        action(id, 'stop')
    })

    $('div.process > div.process-actions > div.process-actions-bts > button.process-actions-btn:nth-child(3)').on('click', function() {
        console.log('remove click')
        id = $(this).parent().parent().parent().attr('id');
        action(id, 'remove')
    })

    $('div.process > div.process-actions > div.process-actions-bts > button.process-actions-btn:nth-child(4)').on('click', function() {
        console.log('update click')
        id = $(this).parent().parent().parent().attr('id');
        update(id);
    })
});

function update(p_id = '') {
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    url = 'process_info'
    data = { 'p_id': p_id }
    console.log(JSON.stringify(data))
    $.ajax({
        url: url,
        type: 'post',
        headers: { 'X-CSRFToken': csrftoken },
        data: JSON.stringify(data),
        dataType: 'json',
        success: function (data) {
            data = JSON.parse(data);
            console.log('response data: ', data);
            if (data['success'] == true) {
                if (data['processes']) {
                    data['processes'].forEach((element) => {
                        proc = $('#' + element['id']);
                        if (element['active']) {
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(1)').removeClass('btn-primary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(1)').addClass('btn-outline-secondary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(2)').addClass('btn-primary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(2)').removeClass('btn-outline-secondary');
                        } else {
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(1)').addClass('btn-primary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(1)').removeClass('btn-outline-secondary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(2)').removeClass('btn-primary');
                            proc.find('div.process-actions > div.process-actions-bts > button.btn:nth-child(2)').addClass('btn-outline-secondary');
                        }
                        active = element['active'] ? 'active' : 'stopped';
                        proc.find('div.process-content > div:nth-child(1) > span.process-info-value').text(element['name']);
                        proc.find('div.process-content > div:nth-child(2) > span.process-info-value').text(element['id']);
                        proc.find('div.process-content > div:nth-child(3) > span.process-info-value').text(active);
                        if (element['active']) {
                            proc.find('div.process-content > div:nth-child(3) > span.process-info-value').removeClass('text-color-red');
                            proc.find('div.process-content > div:nth-child(3) > span.process-info-value').addClass('text-color-green');
                        } else {
                            proc.find('div.process-content > div:nth-child(3) > span.process-info-value').addClass('text-color-red');
                            proc.find('div.process-content > div:nth-child(3) > span.process-info-value').removeClass('text-color-green');
                        }
                        proc.find('div.process-content > div:nth-child(4) > span.process-info-value').text(element['start_time']);
                        proc.find('div.process-content > div:nth-child(5) > span.process-info-value').text(element['total_time']);
                        proc.find('div.process-content > div:nth-child(6) > span.process-info-value').text(element['last_update']);
                    })
                }
            } else {
                console.log('not update')
            }
        }
    });
}

function action(p_id, url) {
    csrftoken = $('input[name=csrfmiddlewaretoken]').val();
    data = { 'p_id': p_id }
    $.ajax({
        url: url,
        type: 'post',
        headers: { 'X-CSRFToken': csrftoken },
        data: JSON.stringify(data),
        dataType: 'json',
        success: function (data) {
            data = JSON.parse(data);
            console.log('response data: ', data);
            if (data['success'] == true) {
                if (url == 'remove')
                    $('#' + p_id).remove();
                update(p_id);
            } else {
                console.log('not success')
            }
        }
    });
}

