import scrapy

from scrapy.loader import ItemLoader

from ..items import AjmanbankaeItem
from itemloaders.processors import TakeFirst
import requests


payload={}
headers = {
  'Connection': 'keep-alive',
  'Content-Length': '0',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'Origin': 'https://www.ajmanbank.ae',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.ajmanbank.ae/site/media-center.html?start=2',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'PHPSESSID=rb4uar7it8p5to8vq84uqqj5pc; BNES_PHPSESSID=VaLEK74dhpJGNwSnH8y9ZunkbFbQUnJyBIa0NCFoPISboSCpvdrk4eR4ShDWepFPK6MgM3qiNiCwG1QyKWtTT9TM3DWOTWJNF9yLjr8z75I='
}


class AjmanbankaeSpider(scrapy.Spider):
	name = 'ajmanbankae'
	page = 1
	start_urls = ['https://www.ajmanbank.ae/site/media-center.html']

	def parse(self, response):
		data = requests.request("POST", f"https://www.ajmanbank.ae/site/ajax/ajax_news.php?start={self.page}", headers=headers, data=payload)
		data = scrapy.Selector(text=data.text)

		post_links = data.xpath('//div[@class="newslistingdata"]')
		for post in post_links:
			link = post.xpath('.//a[@class="newsreadmore"]/@href').get()
			date = post.xpath('.//div[@class="newsdate"]/text()').get()
			title = post.xpath('.//div[@class="newsheading"]/a/text()').get()
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})

		if post_links:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath('//div[contains(@class,"innerbodycontainer")]//p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AjmanbankaeItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
