testdemo
========

API Test Demo

卡片数据
API路径
http://cn-cnt.dolphin-browser.com/content/1/card/data.json? cid=10001&pn=com.dolphin.browser.xf&src=channelId&vn=clientVersionCode&sid=[]&cvn=0
参数
加粗为必选，否则可选

Parameter   Format  Required    Default Description
cid String  Y       Content id
cvn int N   0   公共代码版本号
pn  string  Y       客户端包名
src string  Y       渠道名
vn  int Y       客户端版本号
locale  string  N   None    客户端系统的Locale
mt  int N   0   last modified time
Op  string  N   None    运营商名称
p   string  Y       屏幕sid，该屏起始位置start，请求卡片数目limit组成的三元组列表[[sid,start,limit],[sid,start,limit],…]

说明
   首次请求的时候，sid为[](空list)，返回最多4屏的数据(每屏的数据为前limit个数据)，和总共的屏幕数；
   Content id决定了该代码所要解析内容为小说、视频等等；
返回的数据结构
正常情况下：
{
  "result": 0, // 0 = 成功，1 = 无更新, 其他=错误代码
  “msg”: “OK”, // 描述信息
  “data”: {
    “1”:[//key为screen id；
    {
        “sid”:1
        “order”:1,
        //卡片中小说或者视频，其他的描述字段；
}，
…
],
    “2”:[//key为screen id；
    {
        “sid”:2
        “order”:1,
        //卡片中小说或者视频，其他的描述字段；
}，
…
],

…
},
“screen_data”:{
 “1”:{
   “title”:”男生频道”,
   “more_url”:”www.dolphin-browser.com”,
   “stid”: 1,
}
}
}
其中小说返回的item的内容是：
{
“sid”:1
“order”:1,
“fixed”:False,
    “title”:” 总裁的小萌妻”,
    “image”:” http://img.m.baidu.com/novel/cp/35/20130530/22/22.jpg”,
    “size”:1  //1=”1*1”, 2=”1*2”, 3=”2*1”, 4=”2*2”,
    “pattern”:1  //1=”图文推荐”, 2=”封面推荐”, 3=”纯色分类”
    “url”:” http://www.yqxw.net/files/article/html/34/34147/index.html”,
    “description”:””,
    “tags”:[
        “bottom”:{
            “description”:”热门小说”,
            “color”:”#FF”,
}
“corner”:{
    “direction”:”1”, //四个角的编号，1,2,3,4分别代表左上，右上，左下，右下
    “description”:”现代”,
    “color”:”#F0”,
}
]
}，
视频返回的item的内容是：
{
“sid”:1
“order”:1,
“fixed”:False,
    “title”:” 总裁的小萌妻”,
    “image”:” http://img.m.baidu.com/novel/cp/35/20130530/22/22.jpg”,
    “size”:1  //1=”1*1”, 2=”1*2”, 3=”2*1”, 4=”2*2”,
    “pattern”:1  //1=”图文推荐”, 2=”封面推荐”, 3=”纯色分类”
    “url”:” http://www.yqxw.net/files/article/html/34/34147/index.html”,
    “tags”:[
        “bottom”:{
            “description”:”热门小说”,
            “color”:”#FF”,
}
]
}，
无满足条件的数据时：
{
  "result": 1, // 0 = 成功，1 = 无更新, 其他=错误代码
  “msg”: “No Update”, // 描述信息
  “data”: {}
}
