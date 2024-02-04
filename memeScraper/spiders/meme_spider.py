import scrapy
import requests
import os
from slugify import slugify
from urllib.parse import urlparse
from memeScraper.items import MemescraperItem


class memeSpider(scrapy.Spider):
    name = 'memes'
    start_urls = [
        "https://imgflip.com/gif-templates?page=1",
    ]
    def parse(self, response):
        meme_urls = response.xpath('//*[@id="mt-boxes-wrap"]//h3/a')
        for url in meme_urls:
            relative_url = url.css('a::attr(href)').get() #.replace("meme", "memetemplate")
            meme_url = 'https://imgflip.com' + relative_url
            yield scrapy.Request(url=meme_url, callback=self.parse_meme_data)
        next_page = response.css('#mt-boxes-wrap > div.pager > a.pager-next.l.but::attr(href)').get()
        next_meme_page = 'https://imgflip.com' + next_page
        yield scrapy.Request(next_meme_page, callback=self.parse)

    def parse_meme_data(self, response):
        item = MemescraperItem()
        item['title'] = response.css('#mtm-title::text').get()
        item["description"] = response.css('#mtm-subtitle::text').get()
        image_selector = response.css('#mtm-img::attr(src)').get()
        file_url = ''
        if image_selector and image_selector[2] is not 'i':
            file_url = 'https://imgflip.com/' + image_selector
        elif image_selector and image_selector[2] == 'i':
            file_url = 'https:' + image_selector
        elif response.css('#mtm-video > source::attr(src)').get() and response.css('#mtm-video > source::attr(src)').get()[2] == 'i':
            file_url = 'https:' + response.css('#mtm-video > source::attr(src)').get()
        else:
            file_url = 'https://imgflip.com/' + response.css('#mtm-video > source::attr(src)').get()
        url = urlparse(file_url)
        image_name = os.path.basename(url.path)
        r = requests.get(file_url, stream=True)
        item["img"] = image_name
        item["slug"] = slugify(item['title'])
        with open(os.path.join('images', image_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=255):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        yield item
