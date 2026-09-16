from cloudinary_storage.storage import MediaCloudinaryStorage


class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Media Cloudinary Storage backend that gracefully handles external avatar URLs
    (such as Google and GitHub OAuth avatar URLs) without prepending the Cloudinary prefix
    or generating broken Cloudinary URLs.
    """

    def _get_url(self, name):
        if not name:
            return ""
        if str(name).startswith(("http://", "https://")):
            return str(name)
        return super()._get_url(name)

    def url(self, name):
        if not name:
            return ""
        if str(name).startswith(("http://", "https://")):
            return str(name)
        return super().url(name)

    def exists(self, name):
        if str(name).startswith(("http://", "https://")):
            return True
        return super().exists(name)

    def delete(self, name):
        if str(name).startswith(("http://", "https://")):
            return True
        return super().delete(name)
