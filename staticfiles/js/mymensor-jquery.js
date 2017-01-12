$(document).ready(function() {

    $('ul li').click(function () {
        $('ul li').find('.active').removeClass('active');
        $(this).addClass('active');
    });

});