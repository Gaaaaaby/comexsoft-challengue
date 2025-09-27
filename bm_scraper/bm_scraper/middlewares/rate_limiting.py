import time
import random


class RateLimitingMiddleware:
    def __init__(self, crawler):
        self.crawler = crawler
        self.download_delay = crawler.settings.getfloat('DOWNLOAD_DELAY', 1.0)
        self.randomize_delay = crawler.settings.getbool('RANDOMIZE_DOWNLOAD_DELAY', True)
        self.max_delay = crawler.settings.getfloat('RANDOMIZE_DOWNLOAD_DELAY_MAX', 2.0)
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_request(self, request, spider):
        if self.randomize_delay:
            delay = random.uniform(self.download_delay, self.max_delay)
        else:
            delay = self.download_delay
            
        time.sleep(delay)
        return None


class UserAgentRotationMiddleware:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
        return None


class EthicalScrapingMiddleware:
    def __init__(self, crawler):
        self.crawler = crawler
        self.robots_obey = crawler.settings.getbool('ROBOTSTXT_OBEY', True)
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_request(self, request, spider):
        request.headers['X-Scraper-Name'] = 'BM-Scraper'
        request.headers['X-Scraper-Version'] = '1.0'
        request.headers['X-Scraper-Purpose'] = 'Price-Monitoring'
        
        return None
