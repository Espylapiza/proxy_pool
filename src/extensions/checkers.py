class HttpbinChecker(object):
    url = "https://httpbin.org/ip"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "https://" + proxy
        return (self.url, kwargs)

    def check(self, proxy, response):
        return len(response.text) > 0


class ScooterlabsChecker(object):
    """
    A website echoing headers.
    """

    url = "http://scooterlabs.com/echo"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "http://" + proxy
        return (self.url, kwargs)

    def check(self, proxy, response):
        return len(response.text) > 0


class IpinfoChecker(object):
    url = "https://ipinfo.io/json"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "https://" + proxy
        return (self.url, kwargs)

    def check(self, proxy, response):
        return len(response.text) > 0


class IpapiChecker(object):
    url = "https://ipapi.co/json"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "https://" + proxy
        return (self.url, kwargs)

    def check(self, proxy, response):
        return len(response.text) > 0


class AnjukeChecker(object):
    url = "https://shanghai.anjuke.com/"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "https://" + proxy
        headers = {"Accept-language": "zh-CN,zh;q=0.8,en;q=0.6"}
        kwargs["headers"] = headers
        return (self.url, kwargs)

    def check(self, proxy, response):
        url = response.request.url
        return (
            "captcha-verify" not in url
            and "antispam" not in url
            and len(response.text) > 0
        )


class MomoChecker(object):
    url = "https://www.maimemo.com/"

    def request(self, proxy, **kwargs):
        kwargs["proxy"] = "https://" + proxy
        headers = {"Accept-language": "zh-CN,zh;q=0.8,en;q=0.6"}
        kwargs["headers"] = headers
        return (self.url, kwargs)

    def check(self, proxy, response):
        return len(response.text) > 0

