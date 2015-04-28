import json, urllib, datetime, time, os,sys
from birdy import twitter
from pprint import pprint
from operator import itemgetter
import settings

# Hack to put script on current dir
try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass

# JSON Sample
# [0]  { content: ,
#        thumb: , 
#        author: ,   
#        width: ,
#        height:,
#        date_posted:,
#        media_type:,
#        media_provider:
#       }

class Media:
    '''Generic class for handling media type'''
    def __init__(self):
        self.content = None
        self.thumb = None
        self.author = None
        self.width = 0
        self.height = 0
        self.date_posted = datetime.datetime.now()
        self.original_url = None
        self.media_type = None
        self.media_provider = None
        
    def dictit(self):
        img = {
            'content' : self.content,
            'thumb' : self.thumb,
            'author' : self.author,
            'width' : self.width,
            'height' : self.height,
            'date_posted' : self.date_posted,
            'original_url': self.original_url,
            'media_type' : self.media_type,
            'media_provider' : self.media_provider
            }
        return img
    def timestamp(self, dt):
        return 1000 * time.mktime(dt.timetuple())
        
class Twitter:
    '''Remember to configure the Key and Secret'''
    def __init__(self, tag, api_key, api_secret):
        self.name   = 'Twitter'
        self.api_url = 'https://api.twitter.com/1.1/search/tweets.json?q=' + tag + ' filter:images&count=100&include_entities=true&result_type=recent'
        self.tag = tag
        self.api_key = api_key
        self.secret = api_secret
        
    def getPictures(self):
        print 'Getting ' + self.name
        print self.api_url
        client = twitter.AppClient(self.api_key, self.secret)
        self.access_token = client.get_access_token()
        client = twitter.AppClient(self.api_key, self.secret, self.access_token)
        pictures = []
        soap = client.make_api_call('GET', self.api_url).json()
        for raw_imagem in soap['statuses']:
            if raw_imagem.has_key('entities') and raw_imagem['entities'].has_key('media'):    
                imagem = Media()
                imagem.media_type = 'image'
                imagem.media_provider = self.name.lower()
                imagem.content = raw_imagem['entities']['media'][0]['media_url']
                imagem.thumb = raw_imagem['entities']['media'][0]['media_url']
                imagem.author = raw_imagem['user']['name']
                imagem.width = raw_imagem['entities']['media'][0]['sizes']['large']['w']
                imagem.height = raw_imagem['entities']['media'][0]['sizes']['large']['h']
                imagem.date_posted = imagem.timestamp(datetime.datetime.strptime(raw_imagem['created_at'], "%a %b %d %H:%M:%S +0000 %Y"))
                imagem.original_url = raw_imagem['entities']['media'][0]['expanded_url']
                pictures.append(imagem.dictit())
        return pictures
                

class Instagram:
    '''Remember to configure the api'''
    def __init__(self, tag, api_key):
        self.name = 'Instagram'
        self.api_url = 'https://api.instagram.com/v1/tags/' + tag + '/media/recent?client_id=' + api_key
        self.tag = tag
        self.api_key = api_key
        
    def getPictures(self):
        print 'Getting ' + self.name
        print self.api_url
        pictures = []
        soap = urllib.urlopen(self.api_url)
        soap = json.load(soap)
        for raw_imagem in soap['data']:
            imagem = Media()
            imagem.media_type = 'image'
            imagem.media_provider = self.name.lower()
            imagem.content = raw_imagem['images']['standard_resolution']['url']
            imagem.thumb = raw_imagem['images']['thumbnail']['url']
            imagem.author = raw_imagem['user']['username']
            imagem.width = raw_imagem['images']['standard_resolution']['width']
            imagem.height = raw_imagem['images']['standard_resolution']['height']
            imagem.date_posted = imagem.timestamp(datetime.datetime.fromtimestamp(float(raw_imagem['created_time'])))
            imagem.original_url = raw_imagem['link']
            pictures.append(imagem.dictit())
        return pictures

