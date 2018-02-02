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
                Log("The key and value are ({}) = ({})".format(key, value))

            video_id = list(json_obj.values())[0]['videoid'] #json_obj[u'videoId']
            final_url = urlparse.urljoin(self.BASE_GET_STREAM_URL_PATH, video_id)

            stream_response = self.session.get(final_url)
            hls = self.get_hls(stream_response.json()['targetUrls']).replace("https", "http")
            subtitle = None
            streamMetadata = helperobjects.StreamMetadata(hls, subtitle)

            try:
                streamMetadata.description = json_obj[u'description']
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
