$(document).ready(function() {
    $(".nav").on("click", "li", function(){
       $(".nav li a").find(".active").removeClass("active");
       $(this).addClass("active");
    });
});