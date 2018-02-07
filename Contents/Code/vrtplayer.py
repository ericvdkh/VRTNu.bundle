# import os
# import requests
import config
# from bs4 import BeautifulSoup
# from bs4 import SoupStrainer
# from resources.lib.helperobjects import helperobjects
# from resources.lib.vrtplayer import metadatacollector
import statichelper
# from resources.lib.vrtplayer import actions
# from resources.lib.vrtplayer import metadatacreator
# from resources.lib.kodiwrappers import sortmethod


class VRTPlayer:

    def __init__(self, url_to_stream_service):
        self.url_toStream_service = url_to_stream_service

    def get_vrtnu_stream(self, url):
        stream = self.url_toStream_service.get_stream_from_url(url)
        return stream
        
    @staticmethod
    def format_image_url(element):
        raw_thumbnail = element.xpath(".//img/@srcset")[0].split('1x,')[0]
        return statichelper.replace_double_slashes_with_https(raw_thumbnail.strip())

    @staticmethod
    def get_thumbnail_and_title(element):
        thumbnail = VRTPlayer.format_image_url(element)
        found_element = element.xpath(".//*[@class='tile__title']")
        title = ""
        if found_element is not None:
            title = statichelper.replace_newlines_and_strip(found_element[0].text)
        return thumbnail, title

    @staticmethod
    def get_subtitle(element):
        found_element = element.xpath(".//*[@class='tile__subtitle']")
        subtitle = ""
        if len(found_element) > 0:
            p_item = found_element[0].xpath("./p")
            if len(p_item) > 0:
                subtitle = p_item[0].text.strip()
            else:
                subtitle = found_element[0].text.strip()
        return subtitle

    @staticmethod
    def get_description(element):
        found_element = element.xpath(".//*[@class='tile__description']")
        description = ""
        if len(found_element) > 0:
            p_item = found_element[0].xpath("./p")
            if len(p_item) > 0:
                description = p_item[0].text.strip()
            else:
                description = found_element[0].text.strip()
        return description
