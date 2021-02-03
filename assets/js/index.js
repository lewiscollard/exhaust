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
});
