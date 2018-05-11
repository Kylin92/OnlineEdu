from django.conf.urls import url

from courses.views import CourseListView, CourseDetailView, CourseInfoView, VideoPlayView, AddCommentsView, CommentsView

urlpatterns = [
    # 课程列表url
    url(r'^list/$', CourseListView.as_view(), name="list"),
    # 课程详情页
    url('^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="course_detail"),
    # 课程章节信息页
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name="course_info"),
    # 课程视频播放页
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name="video_play"),
    # 一般方式的添加课程评论;
    url(r'^comments/(?P<course_id>\d+)/$', CommentsView.as_view(), name="course_comments"),
    # 用ajax方式添加的课程评论,把相关参数放至post中;
    url(r'^add_comment/$', AddCommentsView.as_view(), name="add_comment"),

]
