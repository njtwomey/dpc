"""Fetching pages and turning them into rows."""

from dpc.scrape.cache import HtmlCache
from dpc.scrape.client import DpcClient, LoginError
from dpc.scrape.crawl import Crawler, CrawlStats
from dpc.scrape.encoding import decode_html

__all__ = ["CrawlStats", "Crawler", "DpcClient", "HtmlCache", "LoginError", "decode_html"]
