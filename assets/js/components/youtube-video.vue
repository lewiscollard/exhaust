<template>
  <div class="youtube-video">
    <template v-if="shouldShow">
      <iframe :src="iframeUrl" frameborder="0" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </template>
    <template v-else>
      <div class="youtube-video__inner">
        <div class="youtube-video__body">
          <p class="youtube-video__text">
            To protect your privacy, an embedded YouTube video was not loaded.
            Choose from the options below, or
            <a :href="videoUrl">view it on YouTube</a>.
          </p>

          <p class="youtube-video__button-wrap">
            <button class="youtube-video__button" @click="loadVideo">
              Load this video
            </button>

            <button class="youtube-video__button" @click="loadAllVideosForever">
              Always load YouTube videos
            </button>
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
  export default {
    props: {
      id: {
        type: String,
        required: true,
      }
    },

    data() {
      return {
        // The user has asked to show only this video.
        showThis: false,
        // The user has set all videos globally to be shown (pulled from local
        // storage).
        showGlobal: window.localStorage.getItem('autoload-videos') || false,
      }
    },

    mounted() {
      window.addEventListener('exhaustShowVideos', () => {
        this.showThis = true
      })
    },

    computed: {
      iframeUrl () {
        return `https://www.youtube-nocookie.com/embed/${this.id}`
      },
      videoUrl () {
        return `https://www.youtube.com/watch?v=${this.id}`
      },
      shouldShow () {
        return this.showGlobal || this.showThis
      }
    },

    methods: {
      loadVideo (event) {
        this.showThis = true
      },
      loadAllVideosForever () {
        window.localStorage.setItem('autoload-videos', true)
        window.dispatchEvent(new CustomEvent('exhaustShowVideos'))
        this.showThis = true
      }
    }
  }
</script>
