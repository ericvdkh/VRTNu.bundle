import requests
import json
import cookielib
import urlparse
import os
import helperobjects


class UrlToStreamService:

    API_KEY ="3_qhEcPa5JGFROVwu5SWKqJ4mVOIkwlFNMSKwzPDAh8QZOtHqu6L4nD5Q7lk0eXOOG"
    BASE_GET_STREAM_URL_PATH = "https://mediazone.vrt.be/api/v1/vrtvideo/assets/"

    def __init__(self, vrt_base, vrtnu_base_url):
        self.vrt_base = vrt_base
        self.vrtnu_base_url = vrtnu_base_url
        self.session = requests.session()

    def get_stream_from_url(self, url):
        cred = helperobjects.Credentials()
        if not cred.are_filled_in():
            #TODO self._kodi_wrapper.open_settings()
            cred.reload()
        url = urlparse.urljoin(self.vrt_base, url)
        r = self.session.post("https://accounts.eu1.gigya.com/accounts.login",
                               {'loginID': cred.username, 'password': cred.password, 'APIKey': self.API_KEY,
                                'targetEnv': 'jssdk',
                                'includeSSOToken': 'true',
                                'authMode': 'cookie'})

        logon_json = r.json()
        if logon_json['errorCode'] == 0:
            uid = logon_json['UID']
            sig = logon_json['UIDSignature']
            ts = logon_json['signatureTimestamp']

            headers = {'Content-Type': 'application/json', 'Referer': self.vrtnu_base_url}
            data = '{"uid": "%s", ' \
                   '"uidsig": "%s", ' \
                   '"ts": "%s", ' \
                   '"email": "%s"}' % (uid, sig, ts, cred.username)

            response = self.session.post("https://token.vrt.be", data=data, headers=headers)
            securevideo_url = "{0}.mssecurevideo.json".format(self.cut_slash_if_present(url))
            securevideo_response = self.session.get(securevideo_url, cookies=response.cookies)
            json_obj = securevideo_response.json()

            for key in json_obj:
                value = json_obj[key]
                Log("securevideo_response ({}) = ({})".format(key, value))
                #securevideo_response (/content/dam/vrt/2018/01/10/american-epic-sessions-depot_WP00120786) = ({u'videoid': u'pbs-pub-88acf470-f49f-4771-85cc-2ff2413bbda6$vid-942a5061-cde0-41a8-ab1e-49b8a6254bae', u'clientid': u'vrtvideo'})


            video_id = list(json_obj.values())[0]['videoid']
            final_url = urlparse.urljoin(self.BASE_GET_STREAM_URL_PATH, video_id)

            stream_response = self.session.get(final_url)
            stream_json = stream_response.json()
            for key in stream_json:
                value = stream_json[key]
                Log("stream_response: ({}) = ({})".format(key, value))
                #stream_response: (playlist) = ({u'content': []})
                #stream_response: (targetUrls) = ([{u'url': u'https://ondemand-w.lwc.vrtcdn.be/content/vod/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3_nodrm_0760c8fd-ba81-42b1-8699-03b11fedef60.ism/.m3u8', u'type': u'HLS'}, {u'url': u'https://ondemand-w.lwc.vrtcdn.be/content/vod/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3_nodrm_0760c8fd-ba81-42b1-8699-03b11fedef60.ism/.mpd', u'type': u'MPEG_DASH'}, {u'url': u'https://ondemand-w.lwc.vrtcdn.be/content/vod/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3_nodrm_0760c8fd-ba81-42b1-8699-03b11fedef60.ism/Manifest', u'type': u'HSS'}, {u'url': u'https://ondemand-w.lwc.vrtcdn.be/content/vod/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3/vid-942a5061-cde0-41a8-ab1e-49b8a6254bae-CDN_3_nodrm_0760c8fd-ba81-42b1-8699-03b11fedef60.ism/.f4m', u'type': u'HDS'}])
                #stream_response: (description) = (Hedendaagse supersterren, waaronder Elton John, Willie Nelson, Merle Haggard, Alabama Shakes, Jack White, Nas, Ana Gabriel, Beck, Los Lobos en Steve Martin, brengen een eerbetoon aan de allereerste opnamestudio's die ooit gebruikt werden. Ze nemen muziek op met een opnametoestel uit 1920, het toestel waaruit Amerikaanse muziek geboren werd.)
                #stream_response: (title) = (American epic sessions)
                #stream_response: (tags) = ([])
                #stream_response: (metaInfo) = ({u'whatsonId': u'467432878527', u'allowedRegion': u'WORLD', u'ageCategory': u'AL'})
                #stream_response: (subtitleUrls) = ([])
                #stream_response: (posterImageUrl) = (https://images.vrt.be/orig/2018/01/10/fe46b7dc-f60b-11e7-8ba7-02b7b76bf47f.jpg)
                #stream_response: (duration) = (6806160)
                #stream_response: (aspectRatio) = (16:9)

            hls = self.get_hls(stream_json['targetUrls']).replace("https", "http")
            subtitle = None
            streamMetadata = helperobjects.StreamMetadata(hls, subtitle)

            try:
                streamMetadata.description = stream_json['description']
            except:
                pass

            try:
                streamMetadata.duration = stream_json['duration']
            except:
                pass

            return streamMetadata

    @staticmethod
    def get_hls(dictionary):
        for item in dictionary:
            if item['type'] == 'HLS':
                return item['url']

    @staticmethod
    def get_subtitle(dictionary):
        for item in dictionary:
            if item['type'] == 'CLOSED':
                return item['url']

    @staticmethod
    def cut_slash_if_present(url):
        if url.endswith('/'):
            return url[:-1]
        else:
            return url
