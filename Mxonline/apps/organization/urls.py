from organization.views import OrgView, AddUserAskView, OrgHomeView, OrgCourseView, OrgDescView, OrgTeacherView, \
    AddFavView, TeacherListView, TeacherDetailView
from django.conf.urls import url

# 加上一个命名空间;
app_name = "organization"

urlpatterns = [
    # 课程机构列表url
    url(r'^list/$', OrgView.as_view(), name="org_list"),
    # 我要学习;
    url(r'add_ask/$', AddUserAskView.as_view(), name="add_ask"),
    # 课程机构首页;
    url(r'home/(?P<org_id>\d+)/$', OrgHomeView.as_view(), name="org_home"),
    # 访问课程
    url(r'^course/(?P<org_id>\d+)/$', OrgCourseView.as_view(), name="org_course"),
    # 访问机构描述
    url(r'^desc/(?P<org_id>\d+)/$', OrgDescView.as_view(), name="org_desc"),

    # 访问机构讲师
    # url(r'^teacher/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name="org_teacher"),
    # 为避免与下面讲师列表页的冲突,所以此处用url-name来替换前面的正则匹配路径;
    url(r'org_teacher/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name="org_teacher"),

    # 机构收藏
    url(r'^add_fav/$', AddFavView.as_view(), name="add_fav"),
    # 讲师列表
    url(r'^teacher/list/$', TeacherListView.as_view(), name="teacher_list"),
    # 教师详情页
    url(r'^teacher/detail/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),

]

