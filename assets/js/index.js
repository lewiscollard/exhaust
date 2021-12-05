window.addEventListener('DOMContentLoaded', async () => {
  if (document.querySelector('.vue-youtube-mount')) {
    const vueModule = await import('vue');
    const youtubeModule = await import('./components/youtube-video.vue');
    for (const mountpoint of document.querySelectorAll('.vue-youtube-mount')) {
      new vueModule.default({
        el: mountpoint,
        components: {
          'youtube-video': youtubeModule.default,
        }
      })
    }
  }

  // Bind left/right arrows in exogram detail mode.
  const bindArrows = [
    {selector: '.js-bind-right', keyCode: 39},
    {selector: '.js-bind-left', keyCode: 37}
  ]
  for (const binding of bindArrows) {
    const element = document.querySelector(binding.selector)
    if (element) {
      window.addEventListener('keydown', (ev) => {
        if (ev.keyCode === binding.keyCode) {
          ev.stopPropagation()
          element.click()
        }
      })
    }
  }
});
