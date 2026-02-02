from MenuLite.Menu.Func import Func
import os

__all__ = ['举报所有作品', '点赞所有作品', '收藏所有作品', '评论所有作品', '浏览所有作品', '生成学生列表', '批量举报帖子', '添加指定用户的token到tokens文件', '搜索指定作品的评论并置顶or取消置顶', '清除新消息通知', '发布自定义url的CoCo作品', '退出登录']

def 举报所有作品():
    Func.ReportAllWorks()

def 点赞所有作品():
    Func.LikeAllWorks()

def 收藏所有作品():
    Func.CollectAllWorks()
        
def 评论所有作品():
    Func.ReviewAllWorks()

def 浏览所有作品():
    Func.ViewAllWorks()

def 生成学生列表():
    Func.GenerateStudentList()

def 批量举报帖子():
    Func.BRP()

def 添加指定用户的token到tokens文件():
    Func.AddToken()

def 搜索指定作品的评论并置顶or取消置顶():
    Func.SearchAndPinComment()

def 清除新消息通知():
    Func.CleanNewMessages()

def 发布自定义url的CoCo作品():
    Func.PublishCustomCoCoWork()

def 更新():
    os.system('python updater.py')

def 退出登录():
    Func.Logout()
