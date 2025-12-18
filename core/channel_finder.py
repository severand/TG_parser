"""Channel Finder module for discovering Telegram channels and chats."""

import re
import time
import random
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from utils.logger import Logger
from utils.exceptions import ParserException, RateLimitException

logger = Logger.get_instance()


@dataclass
class FoundChannel:
    """Discovered channel/chat information."""
    username: str
    title: str
    url: str
    description: str = ""
    subscribers: int = 0
    channel_type: str = "channel"
    category: str = ""
    language: str = ""
    verified: bool = False
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class SearchSession:
    """Tracks search session state."""
    session_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:16])
    started_at: datetime = field(default_factory=datetime.now)
    requests_count: int = 0
    user_agent: str = ""


class AntiDetection:
    """Anti-detection system with human-like behavior."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    ]

    def __init__(self, aggression_level: str = "medium"):
        self.aggression_level = aggression_level
        self.session = SearchSession()
        self.session.user_agent = random.choice(self.USER_AGENTS)

        self.delay_profiles = {
            'low': {'base': (3.0, 8.0), 'page': (5.0, 15.0)},
            'medium': {'base': (1.5, 4.0), 'page': (3.0, 8.0)},
            'high': {'base': (0.5, 1.5), 'page': (1.0, 3.0)},
        }
        logger.info(f"AntiDetection initialized: level={aggression_level}")

    def wait(self, delay_type: str = 'base'):
        profile = self.delay_profiles[self.aggression_level]
        min_d, max_d = profile.get(delay_type, profile['base'])
        delay = random.uniform(min_d, max_d)
        if random.random() < 0.1:
            delay *= random.uniform(1.5, 2.5)
        time.sleep(delay)


class BrowserFinder:
    """Browser-based finder using Selenium."""

    def __init__(self, anti_detection: AntiDetection, headless: bool = True):
        self.anti_detection = anti_detection
        self.headless = headless

        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not installed. Run: pip install selenium webdriver-manager")

        logger.info(f"BrowserFinder initialized: headless={headless}")

    def _create_driver(self):
        """Create Chrome driver with anti-detection."""
        options = Options()

        if self.headless:
            options.add_argument('--headless=new')

        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={self.anti_detection.session.user_agent}')
        options.add_argument('--lang=ru-RU')

        # Disable automation flags
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Remove webdriver flag
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            '''
        })

        return driver

    def search(self, query: str, limit: int = 50, channel_type: str = "all") -> List[FoundChannel]:
        """Search TGStat using Selenium."""
        results = []
        driver = None

        try:
            driver = self._create_driver()

            # Build URL
            if channel_type == 'chat':
                url = f"https://tgstat.ru/chats/search?q={quote_plus(query)}"
            else:
                url = f"https://tgstat.ru/channels/search?q={quote_plus(query)}"

            logger.info(f"Browser: navigating to {url}")
            driver.get(url)

            # Wait for page load
            time.sleep(2)

            # Try to find and fill search input
            try:
                search_input = driver.find_element(By.CSS_SELECTOR,
                                                   'input[type="text"], input[name="q"], input[placeholder*="поиск"], input[placeholder*="search"]')
                search_input.clear()
                search_input.send_keys(query)
                logger.info(f"Browser: typed '{query}' in search")

                # Press Enter or find search button
                search_button = driver.find_element(By.CSS_SELECTOR,
                                                    'button[type="submit"], button[class*="search"], form button')
                search_button.click()
                logger.info("Browser: clicked search button")

                # Wait for results
                time.sleep(3)
            except Exception as e:
                logger.warning(f"Could not fill search form: {e}")

            self.anti_detection.wait('page')

            pages_loaded = 0
            max_pages = (limit // 20) + 1

            while len(results) < limit and pages_loaded < max_pages:
                # Parse current page
                html = driver.page_source
                page_results = self._parse_html(html)

                if not page_results:
                    logger.debug("No results found on page")
                    break

                # Add only new results
                existing = {r.username for r in results}
                new_results = [r for r in page_results if r.username not in existing]
                results.extend(new_results)

                logger.info(f"Browser: found {len(results)} channels so far")

                if len(results) >= limit:
                    break

                # Try to click next page
                try:
                    next_buttons = driver.find_elements(By.CSS_SELECTOR, 'a.page-link, .pagination a')
                    found_next = False
                    for btn in next_buttons:
                        if 'next' in btn.get_attribute('rel').lower() or 'далее' in btn.text.lower() or '»' in btn.text:
                            btn.click()
                            self.anti_detection.wait('page')
                            pages_loaded += 1
                            found_next = True
                            break

                    if not found_next:
                        break

                except Exception as e:
                    logger.debug(f"No next button: {e}")
                    break

        except Exception as e:
            logger.error(f"Browser error: {e}")
        finally:
            if driver:
                driver.quit()

        return results[:limit]

    def _parse_html(self, html: str) -> List[FoundChannel]:
        """Parse TGStat HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # Find channel cards
        cards = soup.select('.peer-item, .channel-card, [data-peer-id], .lm-list-group-item, .card')

        for card in cards:
            try:
                # Find link
                link = card.select_one('a[href*="t.me/"], a[href*="tgstat.ru/channel/"], a[href*="tgstat.ru/chat/"]')
                if not link:
                    continue

                href = link.get('href', '')
                username = self._extract_username(href)
                if not username:
                    continue

                # Title
                title_elem = card.select_one('.peer-title, .channel-name, h5, h4, h3, .font-weight-bold')
                title = title_elem.get_text(strip=True) if title_elem else username

                # Description
                desc_elem = card.select_one('.peer-description, .text-muted, .small')
                description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""

                # Subscribers
                subs_elem = card.select_one('.peer-subscribers, .subscribers-count, [class*="subscriber"]')
                subscribers = self._parse_subscribers(subs_elem)

                # Detect type
                is_chat = '/chat/' in href or 'чат' in str(card).lower()

                results.append(FoundChannel(
                    username=username,
                    title=title if title else username,
                    url=f"https://t.me/{username}",
                    description=description,
                    subscribers=subscribers,
                    channel_type='chat' if is_chat else 'channel',
                    source='tgstat_browser',
                ))

            except Exception as e:
                logger.debug(f"Parse error: {e}")

        return results

    def _extract_username(self, href: str) -> Optional[str]:
        """Extract username from URL."""
        patterns = [
            r't\.me/([a-zA-Z0-9_]{3,32})',
            r'tgstat\.ru/channel/@?([a-zA-Z0-9_]{3,32})',
            r'tgstat\.ru/chat/@?([a-zA-Z0-9_]{3,32})',
        ]
        for pattern in patterns:
            match = re.search(pattern, href)
            if match:
                name = match.group(1)
                # Filter service pages
                if name not in ['search', 'channels', 'chats', 'rating', 'ru', 'en', 'login']:
                    return name
        return None

    def _parse_subscribers(self, elem) -> int:
        """Parse subscriber count."""
        if not elem:
            return 0

        text = elem.get_text(strip=True).lower().replace(' ', '').replace(',', '.')

        multipliers = {'k': 1000, 'к': 1000, 'm': 1000000, 'м': 1000000, 'тыс': 1000}

        for suffix, mult in multipliers.items():
            if suffix in text:
                try:
                    num = re.search(r'[\d.]+', text)
                    if num:
                        return int(float(num.group()) * mult)
                except:
                    pass

        try:
            nums = re.findall(r'\d+', text)
            if nums:
                return int(nums[0])
        except:
            pass

        return 0


class ChannelFinder:
    """Unified channel finder with browser support."""

    def __init__(
        self,
        aggression_level: str = "medium",
        use_browser: bool = False,
        headless: bool = True,
    ):
        self.anti_detection = AntiDetection(aggression_level)
        self.use_browser = use_browser
        self.browser = None

        if use_browser and SELENIUM_AVAILABLE:
            self.browser = BrowserFinder(self.anti_detection, headless)

        logger.info(f"ChannelFinder initialized: browser={use_browser}")

    def search(
        self,
        query: str,
        limit: int = 50,
        channel_type: str = "all",
    ) -> List[FoundChannel]:
        """Search for channels."""
        if self.browser:
            return self.browser.search(query, limit, channel_type)

        logger.warning("Browser not available")
        return []

    def search_chats(self, query: str, limit: int = 50) -> List[FoundChannel]:
        """Search only chats/groups."""
        return self.search(query, limit, channel_type='chat')

    def search_channels(self, query: str, limit: int = 50) -> List[FoundChannel]:
        """Search only channels."""
        return self.search(query, limit, channel_type='channel')
