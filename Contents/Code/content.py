class Channel(object):
    def __init__(self, title, thumb, channel_id):
        self.title = title
        self.thumb = thumb
        self.channel_id = channel_id
            
        self.channel_url = "{0}/kanalen/{1}".format(config.VRTNU_BASE_URL, self.channel_id)
        
    def live_url(self):
        return "http://www.bbc.co.uk/iplayer/live/%s" % self.channel_id

tv_channels = {
    #                           title                 thumb               channel_id
    'een':              Channel('Eén'.decode("utf-8"),'een',              'een'),
    'canvas':           Channel('Canvas',             'canvas',           'canvas'),
}
ordered_tv_channels = ['een', 'canvas']

radio_stations = {
    'bbc_radio_one':                    'BBC Radio 1',
    'bbc_1xtra':                        'BBC 1Xtra',
    'bbc_radio_two':                    'BBC Radio 2',
    'bbc_radio_three':                  'BBC Radio 3',
    'bbc_radio_fourfm':                 'BBC Radio 4',
    'bbc_radio_four_extra':             'BBC Radio 4 Extra',
    'bbc_radio_five_live':              'BBC Radio 5 Live',
    'bbc_radio_five_live_sports_extra': 'BBC Radio 5 Live Sports Extra',
    'bbc_6music':                       'BBC 6 Music',
    'bbc_asian_network':                'BBC Asian Network',
    
}

ordered_radio_stations = [
    'bbc_radio_one',
    'bbc_1xtra',
    'bbc_radio_two',
    'bbc_radio_three',
    'bbc_radio_fourfm',
    'bbc_radio_four_extra',
    'bbc_radio_five_live',
    'bbc_radio_five_live_sports_extra',
    'bbc_6music',
    'bbc_asian_network'
]

