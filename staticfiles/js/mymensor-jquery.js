$(document).ready(function() {

    $('ul li').click(function () {
        $('ul li').find('.nav-item.active').removeClass('active');
        $(this).addClass('active');
    });

});