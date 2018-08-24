import requests
from lxml import etree

def run():
	url = 'https://www.feixiaohao.com/currencies/bitcoin/';
	response = requests.get(url)
	price = etree.HTML(response.text).xpath('//div[@class="sub"]/span/text()')[0][1:]
	rate = etree.HTML(response.text).xpath('//span[@class="tags-green"]/text()')[0]
	print("比特币价格：%s, 24H涨幅：%s" % (price,rate))
run()