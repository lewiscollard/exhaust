import Vue from 'vue';

window.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.vue-youtube-mount')) {
    import('vue').then(module => {
      import('./components/youtube-video.vue').then(ytmodule => {
        for (const mountpoint of document.querySelectorAll('.vue-youtube-mount')) {
          new Vue({
            el: mountpoint,
            components: {
              'youtube-video': ytmodule.default,
            }
          })
        }
      })
    })
  }
});
