var datepickerOptions = {
    dateFormat: 'MM d, yy',
    changeMonth: true,
    changeYear: true,
};


evil.block('@@RegistrationForm', {

    _generateSlug: function () {
        var components = [this.firstNameField.val(), this.lastNameField.val()];
        components = components.filter(function(i) {return i});
        var slug = components.join('_');
        slug = slug.toLowerCase();
        slug = slug.replace(' ', '_');
        slug = slug.replace(/[^\x00-\x7F]/g, '');
        return slug;
    },

    'init': function () {
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

    'init': function () {
        this.$("#id_date_of_birth").datepicker(datepickerOptions);
    }

});
