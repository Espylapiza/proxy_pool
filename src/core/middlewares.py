import logging
from scrapy.downloadermiddlewares.defaultheaders import DefaultHeadersMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from settings import RETRY_TIMES
import database as db

logger = logging.getLogger(__name__)


class HeadersMiddleware(DefaultHeadersMiddleware):
    def process_request(self, request, spider):
        request.headers["Accept"] = "*/*"
        request.headers["Accept-Encoding"] = "gzip, deflate"
        request.headers["Accept-Language"] = "en"
        request.headers["Method"] = "GET"
        request.headers["Cache-Control"] = "max-age=0"
        request.headers["Dnt"] = "1"
        request.headers["Upgrade-Insecure-Requests"] = "1"
        if "headers" in request.meta:
            for key, value in request.meta["headers"].items():
                request.headers[key] = value


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        import fake_useragent

        request.headers["User-Agent"] = fake_useragent.UserAgent().random


class ProxyMiddleware(HttpProxyMiddleware):
    def process_request(self, request, spider):
        proxy = request.meta.get("proxy")
        if proxy is not None:
            if not proxy.startswith("http"):
                if request.url.startswith("https://"):
                    proxy = "https://" + proxy
                else:
                    proxy = "http://" + proxy
                request.meta["proxy"] = proxy


class MyRetryMiddleware(RetryMiddleware):
    def _retry(self, request, spider):
        retry_times = request.meta.get("retry_times", 0)
        if retry_times < RETRY_TIMES:
            retryreq = request.copy()
            retryreq.meta["retry_times"] = retry_times + 1
            retryreq.priority = request.priority - 2
            return retryreq
        else:
            if "request" in request.meta:
                proxy = request.meta.get("proxy")
                if proxy is not None:
                    proxy = proxy[proxy.rindex("/") + 1 :]
                    db.base_proxy_rem(proxy)

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get(
            "dont_retry", False
        ):
            return self._retry(request, spider)

    def process_response(self, request, response, spider):
        if request.meta.get("dont_retry", False):
            return response

        if response.status in self.retry_http_codes:
            return self._retry(request, spider)

        return response
