class TitleItem:

    def __init__(self, title, url_dictionary, is_playable, thumbnail = None, video_dictionary=None):
        self.title = title
        self.url_dictionary = url_dictionary
        self.is_playable = is_playable
        self.thumbnail = thumbnail
        self.video_dictionary = video_dictionary

class StreamMetadata:

    def __init__(self, stream_url, subtitle_url):
        self.stream_url = stream_url
        self.subtitle_url = subtitle_url
        self.genres = None
        self.tags = None
        self.duration = None
        self.seasonTitle = None
        self.episodeNumber = None
        self.description = None

class Credentials:

    def __init__(self):
        self.reload()

    def are_filled_in(self):
        return not (self.username is None or self.password is None or self.username == "" or self.password == "")

    def reload(self):
        self.username = Prefs["username"]
        self.password = Prefs["password"]

