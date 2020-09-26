window.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.vue-youtube-mount')) {
    import('vue').then(vueModule => {
      import('./components/youtube-video.vue').then(ytModule => {
        for (const mountpoint of document.querySelectorAll('.vue-youtube-mount')) {
          new vueModule.default({
            el: mountpoint,
            components: {
              'youtube-video': ytModule.default,
            }
          })
        }
      })
    })
  }
});
