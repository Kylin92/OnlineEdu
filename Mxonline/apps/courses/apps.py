from django.apps import AppConfig


class CoursesConfig(AppConfig):
    name = 'courses'
    # 将后台左侧默认的名称改为中文名;
    verbose_name=u'课程信息'
