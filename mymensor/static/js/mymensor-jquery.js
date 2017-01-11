$(document).ready(function() {
// JQuery code to be added in here.
    var url = window.location;
    // Will only work if string in href matches with location
        $('ul.item').parent().addClass('active');

    // Will also work for relative and absolute hrefs
        $('ul.nav a').filter(function () {
            return this.href == url;
        }).parent().addClass('active').parent().parent().addClass('active');
});