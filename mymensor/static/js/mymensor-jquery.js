var selector = '.li';

$(selector).on('click', function(){
    $(selector).removeClass('active');
    $(this).addClass('active');
});