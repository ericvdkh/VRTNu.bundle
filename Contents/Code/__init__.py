import requests
import config
import content
import re
import urltostreamservice
import statichelper
from vrtplayer import VRTPlayer

TITLE    = 'VRT Nu'
PREFIX   = '/video/vrtnu'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
U2S = urltostreamservice.UrlToStreamService(config.VRT_BASE_URL, config.VRTNU_BASE_URL)
vrt_player = VRTPlayer(U2S)

##########################################################################################
def Start():
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items', summary=1)
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'InfoList'
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  U2S.signon()
  #HTTP.CacheTime = CACHE_1HOUR
  #HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"


##########################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()

    title = "A-Z"
    oc.add(
        DirectoryObject(
            key = Callback(AToZ, title = title, url = config.VRTNU_BASE_URL + '/a-z'),
            title = title
        )
    )

    title = "Categorieën".decode("utf-8")
    oc.add(
        DirectoryObject(
            key = Callback(Categorieen, title = title, url = config.VRTNU_BASE_URL + '/categorieen'),
            title = title
        )
    )

    title = "Kanalen"
    oc.add(
        DirectoryObject(
            key = Callback(TVChannels, title = title),
            title = title
        )
    )

    pageElement = HTML.ElementFromURL(config.VRTNU_BASE_URL)
    for listelement in pageElement.xpath("//div[@class='list']"):
        header = listelement.xpath(".//h2//text()")[0]
        header = header.strip().decode("utf-8")
        found_element = listelement.xpath(".//a[@class='tile']//@href") #./div/div[2]/ul/li/div/a
        if len(found_element) > 0:
            oc.add(
                DirectoryObject(
                    key=Callback(EpisodesFromElement, title=header, element=HTML.StringFromElement(listelement)), 
                    title=header
                )
            )

    return oc

##########################################################################################
@route(PREFIX + "/atoz")
def AToZ(title, url):
  oc = ObjectContainer(title2 = title)
  pageElement = HTML.ElementFromURL(url)

  for gloschar in pageElement.xpath("//a[@class='vrtglossary__char']"):
    letter = gloschar.xpath("./text()")[0]
    ref = gloschar.xpath("./@href")[0]
    oc.add(
      DirectoryObject(
          key = Callback(ProgramsByLetter, url = url, letter = letter, ref = ref),
          title = letter.upper()
      )
    )

  return oc

@route(PREFIX + "/categorieen")
def Categorieen(title, url):
    oc = ObjectContainer(title2 = title.decode("utf-8"), view_group = "List")
    pageElement = HTML.ElementFromURL(url)

    for categorie in pageElement.xpath("//*[@class='tile tile--category']"):
        t_ref = categorie.xpath("./@href")[0]
        t_image, t_title = VRTPlayer.get_thumbnail_and_title(categorie)
        Log("Categorieen - {0} - {1}".format(t_title, t_ref))
        oc.add(
            DirectoryObject(
                key = Callback(ProgramsByCategory, title=t_title, url=t_ref),
                title = t_title,
                thumb = t_image
            )
        )

    return oc

