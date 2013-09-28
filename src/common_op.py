#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On June 25, 2013
# @Author : Chen Qi
# Email: qchen@bainainfo.com

import logging
import json
import datetime
import time
#from decimal import Decimal

logger=logging.getLogger('dolphinop.service')

COMMON_FIELDS = {
    '_id': 0,
}

def float_truncate(n, prec=2):
    if not isinstance(n, float):
        return n
    return float("%.2f"%n)


def now():
    return datetime.datetime.now()

def now_t():
    return int(time.time())

def distinct_by_key(items, sort=True, cmp_func=None):
    dup_dict = {}
    for item in items:
        label = item['_key']
        dup_key = json.dumps(label)
        if dup_key not in dup_dict or dup_dict[dup_key].get('_priority') < item.get('_priority'):
            dup_dict[dup_key] = item
    keys = dup_dict.keys()
    if sort:
        keys.sort(cmp=cmp_func)
    result_section = []
    for label in keys:
        result_section.append(dup_dict[label])
    return result_section


def _or(*l):
    for v in l:
        if v is not None:
            return v
    return None


def default_normalize_result(res, required=None):
    ret = {}
    if required is None:
        return res
    for q in required:
        if res:
            ret[q] = _or(res.get(q),None)
    return ret


def normalize_result(res, required=None):
    ret = {}
    if required is None:
        return res
    for q in required:
        ret[q] = _or(res.get(q), res["_key"].get(q), res['_meta'].get(q), res['_meta_extend'].get(q) if '_meta_extend' in res else None)
    return ret


def _rule_parse(section, args, name):
    alternative_rule = section["_rule"].get(name)
    if not alternative_rule:
        return True
    if alternative_rule and alternative_rule.get("include") and args.get(name) is not None and args[name] not in alternative_rule["include"]:
        return False
    if alternative_rule and alternative_rule.get("exclude") and args.get(name) is not None and args[name]  in alternative_rule["exclude"]:
        return False
    return True

def rule_parse(section_infos, args, rules=[]):
    sections = []
    for section in section_infos:
        flag = True
        for rule_name in rules:
            if not _rule_parse(section, args, rule_name):
                flag = False
                break;
        if flag:
            sections.append(section)
    return sections


def get_rawdata(request, args, dbmodule, func_name, extend_cond_list=[],distinct=False,
                common_rule_parse=True,extend_cond_only=False,parser=None, parser_args=None):
    now_t = now()

    cond = {
            '_rule.packages': {'$in': [args['package_name']]},
            '_rule.sources.include': {'$in': [args['source'], None]},
            '_rule.sources.exclude': {'$ne': args['source']},
            '_meta.last_modified': {'$gt': args.get('t', 0)},
            '_rule.max_version': {'$gte': args['version']},
            '_rule.min_version': {'$lte': args['version']},
            '_rule.end_time': {'$gte': now_t},
            '_rule.start_time': {'$lte': now_t},
            '_rule.operators': {'$in': [args.get('operator','other_condition'), []]},
    }
    extend_cond = {}
    for item in extend_cond_list:
        extend_cond[item[0]] = item[1]
    if extend_cond_only:
        cond = extend_cond
    else:
        cond.update(extend_cond)
    logger.info(cond)
    section_infos = dbmodule.__getattribute__(func_name)(cond, fields=COMMON_FIELDS, filter_highest_priority=True)
    logger.debug(len(section_infos))
    if parser and callable(parser):
        section_infos = parser(section_infos, parser_args)
        logger.debug(section_infos)
    if not section_infos:
        return None
    if common_rule_parse:
        section_infos = rule_parse(section_infos, args, rules=["locales", "locations"])
    logger.debug(len(section_infos))
    if distinct:
        section_infos = distinct_by_key(section_infos, sort=True, cmp_func=None)
        logger.debug(len(section_infos))
    return section_infos
