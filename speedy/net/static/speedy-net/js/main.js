evil.block('@@RegistrationForm', {

    _generateSlug: function () {
        var slug = this.emailField.val().split('@')[0];
        slug = slug.replace('.', '_');
        return slug;
    },

    'init': function () {
        this.slugField = this.$('#id_slug');
        this.emailField = this.$('#id_email');
        this.slugChanged = (this.slugField.val() != this._generateSlug());
    },

    'change on #id_slug': function () {
        this.slugChanged = true;
    },

    'keyup on #id_email': function () {
        if (!this.slugChanged) {
            this.slugField.val(
                this._generateSlug()
            );
        }
    }

});
