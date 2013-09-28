#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import urlparse
import urllib
import logging
import json
import itertools
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from dolphinop.content.views import response_json, OTHER, OPERATORS
from dolphinop.content.utils import get_parameter_GET
from dolphinop.content.utils.common_op import normalize_result, get_rawdata
from dolphinop.content.errors import internal_server_error, resource_not_modified
from dolphinop.content.models import content

logger=logging.getLogger('dolphinop.service')

def get_common_params(request):
    package_name = get_parameter_GET(request, 'pn', alternative_name='pname')
    source = get_parameter_GET(request, 'src', default='ofw')
    version = get_parameter_GET(request, 'vn', default=0, convert_func=int)


    return {
            "package_name" : package_name,
            "source" : source,
            "version" : version,
            }

def _caculate_total_screens(result_section):
    l = []
    for r in result_section:
        if r["sid"] not in l:
            l.append(r["sid"])
    logger.debug(l)
    return len(l)

def _fixed_card(s):
    c = 0
    for item  in s:
        if item['fixed']:
            c += 1
    return c

URL_APPEND_DOMAIN = settings.URL_APPEND_DOMAIN

def _url_modify(item, args):
    if "url" not in item:
        return item
    try:           
        url_parts = list(urlparse.urlparse(item['url']))
        logger.debug(url_parts)
        if url_parts[1] not in URL_APPEND_DOMAIN:
            return item
        query = dict(urlparse.parse_qsl(url_parts[5]))
        query.update({
                        "pn":args["package_name"],
                        "v":args["version"],
                        "s":args["source"],
                        "op":args["operator"],
                    })
        url_parts[5] = urllib.urlencode(query)
        item["url"] = urlparse.urlunparse(url_parts)
    except:
        logger.exception('parse url failed: %s' % item['url'])
    return item



def _build_content(args, temp_result, item_callback=None):

    result_section = dict([ (k, list(g)) for k, g in itertools.groupby(sorted(temp_result, key=lambda x:x['sid']), key=lambda x: x['sid'])])
    for k, g in result_section.iteritems():
        # sort by order and reset order incr
        g  =  sorted(g, key=lambda x: x['order'])
        for i, t in enumerate(g):
            t['order'] = i + 1
        result_section[k] = g

    for sid, _ in result_section.iteritems():
        l = []
        logger.debug('ARGS:%s ,result_section: %s' % (args, result_section))
        length =  len(result_section[sid])
        count = min(args[sid]['limit'], length)
        w, p = 0, args[sid]['index']
        while w < count:
            index = p % length
            p += 1
            if args.get("reject_fixed") is True and result_section[sid][index]["fixed"]:
                continue
            l.append(result_section[sid][index])
            w += 1
        result_section[sid] = [item_callback(i, args) for i in l] if item_callback and callable(item_callback) else l

    return result_section

COMMON_FIELDS = ["sid", "order", "fixed", "content_id","source",
                    "title","default_image", "corner_image", "promotion_image","size","url"]

CONTENT_FIELDS_MAPPING = {
                          3:COMMON_FIELDS+["pattern","tags"],
                          4:COMMON_FIELDS+["description","pattern","tags"],
                          5:COMMON_FIELDS+["package_name"],
                          }
SCREEN_DATA_FIELDS = ['sid', 'stid', 'title', 'more_text', 'more_url']


MAX_CARD_NUM = 20
def _get_data(request, args):
    try:
        args["sids"] = list(set([ t[0] for t in args["p"]  ]))
        for sid, start, limit in args["p"]:
            args[sid] = {
                        "index":start,
                        "limit":min(limit, MAX_CARD_NUM),
                        }

        extend_cond = [('_key.cid',args['cid']),
                       ('_key.sid', {'$in': args["sids"]}),
                      ]

        screen_data = {}
        if args['cvn'] == 1:
            screen_data = get_rawdata(request, args, content, "get_screen_data", extend_cond_list=extend_cond)
            screen_data = [normalize_result(r, SCREEN_DATA_FIELDS) for r in (screen_data or []) ]
            screen_data = dict([ (k['sid'], k) for k in screen_data])

        extend_cond.append(('_key.cvn', args['cvn'] ))

#        if args.get('reject_fixed') is True:
#            extend_cond.append(('_meta.fixed',0))
        section_infos = get_rawdata(request, args, content, "get_content_data", extend_cond_list=extend_cond)
        if not section_infos:
            return resource_not_modified(request, 'page')
        content_data = [normalize_result(r, CONTENT_FIELDS_MAPPING.get(args['cid'])) for r in section_infos]
        content_data = _build_content(args, content_data, item_callback=_url_modify)
    except Exception,e:
        logger.error(e)
        return internal_server_error(request, e, sys.exc_info())
    return content_data, screen_data

@require_GET
def refresh(request):
    args = get_common_params(request)
    args['t'] = get_parameter_GET(request, 'mt', default=0, convert_func=int)#int(query.get('mt', 0))
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)#query.get('op', OTHER)
    args['p'] = get_parameter_GET(request, 'p', convert_func=json.loads)
    args['cid'] = get_parameter_GET(request, 'cid', convert_func=int)
    args['cvn'] = get_parameter_GET(request, 'cvn', convert_func=int, default=0)
    args['reject_fixed'] = True
    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['source'], args['version'], args['cid'],
              args['t'], args['p']):
        if isinstance(q, HttpResponse):
            return q

    result = _get_data(request, args)
    if isinstance(result, HttpResponse):
        return result
    else:
        ret = {
            "result":0,
            "msg":"OK",
            "data":result[0],
            "screen_data":result[1],
        }
        return response_json(ret)


MAX_SCREEN_NUM = 10
DEFAULT_LOADMORE_ARGSP = [[0,0,6]]
START_CARD_INDEX = 0
@require_GET
def loadmore(request):
    args = get_common_params(request)
    args['t'] = get_parameter_GET(request, 'mt', default=0, convert_func=int)#int(query.get('mt', 0))
    args['operator'] = get_parameter_GET(request, 'op', default=OTHER)#query.get('op', OTHER)
    args['p'] = get_parameter_GET(request, 'p', convert_func=json.loads)
    args['cid'] = get_parameter_GET(request, 'cid', convert_func=int)
    args['cvn'] =  get_parameter_GET(request, 'cvn', convert_func=int, default=0)

    if args['operator'] not in OPERATORS:
        args['operator'] = OTHER
    for q in (args['package_name'], args['source'], args['version'], args['cid'],
              args['t'], args['p'], args['cvn']):
        if isinstance(q, HttpResponse):
            return q

    try:
        start_screen_id, request_screen_num, per_screen_count  = tuple(args['p'])
        args['p'] = [ [ start_screen_id + i + 1, START_CARD_INDEX,  per_screen_count] for i in range(min(request_screen_num, MAX_SCREEN_NUM)) ]
    except Exception:
        args['p'] = DEFAULT_LOADMORE_ARGSP

    result = _get_data(request, args)
    if isinstance(result, HttpResponse):
        return result
    else:
        ret = {
            "result":0,
            "msg":"OK",
            "data":result[0],
            "screen_data":result[1],
        }
        return response_json(ret)



