from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_username, user_email, user_field
from django.db.models.fields.files import ImageFieldFile

# Ensure ImageFieldFile.url dynamically returns external URLs directly without modifying models.py
if not hasattr(ImageFieldFile, "_original_url"):
    ImageFieldFile._original_url = ImageFieldFile.url

    @property
    def _custom_url(self):
        if self.name and (self.name.startswith("http://") or self.name.startswith("https://")):
            return self.name
        return ImageFieldFile._original_url.fget(self)

    ImageFieldFile.url = _custom_url


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter that automatically pulls and populates user details
    (email, username, name, avatar) from social providers (Google, GitHub) and enables
    seamless auto-signup without redirecting to the manual signup form.
    """

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.
        Pulls user first_name and last_name, combines them into `name`,
        and directly attaches the avatar URL from the provider.
        """
        user = super().populate_user(request, sociallogin, data)

        first_name = data.get("first_name") or getattr(user, "first_name", "") or ""
        last_name = data.get("last_name") or getattr(user, "last_name", "") or ""
        full_name = data.get("name") or ""

        # If full_name is provided but first/last are missing, split them
        if full_name and not (first_name or last_name):
            parts = full_name.partition(" ")
            first_name = parts[0]
            last_name = parts[2]
            user.first_name = first_name
            user.last_name = last_name

        # Combine first_name and last_name into name field
        combined_name = f"{first_name} {last_name}".strip() if (first_name or last_name) else full_name.strip()

        if hasattr(user, "name"):
            user.name = combined_name or None

        # Directly attach avatar URL from provider without uploading/downloading
        avatar_url = (
            getattr(sociallogin.account, "get_avatar_url", lambda: None)()
            or sociallogin.account.extra_data.get("picture")
            or sociallogin.account.extra_data.get("avatar_url")
        )
        if avatar_url:
            user.avatar = avatar_url

        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Always allow automatic signup for social logins without manual signup form redirect.
        """
        return True

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login user and directly attaches their avatar URL.
        """
        u = super().save_user(request, sociallogin, form=form)

        avatar_url = (
            getattr(sociallogin.account, "get_avatar_url", lambda: None)()
            or sociallogin.account.extra_data.get("picture")
            or sociallogin.account.extra_data.get("avatar_url")
        )
        if avatar_url and (not u.avatar or str(u.avatar) == "user.png"):
            u.avatar = avatar_url
            u.save(update_fields=["avatar"])

        return u

    def get_app(self, request, provider, client_id=None):
        """
        Safely retrieve the social app for the given provider without raising MultipleObjectsReturned.
        """
        from allauth.socialaccount.models import SocialApp

        apps = self.list_apps(request, provider=provider, client_id=client_id)
        if len(apps) > 1:
            visible_apps = [app for app in apps if not app.settings.get("hidden")]
            if visible_apps:
                apps = visible_apps
            configured_apps = [app for app in apps if app.client_id]
            if configured_apps:
                # Prefer database-backed app if present
                db_apps = [app for app in configured_apps if getattr(app, "pk", None)]
                if db_apps:
                    return db_apps[0]
                return configured_apps[0]
            return apps[0]
        elif len(apps) == 0:
            raise SocialApp.DoesNotExist()
        return apps[0]
