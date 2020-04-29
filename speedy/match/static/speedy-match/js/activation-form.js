$(document).ready(function() {
    $('.widget-json').each(function (index, element) {
        var widget_value = JSON.parse($(element).find('.widget-input').val());
        for (var key in widget_value) {
            $(element).find('.widget-group[data-value="' + key + '"]').find('.widget-choice').slice(0, widget_value[key]).addClass('active')
        }
    });

    $('.widget-json').click(function(e) {
        e.stopPropagation();
    });

    $('.widget-choice').click(function () {
        $(this).closest('.widget-group').find('.widget-checkbox').prop('checked', true);
        if ($(this).closest('.widget-group').find('.widget-checkbox').is(":checked")) {
            var json_widget = $(this).closest('.widget-json');
            var json_widget_value = JSON.parse(json_widget.find('.widget-input').val());
            var json_widget_group = $(this).closest('.widget-group');
            json_widget_value[json_widget_group.data('value')] = $(this).data('value');
            json_widget_group.find('.widget-choice').removeClass('active').slice(0, $(this).data('value')).addClass('active');
            json_widget.find('.widget-input').val(JSON.stringify(json_widget_value));
        }
    });

    $('.widget-checkbox').click(function () {
        var json_widget = $(this).closest('.widget-json');
        var json_widget_value = JSON.parse(json_widget.find('.widget-input').val());
        var json_widget_group = $(this).closest('.widget-group');
        if ($(this).is(":checked")) {
            json_widget_value[json_widget_group.data('value')] = 5;
            json_widget_group.find('.widget-choice').addClass('active');
        } else {
            json_widget_value[json_widget_group.data('value')] = 0;
            json_widget_group.find('.widget-choice').removeClass('active');
        }
        json_widget.find('.widget-input').val(JSON.stringify(json_widget_value));
    });
});

