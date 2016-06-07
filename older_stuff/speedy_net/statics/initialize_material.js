'use strict';

/**
 * initialize all materialize components
 */
$(document).ready(function() {
    $('.datepicker').pickadate({
        selectMonths: true,
        selectYears: 100,
        format: 'yyyy-mm-dd'
    });
    $('select').material_select();
});
