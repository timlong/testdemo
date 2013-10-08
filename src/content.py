#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# Created On Jan 14, 2012
# @Author : Jun Wang
# Email: jwang@bainainfo.com
import logging
import pymongo
from dolphinop.db import cursor_to_array

logger = logging.getLogger('dolphinop.db')

_db = None

DISPLAY_FIELDS = {
        '_id': 0,
        'packages': 0,
        'sources': 0,
        'updated': 0
    }

collection_mapping = {
        "novel": ("novel_category", "novel", "novel_chapter"),
        "video": ("video_category", "video", "video_chapter"),
    }


def _filter_highest_priority(ret):
    try:
        highest_priority = int(max(list(set([s["_rule"]["priority"] for s in ret]))))    # distinct the priority list ,and then get the max
        result = []
        for s in ret:
            if s["_rule"]["priority"] == highest_priority:
                result.append(s)
        return result
    except Exception:
        return ret


def get_content_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.content.find(cond, fields=fields)
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)


def get_page_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.page.find(cond, fields=fields)
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)


def get_categorys(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    collection_name = collection_mapping[content_type][0]
    colls = _db[collection_name].find({}, fields)
    ret = cursor_to_array(colls)
    return ret


def get_category_content(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"category_id": cond["category_id"]}
    if content_type == "video":
        condition["related_from_fangying"] = {"$ne":[], "$exists":True}
    elif content_type == "novel":
        condition["source"] = "baidu"
    if cond['orderby'] == "completed":
        condition["update_state"] = True
        cond['orderby'] = "visitors"
    collection_name = collection_mapping[content_type][1]
    colls = _db[collection_name].find(condition, skip=cond['start'],
                                      limit=cond['limit'], sort=[(cond['orderby'], pymongo.DESCENDING)],
                                      fields=fields)
    ret = cursor_to_array(colls)
    logger.debug(ret)
    return ret


def get_contents(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    collection_name = collection_mapping[content_type][1]
    ret = _db[collection_name].find(cond,fields=fields)
    return  cursor_to_array(ret)


def get_content_detail(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"content_id": cond["content_id"]}
    collection_name = collection_mapping[content_type][1]
    ret = _db[collection_name].find_one(condition, fields=fields)
    return [ret] if ret else []


def get_novel_chapters(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"content_id": cond["content_id"]}
    collection_name = collection_mapping[content_type][2]
    ret = _db[collection_name].find_one(condition, fields={"_id": 0, "charpters": 1, "items": 1})
    if ret:
        return ret.get("charpters") or ret.get("items")
    else:
        return []


def get_video_chapters(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"content_id": cond["content_id"]}
    collection_name = collection_mapping[content_type][2]
    ret = _db[collection_name].find(condition, fields={"_id": 0, "source": 1, "items": 1, "category_id": 1})

    return cursor_to_array(ret)


def get_chapter_detail(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"content_id": cond["content_id"]}
    collection_name = collection_mapping[content_type][2]
    ret = _db[collection_name].find_one(condition, fields=fields)
    return ret.get("charpters", []) if ret else []


def get_raw_content(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    content_type = cond.pop('type')
    condition = {"content_id": cond["content_id"]}
    ret = _db[content_type].find(condition, fields=fields)
    return cursor_to_array(ret)

def get_authorized_novels():
    return [d.get("content_id", "") for d in _db.authorized_novels.find()]


def get_content_version(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    ret = _db.content_version.find(cond, fields={'_id': 0, '_meta.current_version': 1}).distinct("_meta.current_version")
    ret = max(ret) if ret else None
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)


def get_content_conf_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.content_conf.find(cond, fields=fields)
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)


def get_hotwords_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.hotwords.find(cond, fields=fields, limit=100)    # limit the default count of results for multi types
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)


def get_screen_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.content_screen.find(cond, fields=fields, sort=[('_meta.sid', pymongo.ASCENDING)])
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)

def get_subjects_data(cond, fields=DISPLAY_FIELDS, filter_highest_priority=False):
    colls = _db.subject.find(cond, fields=fields) 
    ret = cursor_to_array(colls)
    if not filter_highest_priority:
        return ret
    return _filter_highest_priority(ret)

def get_subjectvideo_data():
    pass
