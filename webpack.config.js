const path = require('path');

const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

const webpack = require('webpack');

const DEV = process.env.NODE_ENV === 'development';
// Remove pointless noise ("caniuse-lite is outdated") that I do not care
// about.
process.env.BROWSERSLIST_IGNORE_OLD_DATA = true

const config = {
  stats: 'minimal',
  entry: {
    'main': './assets/js/index.js',
    'style': './assets/scss/styles.scss',
    // Separate stylesheet to avoid bloating out the primary one - by
    // definition we won't need these styles on our normal pages, so no reason
    // to load them.
    'error-styles': './assets/scss/error-styles.scss'
  },
  output: {
    filename: '[name].js'
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.scss$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          'css-loader', 'sass-loader'
        ]
      },
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          }
        }
      }
    ]
  },

  devServer: {
    // Compression is mildly pointless in local dev.
    compress: false,
    host: 'localhost',
    // I use 3000 out of an old habit.
    port: 3000,
    proxy: {
      '/': {
        target: 'http://localhost:8000/'
      }
    }
  },

  // https://stackoverflow.com/questions/47332728/you-are-using-the-runtime-only-build-of-vue-where-the-template-compiler-is-not-a
  resolve: {
      alias: {
          vue: 'vue/dist/vue.js'
      },
  },

  output: {
    path: path.resolve(__dirname, 'static/build/webpack/'),
    publicPath: '/static/build/webpack/'
  },

  plugins: [
    new CopyPlugin({
      patterns: [
        {from: 'assets/images', to: path.resolve(__dirname, './static/build/webpack/images')}
      ]
    }),
    new MiniCssExtractPlugin({
      filename: '[name].css'
    }),
    new webpack.HotModuleReplacementPlugin(),
    new VueLoaderPlugin(),
  ]
}

module.exports = (env, argv) => {
  if (argv.mode === 'production') {
    config.resolve.alias.vue = 'vue/dist/vue.min.js'
  }

  return config
}
