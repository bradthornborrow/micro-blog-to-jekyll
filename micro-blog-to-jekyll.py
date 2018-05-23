#!/usr/bin/env python
 
import xmlrpclib
import re, string, sys, time, urllib, urlparse
from datetime import datetime, timedelta

def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

# micro.blog domain details
app_token = ''
# enter micro.blog or custom domain name (to properly handle micro.blog img links)
domain = 'www.thedeskofbrad.ca'
user_id = 'thedeskofbrad'
# maximum number of posts expected in time range scanned 
max_posts = 3

# micro.blog xml-rpc server endpoint
server = xmlrpclib.ServerProxy('https://micro.blog/xmlrpc')
posts = server.metaWeblog.getRecentPosts(domain, user_id, app_token, max_posts)

# jekyll blog path
jekyll_root = '/home/pi/git/thedeskofbrad.github.io'
jekyll_post_layout = "single"

# time range to scan posts
time_range = datetime.now() - timedelta(hours = 24)

for post in posts:
	# Correct for UTC date returned from micro.blog API
	dateCreated = datetime_from_utc_to_local(datetime.strptime(str(post['dateCreated'])[:-1], '%Y%m%dT%H:%M:%S'))
	# Download posts with titles in selected time range
	if dateCreated > time_range and post['title'] != "":
		title = post['title']
		content = post['description']
		
		# If there is a micro.blog img attribute, download the image to Jekyll blog assets folder
		img = re.search("(?P<url>img src=\"https?://"+domain+"[^\"]+)", content)
		if img is not None:
			img_url = img.group("url")[9:]
			img_filename = img_url.split("/")[-1] 
			download_path = jekyll_root + "/assets/images/" + img_filename
			download = urllib.URLopener()
			download.retrieve(img_url, download_path)
			content = string.replace(content, img_url, '{{ site.url }}/assets/images/' + img_filename)

		jekyll_post_filename = dateCreated.strftime("%Y-%m-%d") + '-' + title.replace(" ","-") + ".md"		
		with open(jekyll_root + "/_posts/" + jekyll_post_filename, "w") as text_file:
			text_file.write("---\n")
			text_file.write("layout: " + jekyll_post_layout + "\n")
			text_file.write("title: " + title + "\n")
			text_file.write("date: " + dateCreated.strftime("%Y-%m-%d %H:%M:%S") + "\n")
			text_file.write("---\n")
			text_file.write(content.encode("utf-8"))
