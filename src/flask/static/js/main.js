//Initialise tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip({html:true,
      delay: {"show": 500, "hide": 1000 }})
});

//TODO: Make the navbar highlight properly

$('.navbar-nav .nav-link').click(function(){
    $('.navbar-nav .nav-link').removeClass('active');
    $(this).addClass('active');
});
