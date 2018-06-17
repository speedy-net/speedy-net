function initDatepicker() {
    var dobDpElem = this.$("#id_date_of_birth").clone();
    dobDpElem.attr('id', 'id_date_of_birth_dp');
    dobDpElem.attr('name', 'date_of_birth_dp');
    this.$("#id_date_of_birth").after(dobDpElem);
    this.$("#id_date_of_birth").attr('type','hidden');
    this.$("#id_date_of_birth").removeAttr('class');
    this.$("#id_date_of_birth").removeAttr('required');
    this.$("#id_date_of_birth_dp").datepicker(datepickerOptions);
    var dob = $.datepicker.parseDate('yy-mm-dd', this.$("#id_date_of_birth").val());
    this.$("#id_date_of_birth_dp").datepicker('setDate', dob);
}

var datepickerOptions = {
    altField: "#id_date_of_birth",
    altFormat: 'yy-mm-dd',
    changeMonth: true,
    changeYear: true,
	  dateFormat: "d MM yy", //"dd/mm/yy",
    minDate: '-180y',
    maxDate: '+0d',
    yearRange: '-180:+0'
};
//$.datepicker.regional.en = {
//	dateFormat: 'MM d yy' };

$.datepicker.regional.he = {
	closeText: "סגור",
	prevText: "&#x3C;הקודם",
	nextText: "הבא&#x3E;",
	currentText: "היום",
	monthNames: [ "ינואר","פברואר","מרץ","אפריל","מאי","יוני",
	"יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר" ],
	monthNamesShort: [ "ינו","פבר","מרץ","אפר","מאי","יוני",
	"יולי","אוג","ספט","אוק","נוב","דצמ" ],
	dayNames: [ "ראשון","שני","שלישי","רביעי","חמישי","שישי","שבת" ],
	dayNamesShort: [ "א'","ב'","ג'","ד'","ה'","ו'","שבת" ],
	dayNamesMin: [ "א'","ב'","ג'","ד'","ה'","ו'","שבת" ],
	weekHeader: "Wk",
//	dateFormat: "d MM yy", //"dd/mm/yy",
	firstDay: 0,
	isRTL: true,
	showMonthAfterYear: false,
	yearSuffix: "" };

$.datepicker.setDefaults($.datepicker.regional[$('html').attr('lang')]);

/*
evil.block('@@HamburgerMenu', {
    init: function () {
        this.sideMenuPlaceholder.html($('@@SideMenu').html());
        this.sideMenuPlaceholder.find('li:last-child').remove();  // Remove redundant "Edit profile"
    }
});
*/

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
        initDatepicker();
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

    init: initDatepicker

});


evil.block('@@AutoForm', {
    'change on select': function () {
        this.$('form').submit();
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
        }).done(function (data, textStatus, jqXHR) {
            this_.boundState();
            this_.filename.text(data.files[0].name);
            this_.realInput.val(data.files[0].uuid);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            var data = jqXHR.responseJSON;
            for (var errorField in data) {
                if (data.hasOwnProperty(errorField)) {
                    alert(data[errorField]);
                    this_.blankState();
                    break;
                }
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

window.speedy = {};

window.speedy.setSession = function (domain, key) {
    $.ajax({
        url: '//' + domain + '/set-session/',
        method: 'post',
        data: {
            key: key
        },
        xhrFields: {
            withCredentials: true
        }
    });
};
