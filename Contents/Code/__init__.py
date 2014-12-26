######################################################################################
#
#	HindiLinks4u.to - v0.01
#
######################################################################################

import common_functions

TITLE = "HindiLinks4u"
PREFIX = "/video/hindilinks4u"
ART = "art-default.jpg"
ICON = "icon-hindilinks4u.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://HindiLinks4u.to"
CATEGORY_URL = 'http://HindiLinks4u.to/category'
CATEGORIES_URL = 'http://HindiLinks4u.to/'
MOVIES_URL = "http://HindiLinks4u.to/category"
SEARCH_URL = "http://www.hindilinks4u.to/"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	#HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
	HTTP.Headers['Referer'] = 'HindiLinks4u.to'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	
    oc = ObjectContainer(title2=TITLE)
    oc.add(InputDirectoryObject(key = Callback(Search, page_count=1), title='Search', summary='Search Movies', prompt='Search for...'))
    channel_page = HTML.ElementFromURL(CATEGORIES_URL)
    channels = channel_page.xpath("//div[@id='categories-5']/ul/li")
    oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "My Movie Bookmarks", thumb = R(ICON_QUEUE)))
    oc.add(PrefsObject(title = 'Preferences', thumb = R('icon-prefs.png')))
    for each in channels:
        #Log("each---------" + string(each))
        url = each.xpath("./a/@href")[0]
        title = each.xpath("./a/text()")[0]
        if (title == "Adult") or (title == "Mature"):
          if Prefs['adult_cat_bool']:
            Log("title--------------------"+title+ ' ' + str(Prefs['adult_cat_bool']))
            oc.add(DirectoryObject(key = Callback(ShowCategory, title = title, category = url, page_count = 1), title = title, thumb = R(ICON_MOVIES)))
        else:
            oc.add(DirectoryObject(key = Callback(ShowCategory, title = title, category = url, page_count = 1), title = title, thumb = R(ICON_MOVIES)))
 
    tags = channel_page.xpath("//div[@class='tagcloud']/a")
    i=0
    while(i < len(tags)):
        each = tags[i]
        #Log("each---------" + string(each))
        url = each.xpath("./@href")[0]
        title = each.xpath("./text()")[0]
        oc.add(DirectoryObject(key = Callback(ShowCategory, title = title, category = url, page_count = 1), title = title, thumb = R(ICON_MOVIES)))
        i=i+1

    return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	categorytitle = title
	oc = ObjectContainer(title1 = title)
	if str(page_count) == "1":
		page_data = HTML.ElementFromURL(str(category))
	else:
		page_data = HTML.ElementFromURL(str(category) + '/page/' + str(page_count))
	
	movies = page_data.xpath("//div[contains(@class,'-post-')]")
	for each in movies:
		url = each.xpath("div/a/@href")
		#Log("url--------" + str(url))
		title = each.xpath("div/a/@title")[0]
		#Log("title--------" + str(title))
		thumb = each.xpath("div/a/span/img/@src")
		#Log("thumb--------" + str(thumb))
		summary = each.xpath("div[@class='data']/p/text()")[2]
		#Log("summary--------" + str(summary))

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url, thumb = thumb, summary = summary),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=R(ICON_MOVIES))
			)
		)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = categorytitle, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb, summary):
	
	art = common_functions.getArt(title+'+movie', False)
	oc = ObjectContainer(title1 = title, art=art)
	page_data = HTML.ElementFromURL(url)
	
	title = title
	description = summary
	thumb = thumb
	directors = GetDirectors(page_data)
	stars = GetStarring(page_data)
	genres = GetGenres(page_data)
	releaseDate = GetReleaseDate(page_data)
	writers = GetWriters(page_data)
	rate = GetImdbRating(page_data)
	duration = getMovDuration(page_data)
	
	
	try:
		trailer_url = page_data.xpath("//a[@class='trailer btn external']/@href")[0]
		oc.add(VideoClipObject(
			url = trailer_url,
			title = 'Trailer of ' + title,
			art = art,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
			summary = description
		)
	)	
	except:
		trailer_url = ""

	try:
		#url = page_data.xpath("//iframe/@src")[0]
		oc.add(VideoClipObject(
			url = url,
			art = art,
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
			summary = description
		)
	)
	except:
		url = ""
	if Prefs['exp_alt_src']:
		try:
			other_url = ''
			other_url = page_data.xpath("//div[@class='entry-content rich-content']/p/a/@href")
			#other_url_type = page_data.xpath("//div[@class='entry-content rich-content']/p/a/@href/preceding-sibling::strong/text()")
			Log("----------- other url ----------------")
			Log(other_url)
		except:
			other_url = ""
		i=0
		c=0
		while(i < len(other_url)):
			each = other_url[i]
			if each.lower().find('filmshowonline') != -1:
				Log("filmshowonline---------------" + each)
				try:
					c=c+1
					oc.add(VideoClipObject(
						url = each,
						art = art,
						title = str(title) + '   Alternate source ' + str(c),
						thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
						summary = description
						)
					)
				except:
					continue
			if each.lower().find('ipithos') != -1:
				each = each.replace('http://www.ipithos.to/','')
				each = 'http://www.ipithos.to/embed-' + each + '.html'
				try:
					c=c+1
					oc.add(VideoClipObject(
						url = each,
						art = art,
						title = str(title) + '   Alternate source ' + str(c),
						thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
						summary = description
						)
					)
				except:
					continue
			i=i+1
	
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			art = art,
			summary = 'Removes the current movie from the Boomark que',
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url),
			title = "Bookmark Video",
			summary = 'Adds the current movie to the Boomark que',
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)

	return oc
