This is the source code for my site [exhaust](https://exhaust.lewiscollard.com/).

It is a trivial Django project for something that looks like a blog, with all of the features I want from one, and none of them that I do not.

It's intended to be an anti-social replacement for [information silos](https://indieweb.org/silo).

For a couple of months I occasionally sketched notes and photos of interesting things I did on a day in Markdown files,
in the hope I would find a static site generator I liked and maybe have a real blog some day.
I did not find one, mostly because all of the ones I found had awful templating engines.

I also knew that if I spent some non-trivial amount of time setting up a site with a static site generator, I would spend more time fiddling with themes than actually writing anything.

I almost wanted to write a static site generator myself,
but that too would have time from anything getting anything done,
and less on having something approaching a blog.
Given that I know Django (it is my day job), I thought it would be a good idea to write it in Django.

That it is probably the ugliest blog in the world is intentional.
It saves me getting bogged down in making it look nice, and hopefully, gives me more time to write things.
It does have a trivial Webpack build set up in case I want to do something more with it in future.

There's nothing in here that is technically interesting or even more-than-trivial to implement, but please feel free to steal anything and everything from here.

== TODO

* meta descriptions
* OpenGraph stuff
* RSS feeds
