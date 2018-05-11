from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    # 让后台左侧的标题栏显示中文名;
    verbose_name=u'用户信息'

