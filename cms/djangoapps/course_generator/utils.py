"""
Course generator utilities
"""

import urllib
import mimetypes
from functools import partial

from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from cache_toolbox.core import del_cached_content


def store_jacket_image(course_key, img_url):
    # set initial values
    content_name = asset_url = None

    # if image url is available then proceed
    if img_url:
        filename = img_url.split('/')[-1]
        content_loc = StaticContent.compute_location(course_key, filename)
        mime_type = mimetypes.types_map['.'+filename.split('.')[-1]]
        sc_partial = partial(StaticContent, content_loc, filename, mime_type)

        content = sc_partial(urllib.urlopen(img_url).read())
        tempfile_path = None

        (thumbnail_content, thumbnail_location) = contentstore().generate_thumbnail(
                content,
                tempfile_path=tempfile_path,
            )

        # delete cached thumbnail even if one couldn't be created this time (else
        # the old thumbnail will continue to show)
        del_cached_content(thumbnail_location)
        # now store thumbnail location only if we could create it
        if thumbnail_content is not None:
            content.thumbnail_location = thumbnail_location

        # then commit the content
        contentstore().save(content)
        del_cached_content(content.location)

        content_name = content.name
        asset_url = StaticContent.serialize_asset_key_with_slash(content.location)

    # return  content name and asset URL
    return content_name, asset_url