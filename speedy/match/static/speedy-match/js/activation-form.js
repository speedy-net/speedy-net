$(document).ready(function(){
    $('.activation-form #id_photo').change(function () {
        var file = this.files[0];
        var reader = new FileReader();
        reader.onloadend = function () {
           $('.image-click-zone').css('background-image', 'url("' + reader.result + '")').addClass('uploaded');
        };
        if (file) {
            reader.readAsDataURL(file);
        } else {
        }
    });
    $('.image-click-zone').click(function(){
        $(this).closest('.activation-form-field').find('#id_photo').click()
    });
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
        if($(this).closest('.widget-group').find('.widget-checkbox').prop('checked')) {
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
        if($(this).prop('checked')) {
            json_widget_value[json_widget_group.data('value')] = 5;
            json_widget_group.find('.widget-choice').addClass('active');
        } else {
            json_widget_value[json_widget_group.data('value')] = 0;
            json_widget_group.find('.widget-choice').removeClass('active');
        }
        json_widget.find('.widget-input').val(JSON.stringify(json_widget_value));
    });

});
