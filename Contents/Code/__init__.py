import config
import re
import urltostreamservice
from vrtplayer import VRTPlayer

TITLE    = 'VRT Nu'
PREFIX   = '/video/vrtnu'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

##########################################################################################
def Start():
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items', summary=1)
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'InfoList'
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  #HTTP.CacheTime = CACHE_1HOUR

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

  title = "Kanalen"
  oc.add(
    DirectoryObject(
        key = Callback(Channels, title = title, url = config.VRTNU_BASE_URL + '/kanalen'),
        title = title
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
def Programs(title, url):
  oc = ObjectContainer(title2 = title, view_group = 'InfoList')
  pageElement = HTML.ElementFromURL(config.VRT_BASE_URL + url)
  u2s = urltostreamservice.UrlToStreamService(config.VRT_BASE_URL, config.VRTNU_BASE_URL)
  vrt_player = VRTPlayer(u2s)
  for tile in pageElement.xpath("//*[@class='tile']"): #<a
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
                parts = [
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
				        optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

@indirect
def PlayVideo(url, **kwargs):
    return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url))

##########################################################################################
@route(PREFIX + '/tvchannels')
def Channels(title):

    oc = ObjectContainer(title2 = title)

    # for channel_id in content.ordered_tv_channels:
    #     channel = content.tv_channels[channel_id]

    #     oc.add(
    #         DirectoryObject(
    #             key = 
    #                 Callback(
    #                     Channel, 
    #                     channel_id = channel_id
    #                 ),
    #             title = channel.title,
    #             summary = unicode(L(channel_id)),
    #             thumb = R("%s.png" % channel_id)
    #         )
    #     )

    return oc

###############################################################################################################
# OTHER THINGS TO LOOK AT WHEN DESIGNING YOUR CHANNEL
###############################################################################################################
#
# DEBUG LOG MESSAGES
# ANYWHERE IN YOUR CODE THAT YOU WANT TO PUT A DEBUG CODE THAT RETURNS A LINE OF TEXT OR A VARIABLE
# YOU WOULD USE THE LOG COMMAND.  THE PROPER FORMAT IS BELOW:
# To just include a statement, add Log('I am here') To return the value of a variable VAR in the log statement, 
# you would add Log('the value of VAR is %s' %VAR)
#
# PYTHON STRING METHODS
# CHECK OUT THE PYTHON STRING METHODS. THESE GIVE YOU SEVERAL WAYS TO MANIPULATE STRINGS THAT CAN BE HELPFUL IN YOUR CHANNEL CODE
# THIS IS A GOOD PAGE WITH BASIC TUTORIALS AND EXPLANATIONS FOR STRING METHODS: 'http://www.tutorialspoint.com/python/python_strings.htm'
#
# XML XPATH CHECKER
# TRADITIONAL XPATH CHECKERS DO NOT WORK ON XML PAGES. HERE IS A LINK TO AN XML XPATH CHECKING PROGRAM THAT IS VERY HELPFUL
# 'http://chris.photobooks.com/xml/default.htm'
# 
# TRY/EXCEPT 
# TRY IS GOOD FOR SITUATIONS WHERE YOUR XPATH COMMANDS MAY OR MAY NOT WORK. IF YOUR XPATH IS OUT OF RANGE YOU WILL GET ERRORS IN YOUR
# CODE.  USING TRY ALLOWS YOU TO TRY THE XPATH AND IF IT DOESN'T WORK, PUT ALTERNATIVE CODE UNDER EXCEPT AND YOU WILL NOT GET ERRORS
# IN YOUR CODE
#
# DICT[] 
# DICT[] IS PART OF THE PLEX FRAMEWORK THAT ALLOWS YOU TO SAVE DATA IN A GLOBAL VARIABLE THAT IS RETAINED WHEN YOU EXIT THE PLUGIN
# SO YOU CAN PULL IT UP IN MULTIPLE FUNCTIONS WITHOUT PASSING THE VARIABLES FROM FUNCTION TO FUNCTION. AND IT CAN BE ACCESSED AND USED
# OVER MULTIPLE SESSIONS