$(document).ready(function () {
    $('.user-photo-input-wrapper #id_profile_picture').change(function () {
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

    $('.image-click-zone').click(function () {
        $('.user-photo-input-wrapper #id_profile_picture').click()
    });
});

