This is the source code for [Exhaust](https://exhaust.lewiscollard.com/), one of my websites.

It is a trivial Django project for something that looks like a blog, with all of the features I want from one, and with none of the features that I do not need.

It's intended to be my anti-social replacement for [information silos](https://indieweb.org/silo).

For a couple of months I occasionally sketched notes and photos of interesting things I did on a day in Markdown files,
in the hope I would find a static site generator I liked and maybe have a real blog some day.
I did not find one, mostly because all of the ones I found had awful templating engines.

I also knew that if I spent some non-trivial amount of time setting up a site with a static site generator, I would spend more time fiddling with themes than actually writing anything.

I almost wanted to write a static site generator myself,
but that too would have time from anything getting anything done,
and less on having something approaching a blog.
I know Django (it is my day job), so I thought it would be a good idea to write it in Django.

That it is probably the ugliest blog in the world is intentional.
It saves me getting bogged down in making it look nice, which hopefully gives me more time to write things.
It does have a Webpack build system, should I want to make it more frontend-heavy in future.

There's not much here that is more-than-trivial to implement, but please feel free to steal anything and everything from here.

## Things that are pretty interesting

### The `deployment` app

This contains a few management commands for site maintenance.

* `backupdb`: makes a local backup of the site's database to a local `.sql` file.
* `pulldb`: does the above, then loads that file into your local database (this is destructive, obviously!).
* `pullmedia`: a very thin wrapper around `rsync` that pulls a copy of the site's media files.
* `pull`: shortcut that calls both `pulldb` and `pullmedia`.
* `remote_manage`: runs manage.py on the server with the given arguments, e.g. `./manage.py remote_manage migrate`.
* `update`: pushes code changes to the live site. It does a `git pull` on the server, builds the frontend CSS and JS, does a `collectstatic`, migrates the database, and
restarts things that need restarting.

This is heavily inspired by
[onespacemedia-server-management](https://github.com/onespacemedia/server-management/);
it even keeps the same command names.
It was rewritten from scratch to make it use a modern version of [Fabric](https://www.fabfile.org/),
to be less weird in places,
and to take its settings from `django.conf.settings` instead of a JSON file.
It also does not have `pushdb` and `pushmedia`;
these are dangerous,
and permits the data on my local machine being, however briefly, the site's canonical state, which should never be the case.

### Markdown

This uses [Django MarkdownX](https://github.com/neutronX/django-markdownx) (my own fork of it to fix what I consider to be a [design flaw](https://github.com/neutronX/django-markdownx/pull/182), to give me a nice Markdown editor in my admin, with drag and drop image uploads.

This has a custom Markdown renderer to render images in multiple sizes (if they are uploaded via drag-and-drop).
It uses the `<picture>` and `<source>` to allow the browser to pick the most appropriate one.
There are WebP versions for those browsers that support it, too.
That's currently a majority of browsers as of September 2020, and soon to be the _overwhelming_ majority once iOS 14 gets widely deployed).

### Privacy-respecting and noscript-friendly YouTube embeds

In the Markdown editor in the admin, I can enter a tag like this:

```
<youtube id="4bQ6h0DPuHQ" />
```

This gets swapped out on the server side by a link to the video in question, which CSS styles as a link in a fixed 16:9 aspect area. People with Javascript disabled will know there is something missing, and the 16:9 aspect ratio prevents a document reflow if the video is loaded. In the RSS feed, this appears as a paragraph with a link to the video, because it is.

If the user has Javascript enabled, the video is swapped out _again_ with a Vue component. This will ask the user to choose to load just that embedded video, or to always load off-site embeds. If the former, it is switched out with a privacy-enhanced IFrame (using the [special domain youtube-nocookie.com](https://www.ghacks.net/2018/05/23/why-you-should-always-use-youtubes-privacy-enhanced-mode/)). If the latter, all videos on the page are switched out with it, and a local storage item remembers that they'll want to do this in the future. (I may change this to session storage in future.)

I think this is a reasonable compromise between protecting users' privacy and not being too annoying to people that don't care; Google won't be tracking you unless you opt in to it, and if you opt in it'll load the video in a way that Google [almost promises won't track you](https://support.google.com/youtube/answer/171780?hl=en-GB). Anyone that doesn't care is just one extra click away from showing all videos forever.

## License

[WTFPL](http://www.wtfpl.net/)

## TODO

* OpenGraph stuff?
