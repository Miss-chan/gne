#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : run.py
# @Time    : 2020-6-1 16:40
# @Software: PyCharm
# @Author  : Taoz
# @contact : xie-hong-tao@qq.com
import difflib
import requests
from gne import GeneralNewsExtractor
from test_urls import urls

for url in urls:
    res = requests.get(url)
    html = res.content
    try:
        html = html.decode('gbk')
    except Exception:
        html = html.decode('utf8')

    extractor = GeneralNewsExtractor()
    result = extractor.extract(html, noise_node_list=['//div[@class="comment-list"]'])
    print(result)

# html = '<html lang="en"><head><meta charset="UTF-8">' \
#        '<title>贵州省设立“农民工维权岗” 为农民工讨薪提供“一站式”服务爱说</title>' \
#        '</head><body><div class="heading">' \
#        '<h1 class="title">爱说丨消费随笔②方便就是经</h1>' \
#         '<h2 class="title">爱说丨消费随笔②方便</h2>' \
#        '</div><table width="640" border="0" cellspacing="0" cellpadding="0">' \
#        '<tr><td height="70" align="center" valign="middle">' \
#        '<span class="articletitle_p22">爱说丨消费随笔②方便就是经济</span>' \
#         '<span class="articletitle_p22">爱说丨消费随笔②方便就是</span>'\
#        '</td></tr></table></body></html>'

