$(document).ready(function() {
// JQuery code to be added in here.
    $('select[name=assetOwner]').change(function(){
        id_assetOwner = $(this).val();
        request_url = '/get_assets/' + id_assetOwner + '/';
        $.ajax({
            url: request_url,
            success: function(data){
                $.each(data[0], function(key, value){
                    $('select[name=asset]').append('<option value="' + this.key + '">' + this.value +'</option>');
                });
            }
            
        })
    })
});