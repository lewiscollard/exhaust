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
It does have a trivial Webpack build set up in case I need to make it more frontend-heavy in future.

There's nothing in here that is technically interesting or even more-than-trivial to implement, but please feel free to steal anything and everything from here.

## The `deployment` app

This contains a few management commands for maintenance purposes.

* `backupdb`: makes a local backup of the site's database to a local `.sql` file.
* `pulldb`: does the above, then loads that file into your local database (this is destructive, obviously!).
* `pullmedia`: a very thin wrapper around `rsync` that pulls a copy of the site's media files.
* `update`: pushes code changes to the live site. It does a `git pull` on the server, runs a build of frontend files, does a `collectstatic`, migrates the database, and
restarts things that need restarting.

This is heavily inspired by
[onespacemedia-server-management](https://github.com/onespacemedia/server-management/), even keeping the same command names.
It was rewritten from scratch to make it use a modern version of Fabric,
to be less weird in places,
and to take its settings from `django.conf.settings` instead of a JSON file.
It also does not have `pushdb` and `pushmedia`;
these are dangerous,
and reflects a model in which the data on my local machine can, however briefly, be the site's canonical state, which I dislike.

## License

[WTFPL](http://www.wtfpl.net/)

## TODO

* OpenGraph stuff
* RSS feeds
