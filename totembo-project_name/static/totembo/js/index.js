var owl = $('.owl-carousel');
owl.owlCarousel({
    items:3,

    margin:80,
    autoplay:true,
    autoplayTimeout:1000,
    autoplayHoverPause:true
});
$('.play').on('click',function(){
    owl.trigger('play.owl.autoplay',[1000])
})
$('.stop').on('click',function(){
    owl.trigger('stop.owl.autoplay')
})


var owl = $('.product_detail-slider');
owl.owlCarousel({
    items:1,
    loop:true,
    margin:15,
    autoplay:true,
    autoplayTimeout:1000,
    autoplayHoverPause:true
});
$('.play').on('click',function(){
    owl.trigger('play.owl.autoplay',[1000])
})
$('.stop').on('click',function(){
    owl.trigger('stop.owl.autoplay')
})

var owl = $('.customer_reviews-slider');
owl.owlCarousel({
    items:4,
    margin:0,
    autoplay:true,
    autoplayTimeout:1000,
    autoplayHoverPause:true
});
$('.play').on('click',function(){
    owl.trigger('play.owl.autoplay',[1000])
})
$('.stop').on('click',function(){
    owl.trigger('stop.owl.autoplay')
})

document.addEventListener('DOMContentLoaded', () => {
  const stars = document.querySelectorAll('.star-rating span');
  let currentRating = 0;

  stars.forEach(star => {
    star.addEventListener('mouseover', () => {
      resetStars();
      highlightStars(star);
    });

    star.addEventListener('click', () => {
    currentRating = star.getAttribute('data-value');
  updateStars();
  console.log(`Selected rating: ${currentRating}`);
    });

    star.addEventListener('mouseout', () => {
    updateStars();
    });
  });

  function resetStars() {
    stars.forEach(star => star.classList.remove('selected'));
  }

  function highlightStars(star) {
    star.classList.add('selected');
  let previousSibling = star.previousElementSibling;

  while (previousSibling) {
    previousSibling.classList.add('selected');
  previousSibling = previousSibling.previousElementSibling;
    }
  }

  function updateStars() {
    resetStars();
    if (currentRating > 0) {
      for (let i = 0; i < currentRating; i++) {
    stars[i].classList.add('selected');
      }
    }
  }
});


