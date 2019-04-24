# Database Settings
DB_PORT = 6379
DB_NUM = 0
DB_PASSWD = "redis_passroed"

DB_BASE_PROXY_EXPIRE = 36000
DB_PROXY_EXPIRE = 72000

# Scrapy Settings
RETRY_TIMES = 4
RETRY_INTERVAL = 2
TIMEOUT = 20

# Proxy sources
PROXY_SOURCES = [
    "extensions.sources.SourceProxyScrape",
    "extensions.sources.Sourceip3366",
    "extensions.sources.SourceXici",
    "extensions.sources.Sourceproxylist",
    "extensions.sources.Source66ip",
    "extensions.sources.Source89ip",
    # "extensions.sources.SourceJiangxianli",
    # "extensions.sources.Sourceiphai",
    # "extensions.sources.SourceData5u",
    # "extensions.sources.SourceKuaidaili",
    # "extensions.sources.Sourceproxylistplus",
    # "extensions.sources.SourceGoubanjia",
    # "extensions.sources.Sourcecnproxy",
    "extensions.sources.SourceFromDatabase",
]

# Base proxy checkers
# The proxy_pool requests proxies from sources
# using base proxies in case of being banned.
BASE_CHECKER = "extensions.checkers.HttpbinChecker"

# Proxy checkers
CHECKERS = ["extensions.checkers.HttpbinChecker"]
