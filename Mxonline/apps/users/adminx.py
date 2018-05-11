import xadmin
# 和xadmin的view绑定
from xadmin import views

from .models import EmailVerifyRecord, Banner


# xadmin的全局配置信息设置
class BaseSetting(object):
    # 主题功能开启
    enable_themes = True
    use_bootswatch = True


# x admin 全局配置参数信息设置
class GlobalSettings(object):
    site_title = "暮学后台管理系统"
    site_footer = "暮学在线网"
    # 收起菜单
    menu_style = "accordion"


# 创建admin的模型管理类,这里不再是继承admin(继承也没用),而是继承object
class EmailVerifyRecordAdmin(object):
    # 配置后台我们需要显示的列
    list_display = ['code', 'email', 'send_type', 'send_time']
    # 配置搜索字段,不做时间搜索,因为无法对时间进行搜索;
    search_fields = ['code', 'email', 'send_type']
    # 配置筛选字段
    list_filter = ['code', 'email', 'send_type', 'send_time']


# 创建banner的管理类
class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# 将xadmin全局管理器与我们的view绑定注册;
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 将头部与脚部信息进行注册;
xadmin.site.register(views.CommAdminView, GlobalSettings)


