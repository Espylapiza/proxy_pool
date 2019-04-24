from itertools import cycle
from lxml import etree
import re
import base64
import database as db


class Source(object):
    url_list = list()

    def __init__(self):
        self.iter = self.url_gen()

    def url_gen(self):
        for url in cycle(self.url_list):
            yield url

    def next_url(self):
        return next(self.iter)


class SourceData5u(Source):
    """
    http://www.data5u.com/
    """

    url_list = [
        "http://www.data5u.com/",
        "http://www.data5u.com/free/index.shtml",
        "http://www.data5u.com/free/gngn/index.shtml",
        "http://www.data5u.com/free/gnpt/index.shtml",
        "http://www.data5u.com/free/gwgn/index.shtml",
        "http://www.data5u.com/free/gwpt/index.shtml",
    ]

    def parse(self, html):
        html_tree = etree.HTML(html)
        ul_list = html_tree.xpath('//ul[@class="l2"]')
        for ul in ul_list:
            yield ":".join(ul.xpath(".//li/text()")[0:2])


class Source66ip(Source):
    """
    代理66 http://www.66ip.cn/
    """

    url_list = [
        f"http://www.66ip.cn/areaindex_{area_index}/{i}.html"
        for area_index in range(1, 34)
        for i in range(1, 2)
    ]

    def parse(self, html):
        html_tree = etree.HTML(html)
        tr_list = html_tree.xpath("//*[@id='footer']/div/table/tr[position()>1]")
        for tr in tr_list:
            try:
                yield tr.xpath("./td[1]/text()")[0] + ":" + tr.xpath("./td[2]/text()")[
                    0
                ]
            except Exception:
                pass


class SourceXici(Source):
    """
    西刺代理 https://www.xicidaili.com
    """

    url_list = [
        "https://www.xicidaili.com/nn/",  # 高匿
        "https://www.xicidaili.com/nt/",  # 透明
    ]

    def parse(self, html):
        html_tree = etree.HTML(html)
        proxy_list = html_tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
        for proxy in proxy_list:
            try:
                yield ":".join(proxy.xpath("./td/text()")[0:2])
            except Exception:
                pass


class SourceGoubanjia(Source):
    """
    http://www.goubanjia.com/
    """

    url_list = ["http://www.goubanjia.com"]

    def parse(self, html):
        html_tree = etree.HTML(html)
        proxy_list = html_tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = "".join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield "{}:{}".format(ip_addr, port)
            except Exception:
                pass


class SourceKuaidaili(Source):
    """
    https://www.kuaidaili.com/
    """

    url_list = [
        f"https://www.kuaidaili.com/free/{proxy_type}/{page}/"
        for proxy_type in ["inha", "intr"]
        for page in range(1, 5)
    ]

    def parse(self, html):
        html_tree = etree.HTML(html)
        proxy_list = html_tree.xpath(".//table//tr")
        for tr in proxy_list[1:]:
            yield ":".join(tr.xpath("./td/text()")[0:2])


class Sourceip3366(Source):
    """
    云代理 http://www.ip3366.net/free/
    """

    url_list = ["http://www.ip3366.net/free/"]

    def parse(self, html):
        proxies = re.findall(
            r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>", html
        )
        for proxy in proxies:
            yield ":".join(proxy)


class Sourceiphai(Source):
    """
    IP海 http://www.iphai.com
    """

    url_list = [
        "http://www.iphai.com/free/ng",
        "http://www.iphai.com/free/np",
        "http://www.iphai.com/free/wg",
        "http://www.iphai.com/free/wp",
    ]

    def parse(self, html):
        proxies = re.findall(
            r"<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>",
            html,
        )
        for proxy in proxies:
            yield ":".join(proxy)


class SourceJiangxianli(Source):
    """
    Jiangxianli http://ip.jiangxianli.com
    """

    url_list = [f"http://ip.jiangxianli.com/?page={page}" for page in range(1, 9)]

    def parse(self, html):
        html_tree = etree.HTML(html)
        tr_list = html_tree.xpath("/html/body/div[1]/div/div[1]/div[2]/table/tbody/tr")
        for tr in tr_list:
            yield tr.xpath("./td[2]/text()")[0] + ":" + tr.xpath("./td[3]/text()")[0]


class Sourcecnproxy(Source):
    """
    cn-proxy https://cn-proxy.com/
    """

    url_list = ["https://cn-proxy.com/", "https://cn-proxy.com/archives/218"]

    def parse(self, html):
        proxies = re.findall(
            r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>", html
        )
        for proxy in proxies:
            yield ":".join(proxy)


class Sourceproxylist(Source):
    """
    https://proxy-list.org/english/index.php
    """

    url_list = [
        f"https://proxy-list.org/english/index.php?p={page}" for page in range(1, 10)
    ]

    def parse(self, html):
        proxies = re.findall(r"Proxy\('(.*?)'\)", html)
        for proxy in proxies:
            yield base64.b64decode(proxy).decode()


class Sourceproxylistplus(Source):
    """
    https://list.proxylistplus.com
    """

    url_list = ["https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1"]

    def parse(self, html):
        proxies = re.findall(
            r"<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>", html
        )
        for proxy in proxies:
            yield ":".join(proxy)


class Source89ip(Source):
    """
    http://www.89ip.cn
    """

    url_list = [f"http://www.89ip.cn/index_{page}.html" for page in range(1, 11)]

    def parse(self, html):
        html_tree = etree.HTML(html)
        proxy_list = html_tree.xpath(".//table//tr")
        for tr in proxy_list[1:]:
            yield ":".join(tr.xpath("./td")[i].text.strip() for i in range(0, 2))


class SourceProxyScrape(Source):
    """
    https://proxyscrape.com/api?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all
    """

    url_list = [
        "https://proxyscrape.com/api?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all"
    ]

    def parse(self, html):
        proxy_list = html.split()
        for proxy in proxy_list:
            yield proxy


class SourceFromDatabase(Source):
    url_list = ["https://httpbin.org/ip"]

    def parse(self, html):
        for proxy in db.base_proxy_rand(10):
            yield str(proxy, "utf-8")

