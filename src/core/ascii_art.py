from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from . import tools
from urllib.parse import quote


class AsciiArt:
    def __init__(self, source: str, tag: str, element: str, url: str, attribs: dict):
        self.source = source
        self.target = source
        self.tag = tag
        self.element = element
        self.url = url
        self.attribs = attribs
        self.texts = tools.getTags(self.source, self.tag)
        self.options = None
        self.driver = None
        self.fails = {}
        if isinstance(self.texts, dict):
            for key in self.texts:
                success, text = self.fetch(self.texts[key])
                if success:
                    ind = self.target.find(key)
                    while ind >= 0:
                        n_ind = max(self.target.rfind('\n', 0, ind), 0)
                        text = text.replace('\n', '\n' + (' '*(ind - n_ind)))
                        self.target = self.target.replace(key, text, 1)
                        ind = self.target.find(key)
                else:
                    self.fails[key] = text

    def fetch(self, dic: dict):
        try:
            if self.options is None:
                self.options = webdriver.ChromeOptions()
                self.options.add_argument('--headless')
                self.options.page_load_strategy = 'none'
            if self.driver is None:
                self.driver = Chrome(options=self.options)
            else:
                self.driver.back()
            self.driver.implicitly_wait(5)
            url = self.url.format(**{k: quote(dic.get(k, v)) for k, v in self.attribs.items()})
            self.driver.get(url)
            content = self.driver.find_element(By.CSS_SELECTOR, self.element)
            return True, content.text
        except Exception as e:
            return False, 'Could not fetch the ASCII art; more info: %s' % str(e)


class taag(AsciiArt):
    def __init__(self, source: str):
        super().__init__(source=source, tag='taag', element='pre[id="taag_output_text"',
                         url='https://patorjk.com/software/taag/#p=display&h={width}&v={height}&f={font}&t={text}',
                         attribs={'width': '0', 'height': '0', 'font': 'Graffiti', 'text': 'bornalgo'})
