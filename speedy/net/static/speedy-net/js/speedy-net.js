var datepickerOptions = {
    dateFormat: 'MM d, yy',
    changeMonth: true,
    changeYear: true,
    minDate: '-180y',
    maxDate: '+0d',
    yearRange: '-180:+0'
};


evil.block('@@RegistrationForm', {

    _generateSlug: function () {
        var components = [this.firstNameField.val(), this.lastNameField.val()];
        components = components.filter(function (i) {
            return i
        });
        var slug = components.join('_');
        slug = slug.toLowerCase();
        slug = slug.replace(' ', '_');
        slug = slug.replace(/[^\x00-\x7F]/g, '');
        return slug;
    },

    init: function () {
        this.slugField = this.$('#id_slug');
        this.firstNameField = this.$('#id_first_name');
        this.lastNameField = this.$('#id_last_name');
        this.slugChanged = (this.slugField.val() != this._generateSlug());
        this.$("#id_date_of_birth").datepicker(datepickerOptions);
    },

    'change on #id_slug': function () {
        this.slugChanged = true;
    },

    'keyup on #id_first_name, #id_last_name': function () {
        if (!this.slugChanged) {
            this.slugField.val(
                this._generateSlug()
            );
        }
    }

});


evil.block('@@AccountForm', {

    init: function () {
        this.$("#id_date_of_birth").datepicker(datepickerOptions);
    }

});


evil.block('@@RemoveFromFriendsForm', {

    switchState: function (flag) {
        this.button.toggleClass('disabled', !flag);
        this.button.toggleClass('btn-danger', flag);
        this.button.text(this.button.data(flag ? 'hover-text' : 'default-text'));
    },

    init: function () {
        this.switchState(false);
        this.button.width(this.button.width());
    },

    'mouseover on @button': function () {
        this.switchState(true);
    },

    'mouseout on @button': function () {
        this.switchState(false);
    }

});


evil.block('@@MessageList', {
    init: function () {
        var this_ = this;
        window.setInterval(function () {
            this_.poll();
        }, 5000);
    },

    poll: function () {
        var this_ = this;
        var url = this.block.data('poll-url');
        var since = this.$('@message').first().data('timestamp');
        url += '?since=' + since;
        $.get(url, function (data) {
            $(data).prependTo(this_.block);
        });
    }
});


evil.block('@@Uploader', {

    blankState: function () {
        this.progress.hide();
        this.filename.hide();
        this.browseButton.show();
    },

    boundState: function () {
        this.blankState();
        this.filename.show();
    },

    progressState: function () {
        this.progress.show();
        this.progressBar.width(0);
        this.filename.hide();
        this.browseButton.hide();
    },

    startUpload: function (file) {
        var this_ = this;
        this.progressState();
        var data = new FormData();
        data.append('file', file);
        $.ajax({
            url: this.block.data('action'),
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            xhr: function () {
                var xhr = $.ajaxSettings.xhr();
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function (evt) {
                        var percent = Math.round(evt.loaded / evt.total * 100);
                        this_.progressBar.css('width', percent + '%');
                        if (percent == 100) {
                            this_.progressBar.addClass('active');
                            this_.progress.addClass('progress-striped');
                        } else {
                            this_.progressBar.removeClass('active');
                            this_.progress.removeClass('progress-striped');
                        }
                    }, false);
                }
                return xhr;
            }
        }).done(function(data, textStatus, jqXHR) {
            this_.boundState();
            this_.filename.text(data.files[0].name);
            this_.realInput.val(data.files[0].uuid);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            var data = jqXHR.responseJSON;
            for (var errorField in data) {
                if (!data.hasOwnProperty(errorField)) {
                    continue;
                }
                alert(data[errorField]);
                this_.blankState();
                break;
            }
        });
    },

    init: function () {
        if (this.realInput.val()) {
            this.boundState();
        } else {
            this.blankState();
        }
    },

    'click on @browseButton': function (event) {
        event.preventDefault();
        this.fileInput.trigger('click');
    },

    'change on @fileInput': function (event) {
        event.preventDefault();
        files = this.fileInput[0].files;
        if (!files.length) {
            return;
        }
        this.startUpload(files[0]);
    }

});
