'''
Created on 2013-6-18

@author: flong
'''
import unittest2
from pymongo  import Connection
import datetime
import json
import time
from common import *



def convertdata(item):
        #size='(100,100)'
        ret = {
            "_key" : {
                      "sid":item['sid'],
                      "cid":item['cid'],
                      "cvn":0,
                    },
            "_sync_key" : {
                    "platform" : "AndroidCN",
                },
            "_rule" : {
                    "priority" :1,
                    "sources" : {
                        "exclude" : [],
                        "include" : None,
                     },
                    "locale" : {
                        "exclude" : [],
                        "include" : None,
                     },
                    "locations" : {
                        "exclude" : [],
                        "include" : None,
                     },
                    "max_version" : 200,
                    "min_version" : 100,
                    "packages" : [
                        "com.dolphin.timlong.test"
                     ],
                    "start_time" : datetime.datetime(2013, 5, 18, 12, 48, 39, 37130),
                    "end_time" : datetime.datetime(2113, 5, 18, 12, 48, 39, 37130),
                    "operators" : [],
                },
            "_meta":{
                    "tags" :{
                        "corner":{
                                 "des" : item.get('promotion_text2'),
                                 "direction" : 1
                                },
                             "bottom":{
                                 "des" : item.get('promotion_text1'),
                                 }
                    },
                    "promotion_image": None,
                    "description" : 'timlong.test',

                    "last_modified" : 1371456313,
                    "size" : json.loads('['+item['size'][1:-1]+']'),
                    "content_id": item['content_id'],
                    "title" : 'timlong.test.title',
                    "url" : 'http://r2.mo.baidu.com/novel/fetch.php?platform=android&tab=search&ua=I4DJ8YuLDt_quLMENpxhjk4pXPIVlxjhqkXT8ougXi4ZuXiYzusIigIrwitSC&cuid=lu28a_aIvi0qa',
                    "pattern": 'timlong.pattern',
                    "default_image": "http: \/\/b.hiphotos.bdimg.com\/album\/w%3D2048%3Bq%3D90\/sign=408da089b21bb0518f24b4280242e1c5\/55e736d12f2eb93872aad659d4628535e4dd6f52.jpg",
                    "fixed" : 0,
                    "order" : item['order'],
                    "image" : 'http://172.16.255.246/resources/pic/content/xiaoshuo_2.png',
                }
            }
        if not item.get('promotion_text2'):
            del ret["_meta"]["tags"]["corner"]
        if not item.get('promotion_text1'):
            del ret["_meta"]["tags"]["bottom"]
        if item.get('screen_data'):
            ret['_meta']['more_url']='timlong.test.more_url'
            ret['_meta']['stid']= item['_meta']['stid']
            ret['_meta']['content']=item['_meta']['content']
            ret['_meta']['more_text']='timlong.test.more_text'
            ret['_meta']['sid']=item['_meta']['sid']
        return ret