##########################################################################################
@route(PREFIX + '/tvchannels')
def TVChannels(title):

    oc = ObjectContainer(title2 = title)

    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id]

        oc.add(
            DirectoryObject(
                key = Callback(Channel, channel_id = channel_id),
                title = channel.title,
                summary = channel.title,
                thumb = R("%s.png" % channel.thumb)
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/Channel")
def Channel(channel_id):

    channel = content.tv_channels[channel_id]

    oc = ObjectContainer(title1 = channel.title)
    pageElement = HTML.ElementFromURL(channel.channel_url)
    # Log(HTML.StringFromElement(pageElement))
    for listelement in pageElement.xpath("//div[@class='list']"):
        #<h2 class="vrtlist__title default__title" id="list_1823762810-title">Ontdek het beste van onze andere kanalen</h2>
        header = listelement.xpath(".//h2//text()")[0]
        #found_element = listelement.xpath(".//a[@class='tile']//@href") #<a href="/vrtnu/a-z/terzake-docu/2018/terzake-docu-s2018a7/" class="tile">
        #if len(found_element) > 0:
        oc.add(
            DirectoryObject(
                key=Callback(EpisodesForTitle, title=header, element=HTML.StringFromElement(listelement)), 
                title=header
            )
        )

    return oc

@route(PREFIX + "/episodesfortitle")
def EpisodesForTitle(title, element):
    oc = ObjectContainer(title2 = title.decode("utf-8"), view_group = "InfoList")
    #Log("EpisodesForTtile-"+element)
    htmlelement = HTML.ElementFromString(element)
    for tile in htmlelement.xpath("//li[@role='presentation']"):
        t_href = tile.xpath(".//a//@href")[0]
        Log("EpisodesForTtile url="+t_href)
        t_image, t_title = VRTPlayer.get_thumbnail_and_title(tile)
        Log("EpisodesFromElement t_title="+t_title)
        Log("EpisodesFromElement t_image="+t_image)

        oc.add(
            DirectoryObject(
                key = Callback(Programs, title = t_title, url = t_href, preselector="//*[@class='episodeslist']"),
                title = t_title,
                thumb = t_image
            )
        )
    return oc

@route(PREFIX + "/programsbycategory")
def ProgramsByCategory(url, title):
    oc = ObjectContainer(title2 = title.decode("utf-8"), view_group = "InfoList")
    response = requests.get(config.VRTNU_SEARCH_URL + title.lower())
    programs = response.json()
    for program in programs:
        # {u'description': u"<p>Een muzikale reis door de Amerikaanse 'Roaring Twenties'</p>\n", 
        #  u'title': u'American Epic', 
        #  u'episode_count': 4, 
        #  u'score': 6.8267446, 
        #  u'targetUrl': u'//www.vrt.be/vrtnu/a-z/american-epic.relevant/', 
        #  u'brands': [u'canvas'], 
        #  u'type': u'program', 
        #  u'thumbnail': u'//images.vrt.be/orig/2018/01/10/c9e8b896-f609-11e7-8ba7-02b7b76bf47f.jpg'}
        Log(program)
        oc.add(
            DirectoryObject(
                key=Callback(Programs, title=program["title"], url=statichelper.replace_double_slashes_with_https(program["targetUrl"])),
                title=program["title"],
                summary=program["description"].replace('<p>', '').replace('</p>', ''),
                thumb=statichelper.replace_double_slashes_with_https(program["thumbnail"])
            )
        )
    return oc

##########################################################################################
@route(PREFIX + "/episodesfromelement")
def EpisodesFromElement(title, element):
    #Log("EpisodesFromElement-"+element)
    oc = ObjectContainer(title2=title, view_group = 'InfoList')
    htmlelement = HTML.ElementFromString(element)
    for tile in htmlelement.xpath("//*[@class='tile']"):
        t_href = tile.xpath("./@href")[0]
        url = config.VRT_BASE_URL + t_href
        Log("EpisodesFromElement url="+url)
        t_image, t_title = VRTPlayer.get_thumbnail_and_title(tile)
        t_title = t_title
        Log("EpisodesFromElement t_title="+t_title)
        Log("EpisodesFromElement t_image="+t_image)
        t_descr = VRTPlayer.get_description(tile)
        Log("EpisodesFromElement t_descr="+t_descr)
        t_tagline = VRTPlayer.get_subtitle(tile)
        Log("EpisodesFromElement t_tagline="+t_tagline)

        oc.add(
            DirectoryObject(
                key = Callback(Programs, title = t_title, url = t_href, preselector="//*[@class='episodeslist']"),
                title = t_title,
                summary = t_descr,
                tagline = t_tagline,
                thumb = t_image
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/programsbyletter")
def ProgramsByLetter(url, letter, ref):
  Log("ProgramsByLetter - letter={}, ref={}".format(letter, ref))
  oc = ObjectContainer(title2 = letter.upper(), view_group = 'InfoList')
    # <div class="vrtlist vrtglossary__group">
    #         <h2 id="a" class="vrtglossary__group__title sticky"><div class="vrtglossary__group__title__letter">a</div></h2>
    #         <div class="vrtglossary__list">
    #           <ul class="vrtlist__list" aria-labelledby="a">
    #             <li class="vrtlist__item vrtglossary__item">
    #               <a href="/vrtnu/a-z/abba-in-concert.relevant/" class="tile">
    #                 <div class="tile__image-wrapper">
    #                  <div class="tile__image">
    #                    <picture class="">
    #                       <!--[if IE 9]><video style="display: none"><![endif]-->
    #                         <source srcset="//images.vrt.be/VV_4x3_400/2018/01/10/c9e8b896-f609-11e7-8ba7-02b7b76bf47f.jpg 1x, //images.vrt.be/VV_4x3_800/2018/01/10/c9e8b896-f609-11e7-8ba7-02b7b76bf47f.jpg 2x" media="(max-width: 1599px)">
    #                       <!--[if IE 9]></video><![endif]-->
    #                       <img srcset="//images.vrt.be/VV_4x3_400/2018/01/10/c9e8b896-f609-11e7-8ba7-02b7b76bf47f.jpg 1x, //images.vrt.be/VV_4x3_800/2018/01/10/c9e8b896-f609-11e7-8ba7-02b7b76bf47f.jpg 2x" alt="" class="image   " onerror="if(this.parentNode) { this.parentNode.classList.add('image--error');this.parentNode.classList.remove('image--loading'); }" onload="if(this.parentNode) { this.parentNode.classList.remove('image--loading'); }">
    #                     </picture>
    #                  </div>
    #                 </div>
    #                 <div class="tile__content-wrapper">
    #                   <h3 class="tile__title">ABBA in concert</h3>
    #                   <hr class="tile__divider" aria-hidden="true">
    #                   <div class="tile__description" id="ABBA in concert-description" aria-hidden="true">De concerttournee van ABBA in 1979</div>
    #                 </div>
    #                 <div class="tile__brand" aria-label="te zien op kanaal canvas">
    #                   <svg role="img" aria-hidden="true">
    #                     <title>Logo van canvas</title>
    #                     <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/etc/designs/vrtvideo/logos.svg#logo-canvas"></use>
    #                   </svg>
    #                 </div>
    #               </a>
    #             </li>
    #             <li class="vrtlist__item vrtglossary__item">
    #           </ul>
    #         </div>
    #       </div>
  xp = "//*[@id='{0}']".format(ref[1:].lower())
  pageElement = HTML.ElementFromURL(url)
  for item in pageElement.xpath(xp):
    for tile in item.xpath("./following-sibling::div//*[@class='tile']"): #<a
      t_href = tile.xpath("./@href")[0]
      url = config.VRT_BASE_URL + t_href
      t_image, t_title = VRTPlayer.get_thumbnail_and_title(tile)
      Log("t_title="+t_title)
      Log("t_image="+t_image)
      t_descr = VRTPlayer.get_description(tile)
      Log("t_descr="+t_descr)

      oc.add(
        DirectoryObject(
            key = Callback(Programs, title = t_title, url = t_href),
            title = t_title,
            summary = t_descr,
            thumb = t_image
        )
      )
  return oc

@route(PREFIX + "/programs")
def Programs(title, url, preselector = ""):
  oc = ObjectContainer(title2 = title, view_group = 'InfoList')
  pageURL = url if url.startswith("http") else config.VRT_BASE_URL + url
  pageElement = HTML.ElementFromURL(pageURL)
  found_elements = pageElement.xpath("{0}//*[@class='tile']".format(preselector))
  if (len(found_elements) == 0):
    Log("Programs-No episode tiles found, get episode from main")
    myStream = vrt_player.get_vrtnu_stream()
    MyShow = VRTPlayer.get_title(pageElement)
    MyThumb = VRTPlayer.format_image_url(pageElement)
    oc.add(createEpisodeObject(
            url=myStream.stream_url,
            title=myStream.title,
            summary=myStream.description,
            show_name=MyShow,
            duration=myStream.duration,
            thumb=MyThumb,
            rating_key=myStream.title))

  for tile in found_elements:
    t_image, t_title = VRTPlayer.get_thumbnail_and_title(tile)
    Log("episode t_title="+t_title)
    Log("episode t_image="+t_image)
    t_href = tile.xpath("./@href")[0]
    url = config.VRT_BASE_URL + t_href
    Log("episode url="+url)
    stream = vrt_player.get_vrtnu_stream(t_href)
    Log("episode stream_url="+stream.stream_url)

    oc.add(createEpisodeObject(
            url=stream.stream_url,
            title=t_title,
            summary=stream.description,
            show_name=title,
            duration=stream.duration,
            thumb=t_image,
            rating_key=t_title)) #,
            #originally_available_at=date,
            #show_name=show_name))

  return oc

@route(PREFIX + "/createepisodeobject")
def createEpisodeObject(url, title, summary, thumb, rating_key, originally_available_at=None, duration=None, show_name=None, include_container=False, **kwargs):
    track_object = EpisodeObject(
        key = Callback(
            createEpisodeObject,
            url=url,
            title=title,
            summary=summary,
            thumb=thumb,
            rating_key=rating_key,
            originally_available_at=originally_available_at,
            duration=duration,
            show_name=show_name,
            include_container=True
        ),
        rating_key = rating_key,
        title = title,
        summary = summary,
        thumb = thumb,
        originally_available_at = originally_available_at,
        duration = int(duration),
        producers = [],
        show = show_name,
        items = [
            MediaObject(
                #parts = [
                #    PartObject(key=Callback(PlayVideo, hls_url=url))
                parts = [
                    PartObject(key=HTTPLiveStreamURL(url))
                ],
                audio_channels = 2,
                # HTTPLiveStreamURL will set protocol = 'hls' container = 'mpegts' video_codec = VideoCodec.H264 audio_codec = AudioCodec.AAC. Other attributes you can set: video_resolution = '480' audio_channels = 2 optimized_for_streaming = True.
                #   protocol = 'hls',
                #   container = 'mpegts',
                #   video_codec = VideoCodec.H264,
                #   audio_codec = AudioCodec.AAC,
                # Other settings tried but not much better:
                #   bitrate = '1500',
                #   video_resolution = '720',
                #   container = Container.MP4,
                #   video_frame_rate = 60,
				optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

def PlayVideo(hls_url):
    return HTTP.Request(hls_url).content

# @indirect
# def PlayVideo(url, **kwargs):
#     return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url))
