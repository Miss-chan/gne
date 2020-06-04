#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:chenlincui
import re
from ..utils import config
from lxml.html import HtmlElement, tostring
from ..defaults import REPRINT_PATTERN


class ReprintExtractor:
    def __init__(self):
        self.reprint_pattern = REPRINT_PATTERN

    def extractor(self, element: HtmlElement, reprint_xpath=''):
        reprint_xpath = reprint_xpath or config.get('reprint', {}).get('xpath')
        if reprint_xpath:
            reprint = ''.join(element.xpath(reprint_xpath))
            return reprint
        text = tostring(element.xpath('//body')[0], True, True, encoding='utf-8').decode('utf-8')
        for pattern in self.reprint_pattern:
            reprint_obj = re.search(pattern, text)
            if reprint_obj:
                return reprint_obj.group(2)
        return ''