class CardRefreshServiceTest(unittest2.TestCase):
    _db = None
    _conn=None
    _card_api='http://'+HOST+'/content/1/card/refresh.json'
    _loadmore_api='http://'+HOST+'/content/1/card/loadmore.json'
    _cid=4

    def setUp(self):
        self._conn=Connection(HOST,MONGO_PORT)
        self._db=self._conn.dolphinop
        cond = {
            #'_key.cid':self._cid,
            '_meta.description':'timlong.test',
           }
        self._db.content.remove(cond)
        self._db.content_screen.remove(cond)
        time.sleep(WAIT_MONGODB)



    def tearDown(self):
        cond = {
            #'_key.cid':self._cid,
            '_meta.description':'timlong.test',
           }
        self._db.content.remove(cond)
        self._db.content_screen.remove(cond)
        time.sleep(WAIT_MONGODB)
        self._conn.close()
    
    def test_01_api_cardrefresh_normal(self):
        '''
        card_refresh normal test
        '''
        item_insert=[]
        item={}
        p=[]
        sids=[]
        max_count=10
        for i in range(1,max_count+1):
            sids.append(i)
            
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                ret= convertdata(item)
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
       
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        for item in p:
            sid=str(item[0])
            start=item[1]
            limit=item[2]
            self.assertEqual(len(result['data'][sid]), limit, 'sid :%s size is not :%s,but:%s' %(sid,limit,len(result['data'][sid])))
            w=0
            while w < len(result['data'][sid]):
                #print result['data'][sid][w]['content_id']
                expected_order=(w+start)%(max_count)+1
                self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+sid+"-"+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+sid+"-"+str(expected_order),result['data'][sid][w]['content_id']))
                w+=1
       
    def test_02_api_cardrefresh_order(self):
        '''
         card_refresh result should be in order
        '''
        item_insert=[]
        item={}
        for i in range(1,21):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-'+str(i)
            ret= convertdata(item)
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        sid=1
        start=1
        limit=10
        p=[[sid,start,limit]]
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        sid=str(sid)
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data'][sid]), limit, 'sid 1 size is not 10,but:%s' %(len(result['data'][sid])))
        w=0
        while w < len(result['data'][sid]):
            #print result['data'][sid][w]['content_id']
            self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+str(w+start+1), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+str(w+start+1),result['data'][sid][w]['content_id']))
            w+=1
       
    def test_03_api_cardrefresh_mod(self):
        '''
         card_refresh start param should be mod by data lenth
        '''
        item_insert=[]
        item={}
        max_count=10
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-'+str(i)
            ret= convertdata(item)
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        sid=1
        start=12
        limit=20
        p=[[sid,start,limit]]
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        sid=str(sid)
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data'][sid]), min(limit,max_count), 'sid 1 size is not %s,but:%s' %( min(limit,max_count),len(result['data'][sid])))
        w=0
        while w < len(result['data'][sid]):
            #print result['data'][sid][w]['content_id']
            expected_order=(w+start)%(len(result['data'][sid]))+1
            self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+str(expected_order),result['data'][sid][w]['content_id']))
            w+=1
       
           
       
    
    
    def test_05_api_cardrefresh_maxcardnum(self):
        '''
         card_refresh maxcarnum limitaion
        '''
        item_insert=[]
        item={}
        max_count=50
        max_card_num=20
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-'+str(i)
            ret= convertdata(item)
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        sid=1
        start=0
        limit=25
        p1=[sid,start,limit]
        p=[p1]
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        sid=str(sid)
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data'][sid]), min(limit,max_card_num), 'sid 1 size is not %s,but:%s' %( min(limit,max_count),len(result['data'][sid])))
     

    

    def test_07_api_cardrefresh_rule_package(self):
        '''
        card_refresh normal test
        '''
        item_insert=[]
        item={}
        p=[]
        sids=[]
        max_count=10
        for i in range(1,max_count+1):
            sids.append(i)
            
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                ret= convertdata(item)
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
       
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        for item in p:
            sid=str(item[0])
            start=item[1]
            limit=item[2]
            self.assertEqual(len(result['data'][sid]), limit, 'sid 1 size is not 10,but:%s' %(len(result['data'][sid])))
            w=0
            while w < len(result['data'][sid]):
                #print result['data'][sid][w]['content_id']
                expected_order=(w+start)%(max_count)+1
                self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+sid+"-"+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+sid+"-"+str(expected_order),result['data'][sid][w]['content_id']))
                w+=1
      
        
        #re-insert mongo data for another package_name    
        cond = {
            #'_key.cid':self._cid,
            '_meta.description':'timlong.test',
           }
        self._db.content.remove(cond)
        time.sleep(WAIT_MONGODB)
        
        item_insert=[]
        item={}
        p=[]
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                ret= convertdata(item)
                ret['_rule']['packages']=[]
                ret['_rule']['packages'].append('com.dolphin.timlong.test.anthoer')
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        rt=sendRequest(self._card_api,values)
        self.assertEqual(rt['http_status'],304,'http_status is not 304,but :%s' %(rt['http_status']))
      
            
    def test_08_api_cardrefresh_rule_sources_include(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['sources']['include']=[]
            ret['_rule']['sources']['include'].append(str(i))
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        
        for i in range(1,max_count+1):
            values={
                'pn':'com.dolphin.timlong.test',
                'src':str(i),
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':'[[1,1,10]]',
                'cid':self._cid
                 }
            rt=sendRequest(self._card_api,values)
            result=rt['data']
            self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
            print result
            self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
            self.assertEqual(len(result['data']['1']), 1, 'sid 1 size is not 1,but:%s' %(len(result['data']['1'])))
            w=0
            while w < len(result['data']['1']):
                self.assertEqual(result['data']['1'][w]['content_id'], 'timlong-1-'+str(i), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-1-'+str(i),result['data']['1'][w]['content_id']))
                w+=1
           
    def test_09_api_cardrefresh_rule_sources_exclude(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['sources']['exclude']=[]
            ret['_rule']['sources']['exclude'].append(str(i))
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        
        for i in range(1,max_count+1):
            values={
                'pn':'com.dolphin.timlong.test',
                'src':str(i),
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':'[[1,1,10]]',
                'cid':self._cid
                 }
            rt=sendRequest(self._card_api,values)
            result=rt['data']
            self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
            print result
            self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
            self.assertEqual(len(result['data']['1']), max_count-1, 'sid 1 size is not 9,but:%s' %(len(result['data']['1'])))
            w=0
            while w < len(result['data']['1']):
                self.assertNotEqual(result['data']['1'][w]['content_id'], 'timlong-1-'+str(i), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-1-'+str(i),result['data']['1'][w]['content_id']))
                w+=1
           
                
    def test_10_api_cardrefresh_rule_last_modified(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        now_t=int(time.time())
        tomorrow_t=int(now_t+60*5)
        yesterday_t=int(now_t-60*5)
        tomorrow_contents=[]
        yesterday_contents=[]
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            if i%2==0:
                ret['_meta']['last_modified']=yesterday_t
                yesterday_contents.append( item['content_id'])
            else:
                ret['_meta']['last_modified']=tomorrow_t
                tomorrow_contents.append( item['content_id'])
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        values={
            'pn':'com.dolphin.timlong.test',
            'src':'ofw',
            'vn':102,
            'op':02,
            'mt':now_t,
            'p':'[[1,1,10]]',
            'cid':self._cid
                }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data']['1']), len(tomorrow_contents), 'sid 1 size is not 9,but:%s' %(len(result['data']['1'])))
        w=0
        while w < len(result['data']['1']):
            self.assertTrue(result['data']['1'][w]['content_id'] in tomorrow_contents, 'got content not in tomorrow_contents:%s' %(result['data']['1'][w]['content_id']))
            w+=1
      
    def test_11_api_cardrefresh_rule_version(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        min_version=250
        max_version=300
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['min_version']=min_version
            ret['_rule']['max_version']=max_version
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        values={
            'pn':'com.dolphin.timlong.test',
            'src':'ofw',
            'vn':min_version+10,
            'op':02,
            'mt':1236000,
            'p':'[[1,1,10]]',
            'cid':self._cid
                }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data']['1']), max_count, 'sid 1 size is not 9,but:%s' %(len(result['data']['1'])))
      
                
        values['vn']=max_version+1
        rt=sendRequest(self._card_api,values)
        self.assertEqual(rt['http_status'],304,'http_status is not 304,but :%s' %(rt['http_status']))
       
    def test_12_api_cardrefresh_rule_startendtime(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        now_t=datetime.datetime.now()
        tomorrow_t=now_t+datetime.timedelta(1)
        yesterday_t=now_t+datetime.timedelta(-1)
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['start_time']=yesterday_t
            ret['_rule']['end_time']=tomorrow_t
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        values={
            'pn':'com.dolphin.timlong.test',
            'src':'ofw',
            'vn':'102',
            'op':02,
            'mt':1236000,
            'p':'[[1,1,10]]',
            'cid':self._cid
                }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data']['1']), max_count, 'sid 1 size is not 9,but:%s' %(len(result['data']['1'])))
    
    
        cond = {
            '_meta.description':'timlong.test',
           }
        self._db.content.remove(cond)  
        item_insert=[]
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['start_time']=tomorrow_t
            ret['_rule']['end_time']=tomorrow_t+datetime.timedelta(1)
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        rt=sendRequest(self._card_api,values)
        self.assertEqual(rt['http_status'],304,'http_status is not 304,but :%s' %(rt['http_status']))
      
            
    def test_13_api_cardrefresh_rule_operators(self):
        '''
        card_refresh rule test
        '''
        item_insert=[]
        item={}
        max_count=10
        OPERATORS = ['46000', '46001', '46002', '46003']
        operators_4600=[]
        operators_4601=[]
        for i in range(1,max_count+1):
            item['cid']=self._cid
            item['size']='(100,100)'
            item['sid']=1
            item['order']=i
            item['content_id']='timlong-1-'+str(i)
            ret= convertdata(item)
            ret['_rule']['operators']=[]
            target_operator=OPERATORS[i%len(OPERATORS)]
            ret['_rule']['operators'].append(target_operator)
            if target_operator=='46000':
                operators_4600.append(item['content_id'])
            elif target_operator=='46001':
                operators_4601.append(item['content_id'])
            item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        sid=1
        start=1
        limit=10
        p=[[sid,start,limit]]
        values={
            'pn':'com.dolphin.timlong.test',
            'src':'ofw',
            'vn':'102',
            'op':46000,
            'mt':1236000,
            'p':p,
            'cid':self._cid
                }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data']['1']), len(operators_4600), 'sid 1 size is not 1,but:%s' %(len(result['data']['1'])))
        w=0
        while w < len(result['data'][str(sid)]):
            #print result['data'][sid][w]['content_id']
            self.assertTrue(result['data'][str(sid)][w]['content_id'] in operators_4600, 'got content not in operators_4600:%s' %(result['data'][str(sid)][w]['content_id']))
            w+=1
       
       
        values={
            'pn':'com.dolphin.timlong.test',
            'src':'ofw',
            'vn':'102',
            'op':11,
            'mt':1236000,
            'p':p,
            'cid':self._cid
                }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        self.assertEqual(len(result['data']['1']), len(operators_4601), 'sid 1 size is not 1,but:%s' %(len(result['data']['1'])))
        w=0
        while w < len(result['data'][str(sid)]):
            #print result['data'][sid][w]['content_id']
            self.assertTrue(result['data'][str(sid)][w]['content_id'] in operators_4601, 'got content not in operators_4601:%s' %(result['data'][str(sid)][w]['content_id']))
            w+=1
        
            
    def test_14_api_cardrefresh_screendata(self):
        '''
        card_refresh normal test
        '''
        item_insert=[]
        item={}
        p=[]
        sids=[]
        max_count=10
        for i in range(1,max_count+1):
            sids.append(i)
            
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                item['screen_data']=True
                item['_meta']={}
                item['_meta']['stid']= i
                item['_meta']['content']=self._cid
                item['_meta']['sid']=sid
                ret= convertdata(item)
                ret['_key']['cvn']=1
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        self._db.content_screen.insert(item_insert)
        time.sleep(WAIT_MONGODB)
       
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid,
                'cvn':1
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        for item in p:
            sid=str(item[0])
            start=item[1]
            limit=item[2]
            self.assertEqual(len(result['data'][sid]), limit, 'sid :%s size is not :%s,but:%s' %(sid,limit,len(result['data'][sid])))
            self.assertEqual(result['screen_data'][sid]['sid'], int(sid), 'screen_data sid :%s  is not %s,but:%s' %(sid,sid,result['screen_data'][sid]['sid']))
            #http://172.16.9.31:9090/browse/CONTENT-11
            #self.assertEqual(result['screen_data'][sid]['stid'], max_count, 'screen_data sid :%s  is not %s,but:%s' %(sid,max_count,result['screen_data'][sid]['stid']))
            w=0
            while w < len(result['data'][sid]):
                #print result['data'][sid][w]['content_id']
                expected_order=(w+start)%(max_count)+1
                self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+sid+"-"+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+sid+"-"+str(expected_order),result['data'][sid][w]['content_id']))
                w+=1
        
    def test_15_api_cardrefresh_without_screendata(self):
        '''
        card_refresh normal test
        '''
        item_insert=[]
        item={}
        p=[]
        sids=[]
        max_count=10
        for i in range(1,max_count+1):
            sids.append(i)
            
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                item['screen_data']=True
                item['_meta']={}
                item['_meta']['stid']= i
                item['_meta']['content']=self._cid
                item['_meta']['sid']=sid
                ret= convertdata(item)
                ret['_key']['cvn']=1
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        #self._db.content_screen.insert(item_insert)
        time.sleep(WAIT_MONGODB)
       
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid,
                'cvn':1
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        print result
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        for item in p:
            sid=str(item[0])
            start=item[1]
            limit=item[2]
            self.assertEqual(len(result['data'][sid]), limit, 'sid :%s size is not :%s,but:%s' %(sid,limit,len(result['data'][sid])))
            self.assertFalse(result.get('screen_data'), 'got screen_data :%s' %(result.get('screen_data')))
            w=0
            while w < len(result['data'][sid]):
                #print result['data'][sid][w]['content_id']
                expected_order=(w+start)%(max_count)+1
                self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+sid+"-"+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+sid+"-"+str(expected_order),result['data'][sid][w]['content_id']))
                w+=1
        
  

    
    def test_17_api_cardrefresh_priority_onlymax(self):
        '''
        card_refresh only return the highest priority item
        '''
        item_insert=[]
        item={}
        p=[]
        sids=[]
        max_count=10
        for i in range(1,max_count+1):
            sids.append(i)
            
        for sid in sids:
            p.append([sid,sid,sid])
            for i in range(1,max_count+1):
                item['cid']=self._cid
                item['size']='(100,100)'
                item['sid']=sid
                item['order']=i
                item['content_id']='timlong-'+str(sid)+"-"+str(i)
                ret= convertdata(item)
                ret['_rule']['priority']=i
                item_insert.append(ret)
        self._db.content.insert(item_insert)
        time.sleep(WAIT_MONGODB)
        values={
                'pn':'com.dolphin.timlong.test',
                'src':'ofw',
                'vn':102,
                'op':02,
                'mt':"1236000",
                'p':p,
                'cid':self._cid
                 }
        rt=sendRequest(self._card_api,values)
        result=rt['data']
        self.assertEqual(rt['http_status'],200,'http_status is not 200,but :%s' %(rt['http_status']))
        self.assertEqual(result.get('msg'), 'OK', 'msg is not OK')
        for item in p:
            sid=str(item[0])
            self.assertEqual(len(result['data'][sid]), 1, 'sid :%s size is not 1,but:%s' %(sid,len(result['data'][sid])))
            w=0
            while w < len(result['data'][sid]):
                #print result['data'][sid][w]['content_id']
                expected_order=max_count
                self.assertEqual(result['data'][sid][w]['content_id'], 'timlong-'+sid+"-"+str(expected_order), 'content_id is wrong ,expect:%s,but got:%s' %('timlong-'+sid+"-"+str(expected_order),result['data'][sid][w]['content_id']))
                w+=1
      
    
      
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDemo']
    #unittest.main()
    suite = unittest2.TestSuite()
    if len(sys.argv) == 1:
        suite = unittest2.TestLoader().loadTestsFromTestCase(CardRefreshServiceTest)
    else:
        for test_name in sys.argv[1:]:
            suite.addTest(CardRefreshServiceTest(test_name))

    unittest2.TextTestRunner(verbosity=2).run(suite)
