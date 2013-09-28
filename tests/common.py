# coding: utf-8
'''
Created on 2013-8-26

@author: flong
'''
import urllib2
import sys
import urllib
import json
import httplib
import urlparse



TEST_MODE=1
HOST = '172.16.2.186'
MONGO_PORT=27017
WAIT_MONGODB=2
'''
TEST_MODE=1 unittest2 mode ,use urllib2
TEST_MODE=0 django_test mode, use django.test.client
'''

URL_APPEND_DOMAIN = ["v5kanshu.com", "55yule.com", "game.dolphin.com"]

COMMON_FIELDS = ["sid", "order", "fixed", "content_id","source",
                    "title","default_image","corner_image","promotion_image","size","url"]

CONTENT_FIELDS_MAPPING = {
                          3:COMMON_FIELDS+["pattern","tags"],
                          4:COMMON_FIELDS+["description","pattern","tags"],
                          5:COMMON_FIELDS+["package_name"],
                          }
DEFAULT_DPI = 240
DEFAULT_WIDTH = 480
MIN_DPI = 160

LAYOUT_FIELDS=["card_width","card_high", "card_space", "load_more",
                                    "orientation", "row_count", "col_count","screens",
                                    "content_title","loading_text","refresh_text",
                                    "refresh_loading_text","refresh_failed_text",
                                    "retry_text","check_network_text",
                                    "search_url","load_internal","t"]

collection_mapping = {
            "novel":("novel_category", "novel", "novel_chapter"),
            "video":("video_category", "video", "video_chapter"),
        }
TYPE=['novel','video']
CONTENT_FIELDS=["category_name","order","image","category_id","url"]
OrderByFields = ["updatetime", "visitors", "completed"]

common_page_fields = ["order", "content_id","last_chapter", "url","chapters",
                    "title","image","visitors","update_state", "category_id","description", "category_name"]

content_page_fields = {
                          u"novel":common_page_fields+["url", "description", "author", "words", "updatetime"],
                          u"video":common_page_fields+["promotion_text", "score","actors", "directors","related_from_fangying",
                                                       "area", "sub_categories","release_time","tags","source", "related_videos"],
                          }



#CHAPTER_FIELDS={
#                'novel':["index","title"],
#                'video':["index","title","url"],
#                }
source_category_mapping = {
                           1:["youku", "iqiyi", "dudou", "sohu", "leshi"],
                           2:["iqiyi","sohu","youku","dudou","leshi"],
                           3:["sohu", "iqiyi","youku","leshi"],
                           }
source_category={
                 'movie':1,
                 'tv':2,
                 'show':3
                 }
PRIVATE_SOURCE_CATEGORY_MAPPING = {
                           1:["qvod",],
                           2:["qvod",],
                           3:["qvod",],
                           # remove "thunder", "bdyy"
                           }

PIRATE_CATEGORY = [1, ]

authorized_sources = ["cm", "unicom", "ct"]
unauthorized_sources = ["baidu", "yicha", "sousou"]
default_sources=['cm','luoqiu']
OTHER = 'other_condition'
OPERATORS = ['46000', '46001', '46002', '46003']
SOURCE_OPERATOR={
                 '46000':'cm',
                 '46001':'unicom',
                 '46002':'cm',
                 '46003':'ct',
                 }

TYPE_MAPPING={
              'novel':'novels',
              'video':'videos'
              }
common_update_fields = ["content_id","last_chapter", "chapters",]

content_update_fields = {    
                          u"novel":set(common_update_fields+["updatetime","update_state"]),    
                          u"video":set(common_update_fields),    
                          }

CHAPTER_FIELDS={
                'novel':["index","title","order"],
                'video':["index","title","url","order"],
                }
CHAPTER_FIELDS_PRIVATE={
                'novel':["index","title"],
                'video':["index","title","url"],
                }


source_category={
                 'movie':1,
                 'tv':2,
                 'show':3
                 }



common_hotwords_fields = ["title", "url", "order", "color"]
content_hotwords_fields = {
                          u"novel":common_hotwords_fields+["hotword_type"],
                          u"video":common_hotwords_fields,
                          }
HOT_WORD_TYPES = ['hot_search_word','hot_tag_word','hot_title_word','hot_author_word','hot_male_word','hot_female_word']
LIST_TYPE=['ranking_all','ranking_completed','show_hottest','movie_hottest','tv_hottest']
VERSION_TYPES=['tpls','cnts','cards']
   
   

def float_truncate(n, prec=2):
    if not isinstance(n, float):
        return n
    return float("%.2f"%n)
            
            
            
            

def url_modify(url, args):
    new_url=''
    try:
        url_parts = list(urlparse.urlparse(url))
        if url_parts[1] not in URL_APPEND_DOMAIN:
            return url
        query = dict(urlparse.parse_qsl(url_parts[5]))
        query.update({
                        "pn":args["pn"],
                        "v":args["vn"],
                        "s":args["src"],
                        "op":args["op"],
                    })
        url_parts[5] = urllib.urlencode(query)
        new_url = urlparse.urlunparse(url_parts)
    except:
        print'parse url failed: %s' %url
    return new_url


def sendRequest(api_url,params,type=1):
    if TEST_MODE and type==1:
        return sendRequesturllib2(api_url,params)
    elif TEST_MODE and type==0:
        return sendRequestHttplib(api_url,params)
    else:
        return sendRequestClient(api_url,params)
            
            
        

def sendRequesturllib2(api_url,params):
    rt={
        'http_status':None,
        'data':{}
        }
    data=urllib.urlencode(params)
    full_url=api_url+'?'+data
    try:
        req=urllib2.Request(full_url)
        print req.get_full_url()
        response=urllib2.urlopen(req)
        content=response.read()
        response.close()
        rt['http_status']=200
        rt['data']=json.loads(content, encoding='utf-8')
    except urllib2.HTTPError,e:
        rt['http_status']=e.code
    return rt
    
def sendRequestClient(api_url,params):
    rt={
        'http_status':None,
        'data':{}
        }
    data=urllib.urlencode(params)
    full_url=api_url+'?'+data
    c=Client()
    response=c.get(full_url)
    if response.status_code==200:
        rt['http_status']=response.status_code
        rt['data']=json.loads(response.content, encoding='utf-8')
    elif response.status_code==302:
        rt['http_status']=response.status_code
        rt['data']['url']=response.__getitem__('Location')
    else:
        rt['http_status']=response.status_code
    return rt

def sendRequestHttplib(api_url,params):
    rt={
        'http_status':None,
        'data':{}
        }
    
    data = urllib.urlencode(params)
    full_url = api_url + '?' + data
    try:
        conn = httplib.HTTPConnection(HOST)  
        conn.request('GET', full_url)
        response=conn.getresponse()  
        rt_url=response.getheader('Location', '')
        rt['http_status']=response.status
        if rt['http_status']==302:
            rt['data'].update({'url':rt_url})
            print rt['data']['url']
        elif rt['http_status']==200:
            content = response.read()
            result = json.loads(content, encoding='utf-8')
            rt['data']=result
        response.close()
       
    except urllib2.HTTPError, e:
        rt['http_status']=e.code
    return rt
    
   
    
    