class Flickr:
    '''Remember to configure the api'''
    def __init__(self, tag, api_key):
        self.name   = 'Flickr'
        self.api_url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=' + api_key +'&text=' + tag +'&sort=&per_page=500&format=json&nojsoncallback=1&extras=owner_name,date_upload,url_t,url_l'
        self.tag = tag
        
    def getPictures(self):
        print 'Getting ' + self.name
        print self.api_url
        pictures = []
        soap = urllib.urlopen(self.api_url)
        soap = json.load(soap)
        for raw_imagem in soap['photos']['photo']:
            if raw_imagem.has_key('url_l'):
                imagem = Media()
                imagem.media_type = 'image'
                imagem.media_provider = self.name.lower()
                imagem.thumb = raw_imagem['url_t']
                imagem.author = raw_imagem['ownername']
                imagem.content = raw_imagem['url_l']
                imagem.width = raw_imagem['width_l']
                imagem.height = raw_imagem['height_l']
                imagem.date_posted = imagem.timestamp(datetime.datetime.fromtimestamp(float(raw_imagem['dateupload'])))
                imagem.original_url = 'http://www.flickr.com/photos/' + raw_imagem['owner'] + '/' + raw_imagem['id'] + '/'
                pictures.append(imagem.dictit())
        return pictures

class Picasa:
    def __init__(self, tag):
        self.name = 'Picasa'
        self.api_url = 'https://picasaweb.google.com/data/feed/base/all?alt=json&kind=photo&access=public&filter=1&q=' + tag + '&imgmax=1600&hl=pt_BR'
        self.tag = tag

    def getPictures(self):
        print 'Getting ' + self.name
        print self.api_url
        pictures = []
        soap = urllib.urlopen(self.api_url)
        soap = json.load(soap)
        for raw_imagem in soap['feed']['entry']:
            imagem = Media()
            imagem.media_type = 'image'
            imagem.media_provider = self.name.lower()
            imagem.author = [x['name']['$t'] for x in raw_imagem['author']]
            imagem.content = raw_imagem['content']['src']
            imagem.date_posted = imagem.timestamp(datetime.datetime.strptime(raw_imagem['published']['$t'], "%Y-%m-%dT%H:%M:%S.000Z"))
            imagem.original_url = [x['href'] for x in raw_imagem['link']][2]
            pictures.append(imagem.dictit())
        return pictures

class Youtube:
    def __init__(self, tag):
        self.name = 'Youtube'
        self.api_url = 'http://gdata.youtube.com/feeds/api/videos/-/' + tag + '?alt=json'
        self.tag = tag
    
    def getVideos(self):
        print 'Getting ' + self.name
        print self.api_url
        videos = []
        soap = urllib.urlopen(self.api_url)
        soap = json.load(soap)
        for raw_video in soap['feed']['entry']:
            video = Media()
            video.media_type = 'video' 
            video.media_provider = self.name.lower()
            video.content = raw_video['media$group']['media$content'][0]['url']
            video.thumb = raw_video['media$group']['media$thumbnail'][0]['url']
            video.author = raw_video['author'][0]['name']['$t']
            video.width = raw_video['media$group']['media$thumbnail'][0]['width']
            video.height = raw_video['media$group']['media$thumbnail'][0]['height']
            video.date_posted = video.timestamp(datetime.datetime.strptime(raw_video['updated']['$t'], "%Y-%m-%dT%H:%M:%S.000Z"))
            video.original_url = raw_video['link'][0]['href']
            if video.author != "YouTube Help":
                videos.append(video.dictit())
        return videos
            

def rockndroll():
    tag = settings.config['tag']
    flickr = Flickr(tag, settings.config['flickr_apikey']).getPictures()
    twitter = Twitter(tag, settings.config['twitter_apikey'], settings.config['twitter_secret']).getPictures()
    instagram = Instagram(tag, settings.config['instagram_apikey']).getPictures()
    picasa = Picasa(tag).getPictures()
    youtube = Youtube(tag).getVideos()
    lista_de_fotos =  instagram +  flickr + picasa + youtube
    lista_de_fotos = sorted(lista_de_fotos, key=itemgetter('date_posted'), reverse=True)
    a = open('muro.json','w')
    a.write(json.dumps(lista_de_fotos))
    a.close()

rockndroll()
