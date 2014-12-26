import re
import random

def getArt(s, bool):
  try:
	s = s.replace(' ','+')
	field = ''
	if bool == True:
	 field = '&tbs=isz:m'
	page_data = HTML.ElementFromURL("http://www.google.com/search?biw=1440&bih=740&source=lnms&tbm=isch&sa=X&ei=VyaNVJ6iNcXIsAT5m4HABQ&sqi=2&ved=0CAgQ_AUoAw&tbm=isch&q="+s+"&revid=1657896103"+field)
	art = page_data.xpath("//div[@class='rg_di']/a/@href")[random.randint(1, 6)]
	art = art.replace('http://www.google.com/imgres?imgurl=','')
	#Log("google -- " + str(art))
	ind = art.index('&imgrefurl')
	ind = (-1*len(art))+ind
	#Log("index -------- " + str(ind))
	art = art[:ind]
	#Log("google -- " + str(art))
	if (len(art) < 10):
	 art = 'art-default.jpg'

	#Log("art -- " + str(art))

  except:
    art = R('art-default.jpg')

  return art