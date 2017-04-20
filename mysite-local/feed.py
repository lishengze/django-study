#coding=utf-8
'''
Created on 2011-2-16

@author: xugang
'''
from django.contrib.syndication.views import Feed
from blog.models import Essay

class LatestEntriesFeed(Feed):
    #订阅标题
    title = u"许刚的博客的更新"
    link = "/feeds/"
    #描述
    description = "关注许刚的最新动态"
    #订阅的数据
    def items(self):
    
        return Essay.objects.order_by('-pub_date')[:5]
    #订阅的标题
    def item_title(self, item):     
        return item.title
    #订阅的表示
    def item_description(self, item):
        return item.abstract
    #每条订阅的链接
    def item_link(self,item):
        return "xgjava.com/essay/"+str(item.id)+"/"