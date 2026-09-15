from urllib.parse import urlparse

def get_favicon(url):
    try:
        domain = urlparse(url).hostname
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    except:
        return None