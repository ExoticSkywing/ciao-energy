(function () {
  function recover() {
    if (window.carousel) return;
    document.documentElement.classList.add('loader-watchdog-ready');
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    if (window.lenis && window.lenis.start) window.lenis.start();
    window.dispatchEvent(new Event('resize'));
  }

  function begin() {
    var checks = 0;
    var timer = setInterval(function () {
      checks += 1;
      var video = document.querySelector('.loader_video');
      if (window.carousel) {
        clearInterval(timer);
        return;
      }
      if ((video && video.ended) || checks >= 15) {
        recover();
        clearInterval(timer);
      }
    }, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', begin, { once: true });
  } else {
    begin();
  }
})();
