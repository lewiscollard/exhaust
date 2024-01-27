"""
The last thing written for the Django version of Exhaust: an exporter to a
Hugo markdown site.
"""
# ..thus, I don't care about making this tidy.
# pylint:disable=too-many-locals,too-many-statements
import re
import shutil
from pathlib import Path

import toml
from django.core.files.storage import default_storage
from django.core.management import BaseCommand
from django.urls import resolve

from exhaust.posts.models import Category, Post, PostImage

# https://stackoverflow.com/questions/44227270/regex-to-parse-image-link-in-markdown
# (there's a bug, it has a leading "[" on the alt text, and I can't be
# bothered to work out why)")
IMAGE_RE = re.compile(
    r"""\[?(!)(?P<alt>\[[^\]\[]*\[?[^\]\[]*\]?[^\]\[]*)\]\((?P<url>[^\s]+?)(?:\s+(["'])(?P<title>.*?)\4)?\)"""
)
# Regex for YouTube embeds.
YOUTUBE_RE = re.compile(r"""<youtube id=['"](?P<id>.*)["']></youtube>""")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('output', nargs=1, help='output dir')

    def handle(self, *args, **options):
        output_dir = Path(options['output'][0])
        # List of (old_path, new_path) tuples.
        redirects = [
            # New site lists posts on the homepage.
            ("/posts/", "/"),
        ]
        for post in Post.objects.all().prefetch_related('categories'):
            date = post.date.date().isoformat()
            new_slug = f'{date}-{post.slug}'
            new_post_base = Path("posts") / new_slug
            new_post_root = output_dir / "content" / new_post_base
            output_path = new_post_root / 'index.md'
            new_post_root.mkdir(exist_ok=True, parents=True)
            frontmatter = {
                'title': post.title,
                'date': post.date,
                'categories': [category.slug for category in post.categories.all()],
                'seo_title': post.seo_title,
                'og_description': post.opengraph_description,
                'og_image': post.opengraph_image.file.name if post.opengraph_image else '',
                "meta_description": post.meta_description or ""
            }

            text = post.text
            while image_match := IMAGE_RE.search(text):
                image = image_match.groupdict()
                assert image['url'].startswith('/'), f'image found pointing to external host: {image}'

                # Image which was inserted by my version of the drag-and-drop
                # in MarkdownX.
                if image["url"].startswith("/image-redirect/"):
                    image_obj = PostImage.objects.get(pk=resolve(image["url"]).kwargs["pk"])
                    new_image_path = new_post_root / image_obj.image.name
                    # Have we already saved this? No point doing it again
                    # (until I find a bug which means I have to do it again).
                    if not new_image_path.exists():
                        shutil.copy(image_obj.image.path, new_image_path)
                    # Create redirects for the image.
                    redirects.append((image_obj.image.url, str(Path("/") / new_post_base / image_obj.image.name)))
                    new_name = Path(image_obj.image.name).name

                # Older image from a brief time window using the upstream
                # version of MarkdownX before I figured out its really bad
                # default behaviour.
                else:
                    assert image["url"].startswith("/media/markdownx")
                    image_path_obj = Path(image["url"])
                    new_image_path = new_post_root / image_path_obj.name
                    if not new_image_path.exists():
                        shutil.copy(
                            default_storage.path("/".join(image_path_obj.parts[2:])),
                            new_image_path,
                        )
                    redirects.append(
                        (image["url"], str(Path("/") / new_post_base / image_path_obj.name))
                    )
                    new_name = image_path_obj.name

                # Replace the image with the new shortcode.
                shortcode_parts = [
                    "{{< image",
                    f'src="{new_name}"',
                ]
                if image["alt"]:
                    # Escape quotes, and also remove the spurious leading "["
                    # which got in here somewhere and I don't feel like poking
                    # the copy-pasted regex.
                    alt = image["alt"].replace('"', r'\"').lstrip("[")
                    shortcode_parts.append(f'alt="{alt}"')
                if image["title"]:
                    title = image["title"].replace('"', r'\"')
                    shortcode_parts.append(f'caption="{title}"')
                shortcode_parts.append(">}}")
                replacement = " ".join(shortcode_parts)
                text = text[:image_match.start()] + replacement + text[image_match.end():]

            # Is this an image post? Insert it into the body at the start.
            if post.image:
                post_image_path_obj = Path(post.image.path)
                new_post_image_path = new_post_root / post_image_path_obj.name
                post_image_alt = (post.alt_text or "").replace('"', r'\"')
                if not new_post_image_path.exists():
                    shutil.copy(post_image_path_obj, new_post_image_path)
                text = " ".join([
                    "{{< image",
                    f'src="{post_image_path_obj.name}"',
                    f'alt="{post_image_alt}"'
                    ">}}"
                ]) + "\n\n" + text
                redirects.append(
                    (post.image.url, str(Path("/") / new_post_base / post_image_path_obj.name))
                )

            # Replace YouTube embeds with new shortcode.
            while youtube_match := YOUTUBE_RE.search(text):
                yt_shortcode = " ".join([
                    "{{< youtube",
                    f'"{youtube_match.groupdict()["id"]}"',
                    ">}}"
                ])
                text = text[:youtube_match.start()] + yt_shortcode + text[youtube_match.end():]
            with open(output_path, 'w') as fd:
                fd.write("+++\n")
                fd.write(toml.dumps(frontmatter))
                fd.write("+++\n")
                fd.write(text)

            # Add redirects for this post.
            redirects.append((post.get_absolute_url(), f"/posts/{new_slug}/"))

        for category in Category.objects.exclude(post=None).distinct():
            output_base = Path("categories") / category.slug
            output_path = output_dir / "content" / output_base / '_index.md'
            frontmatter = {
                'title': category.title,
                'meta_description': category.meta_description or '',
            }
            output_path.parent.mkdir(exist_ok=True, parents=True)
            output_path.write_text(f"+++\n{toml.dumps(frontmatter)}\n+++\n{category.description}")
            redirects.append((category.get_absolute_url(), f"/{output_base}/"))

        with (output_dir / "redirects.map").open("w") as fd:
            fd.write("# Generated redirects from migration to Hugo\n")
            fd.write(
                "\n".join([
                    f"{old_path} {new_path};"
                    for old_path, new_path in redirects
                ]),
            )