####################################################################################################


######################################################################################

def GetDirectors(html):
	try:
		str = html.xpath("//div[@id='entry-content rich-content']/p/text()")[0]
	except:
		str = ''
	return str
  
def GetStarring(html):
	try:
		str = html.xpath("//div[@id='entry-content rich-content']/p/text()")[1]
	except:
		str = ''
	return str
	
def GetGenres(html):
	try:
		str = html.xpath("//div[@id='entry-content rich-content']/p/text()")[0]
		Log("genres============" + str)
		str = str.replace(' ','')
		str = str.replace(':','')
	except:
		str = 'Drama'
	return str

def ParseGenres(str):
	try:
		str = str.replace(' ','')
		strs = str.split('|')
	except:
		strs = []
		strs.append("Drama")
    #Log('Summary: ' +summary)
	return strs

def GetReleaseDate(html):
	try:
		str = html.xpath("//div[@id='entry-content rich-content']/p/text()")[3]
	except:
		str = ''
	return str
	
def GetWriters(html):
	try:
		str = html.xpath("//div[@id='entry-content rich-content']/p/text()")[4]
	except:
		str = ''
	return str

def GetImdbRating(html):
	try:
		rate = html.xpath("//div[@id='entry-content rich-content']/p/text()")[5]
		rate = re.sub(r'(?is)/10.+', '', rate)
	except:
		rate = '5.0'
	return rate
	
def getMovDuration(html):
	try:
		rate = html.xpath("//div[@id='entry-content rich-content']/p/text()")[6]
	except:
		rate = '5.0'
    #Log('Summary: ' +summary)
	return rate

	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1:
			page_data = HTML.ElementFromURL(url)
			title = each
			try:
				thumb = page_data.xpath("//div[@id='thumb']/img/@src")[0]
			except:
				thumb = page_data.xpath("//div[@id='video']/meta/@content")
			try:
				summary = page_data.xpath("//meta[@name='description']/@content")[0]
			except:
				summary = 'Description not available !'
			
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url, thumb=thumb, summary=summary),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No Bookmarked Videos Available')
	return oc

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")	
def Check(title, url):
	bool = False
	url = Dict[title]
	#Log("url-----------" + url)
	if url != None and (url.lower()).find(TITLE.lower()) != -1:
		bool = True
	
	return bool

######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url):
	
	Dict[title] = url
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been added to your bookmarks.')
######################################################################################
# Removes a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url):
	
	Dict[title] = 'removed'
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been removed from your bookmarks.')	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	Dict.Reset()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.')

####################################################################################################
@route(PREFIX + "/search")
def Search(query, page_count):

	oc = ObjectContainer(title2='Search Results')
	if str(page_count) == "1":
		data = HTTP.Request(SEARCH_URL + '?s=%s' % String.Quote(query, usePlus=True), headers="").content
	else:
		data = HTTP.Request((SEARCH_URL + '/page/' + str(page_count)) + '?s=%s' % String.Quote(query, usePlus=True), headers="").content
	
	page_data = HTML.ElementFromString(data)
	
	movies = page_data.xpath("//div[contains(@class,'-post-')]")
	for each in movies:
		url = each.xpath("div/a/@href")
		#Log("url--------" + str(url))
		title = each.xpath("div/a/@title")[0]
		#Log("title--------" + str(title))
		thumb = each.xpath("div/a/span/img/@src")
		#Log("thumb--------" + str(thumb))
		summary = each.xpath("div[@class='data']/p/text()")[2]
		#Log("summary--------" + str(summary))

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url, thumb = thumb, summary = summary),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=R(ICON_MOVIES))
			)
		)

	oc.add(NextPageObject(
		key = Callback(Search, query=query, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc
####################################################################################################