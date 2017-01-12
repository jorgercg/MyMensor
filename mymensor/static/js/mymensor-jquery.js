// Activate menu item on click
$(".nav a").on("click", function(){
   $(".nav").find(".active").removeClass("active");
   $(this).addClass("active");
});