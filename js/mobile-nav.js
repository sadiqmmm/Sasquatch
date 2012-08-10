$(document).ready(function() {
    $('#drop_menu').change(function() {
        if ($(this).val() != 'navigation')
        {
            window.location = $(this).val();
        }
    })
})