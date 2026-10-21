"""
CrawlerRunConfig(word_count_threshold=N) must reach the default LXML scraper.
Previously _scrap() called remove_empty_elements_fast(body, 1) with a hard
coded 1, so the configured threshold was ignored.
"""

import pytest

from crawl4ai import CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

HTML = (
    "<html><body>"
    "<p>too short</p>"
    "<p>this paragraph has exactly seven words total</p>"
    "<div></div>"
    "</body></html>"
)


@pytest.fixture
def strategy():
    return LXMLWebScrapingStrategy()


def scrap(strategy, **config_kwargs):
    # Same path as AsyncWebCrawler: the config's attributes become kwargs.
    params = CrawlerRunConfig(**config_kwargs).__dict__.copy()
    params.pop("url", None)
    return strategy.scrap("http://test.com", HTML, **params).cleaned_html


def test_block_under_threshold_is_removed(strategy):
    cleaned = scrap(strategy, word_count_threshold=5)
    assert "too short" not in cleaned
    assert "exactly seven words" in cleaned


def test_block_at_threshold_is_kept(strategy):
    cleaned = scrap(strategy, word_count_threshold=2)
    assert "too short" in cleaned


def test_threshold_above_every_block_removes_all_text(strategy):
    cleaned = scrap(strategy, word_count_threshold=8)
    assert "too short" not in cleaned
    assert "exactly seven words" not in cleaned


def test_default_threshold_keeps_text_and_drops_empty_elements(strategy):
    cleaned = scrap(strategy)
    assert "too short" in cleaned
    assert "exactly seven words" in cleaned
    assert "<div>" not in cleaned
