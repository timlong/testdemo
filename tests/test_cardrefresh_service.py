'''
Created on 2013-6-18

@author: flong
'''
import unittest
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

class CardRefreshServiceTest(unittest.TestCase):
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
        print 'test_02_api_cardrefresh_order pass'
        pass
       
    def test_03_api_cardrefresh_mod(self):
        print 'test_03_api_cardrefresh_mod pass'
        pass
    
    def test_04_api_cardrefresh_maxcardnum(self):
        print 'test_04_api_cardrefresh_maxcardnum pass'
        pass
            
    def test_05_api_cardrefresh_rule_sources_include(self):
        print 'test_05_api_cardrefresh_rule_sources_include pass'
        pass
           
    def test_06_api_cardrefresh_rule_sources_exclude(self):
        print 'test_06_api_cardrefresh_rule_sources_exclude pass'
        pass
           
    def test_07_api_cardrefresh_rule_last_modified(self):
        print 'test_07_api_cardrefresh_rule_last_modified pass'
        pass

    def test_08_api_cardrefresh_rule_version(self):
        print 'test_08_api_cardrefresh_rule_version pass'
        pass
            
    def test_09_api_cardrefresh_screendata(self):
        print 'test_09_api_cardrefresh_screendata pass'
        pass
        
    def test_10_api_cardrefresh_without_screendata(self):
        print 'test_10_api_cardrefresh_without_screendata pass'
        pass
    
    def test_11_api_cardrefresh_priority_onlymax(self):
        print 'test_11_api_cardrefresh_priority_onlymax pass'
        pass
    
      
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDemo']
    #unittest.main()
    suite = unittest.TestSuite()
    if len(sys.argv) == 1:
        suite = unittest.TestLoader().loadTestsFromTestCase(CardRefreshServiceTest)
    else:
        for test_name in sys.argv[1:]:
            suite.addTest(CardRefreshServiceTest(test_name))
    unittest.TextTestRunner(verbosity=2).run(suite)
