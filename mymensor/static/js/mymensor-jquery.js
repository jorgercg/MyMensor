$(document).ready(function() {

    $('#mediaModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var recipient = button.data('whatever') // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var modal = $(this)
        modal.find('#mediaContent').attr('src',recipient)
    })


});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

window.chartColors = {
	color01: 'rgb(51,102,204)',
    color02: 'rgb(220,57,18)',
    color03: 'rgb(255,153,0)',
    color04: 'rgb(16,150,24)',
    color05: 'rgb(153,0,153)',
    color06: 'rgb(59,62,172)',
    color07: 'rgb(0,153,198)',
    color08: 'rgb(221,68,119)',
    color09: 'rgb(102,170,0)',
    color10: 'rgb(184,46,46)',
    color11: 'rgb(49,99,149)',
    color12: 'rgb(153,68,153)',
    color13: 'rgb(34,170,153)',
    color14: 'rgb(170,170,17)',
    color15: 'rgb(102,51,204)',
    color16: 'rgb(230,115,0)',
    color17: 'rgb(139,7,7)',
    color18: 'rgb(50,146,98)',
    color19: 'rgb(85,116,166)',
    color20: 'rgb(59,62,172)'
};


