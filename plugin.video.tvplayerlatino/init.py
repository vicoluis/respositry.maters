import sys, urllib, urllib2, cookielib, urlparse, json, xbmcgui, xbmcplugin, xbmcaddon

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
guid = xbmcaddon.Addon().getSetting('guid')
xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def add_directory(type, name):
    url = build_url({'type': type, 'name': name})
    li = xbmcgui.ListItem(name, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def add_subdirectory(type, name, id, art, fanart):
    url = build_url({'type': type, 'nombre': name, 'serie': id})
    li = xbmcgui.ListItem('[COLOR FF42A5F5]'+name+'[/COLOR]', thumbnailImage=art)
    li.setProperty('Fanart_Image', fanart)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def add_search(type, name, text):
    url = build_url({'type': type, 'name': name, 'search': True})
    li = xbmcgui.ListItem(text, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def add_item(name, uri, art, thumb=''):
    url = uri+'?'+guid if 'tvplayerlatino.com' in uri else uri
    li = xbmcgui.ListItem('[COLOR FF42A5F5]'+name+'[/COLOR]', iconImage=art, thumbnailImage=thumb)
    if art:
        li.setProperty('Fanart_Image', art)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

def get_url(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.11 (KHTML,like Gecko) fb.com/tvplayerlatino'}
    req = urllib2.Request(url, headers=hdr)
    response = urllib2.urlopen(req);
    data = response.read()
    response.close()
    return data

type = args.get('type', None)

if type is None:
    add_directory('menu', 'TV')
    add_directory('menu', 'Peliculas')
    add_directory('menu', 'Series')
    xbmcplugin.endOfDirectory(addon_handle)

    data = get_url("http://live.tvplayerlatino.com/api/guid")
    xbmcaddon.Addon().setSetting('guid', data)

elif type[0] == 'menu':
    name = args['name'][0]

    if name == 'TV':
        isSearch = args.get('search', False);
        if isSearch:
            q = xbmcgui.Dialog().input('Buscar')
            add_search('menu', 'TV', '[COLOR FF8BC34A]Buscando '+q+'[/COLOR]')
        else:
            add_search('menu', 'TV', '[COLOR FF8BC34A][B]Buscar...[/B][/COLOR]')

        data = json.loads(get_url('http://live.tvplayerlatino.com/kodi/tv'))

        for item in data:
            if isSearch:
                q = q.lower();
            if not isSearch or q in item[0].lower():
                add_item(item[0].encode('utf-8'), item[2], item[1])
        xbmcplugin.endOfDirectory(addon_handle)

    if name == 'Peliculas':
        isSearch = args.get('search', False)
        if isSearch:
            q = xbmcgui.Dialog().input('Buscar');
            add_search('menu', 'Peliculas', '[COLOR FF8BC34A]Buscando '+q+'[/COLOR]')
        else:
            add_search('menu', 'Peliculas', '[COLOR FF8BC34A][B]Buscar...[/B][/COLOR]')

        data = json.loads(get_url('http://live.tvplayerlatino.com/kodi/peliculas'))

        for item in data:
            if isSearch:
                q = q.lower();
            if not isSearch or q in item[0].lower():
                add_item(item[0].encode('utf-8'), 
                    'http://live.tvplayerlatino.com/movie/'+item[3]+'.mp4', 
                    item[2] if 'http' in item[2] else 'https://image.tmdb.org/t/p/w650/'+item[2],
                    item[1] if 'http' in item[1] else 'https://image.tmdb.org/t/p/w185/'+item[1])
        xbmcplugin.endOfDirectory(addon_handle)

    elif name == 'Series':
        isSearch = args.get('search', False)
        if isSearch:
            q = xbmcgui.Dialog().input('Buscar');
            add_search('menu', 'Series', '[COLOR FF8BC34A]Buscando '+q+'[/COLOR]')
        else:
            add_search('menu', 'Series', '[COLOR FF8BC34A][B]Buscar...[/B][/COLOR]')

        data = json.loads(get_url('http://live.tvplayerlatino.com/kodi/series'))

        for item in data:
            if isSearch:
                q = q.lower();
            if not isSearch or q in item[0].lower():
                add_subdirectory('serie', 
                    item[0].encode('utf-8'), 
                    item[3], 
                    item[1] if 'http' in item[1] else 'https://image.tmdb.org/t/p/w325/'+item[1], 
                    item[2] if 'http' in item[2] else 'https://image.tmdb.org/t/p/w650/'+item[2])
        xbmcplugin.endOfDirectory(addon_handle)

elif type[0] == 'serie':
        data = json.loads(get_url('http://live.tvplayerlatino.com/kodi/serie/'+args['serie'][0]))

        for item in data['episodios']:
            add_item(item[0], 'http://live.tvplayerlatino.com/episodio/'+item[1]+'.mp4',
             'https://image.tmdb.org/t/p/w325/'+data['backdrop'],
             'https://image.tmdb.org/t/p/w325/'+data['poster'])
        xbmcplugin.endOfDirectory(addon_handle)