$(document).ready(function() {

    $('.nav a').click(function () {
        $('.nav').find('.active').removeClass('active');
        $(this).parent().addClass('active');
        alert('clicked');
    });

});