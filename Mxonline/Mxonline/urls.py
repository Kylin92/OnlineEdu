"""Mxonline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.views.static import serve

import xadmin
# 该模块可以直接指向环境中的静态内容;
from django.views.generic import TemplateView

from Mxonline.settings import MEDIA_ROOT
from organization.views import OrgView
from users.views import LoginView,RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, \
    IndexView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    # 首页;直接在类的as_view方法里加入前端页面参数,指向前端页面;在无需设置视图的情况下即可完成页面的加载;
    # url(r'^$',TemplateView.as_view(template_name='index.html'),name='index'),
    # View中做好完善之后修改首页的url路径;
    url(r'^$', IndexView.as_view(), name= "index"),

    # 登录页面;其指向的其前端页面需在index中做‘登录’跳转的修改;将login.html改成'/login/';
    # url(r'^login/$', TemplateView.as_view(template_name="login.html"), name="login"),
    # 基于类方法实现登录,这里是调用它的方法
    url(r'^login/$',LoginView.as_view(),name='login'),

    # 退出功能url
    url(r'^logout/$', LogoutView.as_view(), name="logout"),

    # 注册页面;
    url(r'^register/$',RegisterView.as_view(),name='register'),
    # 用于用户注册的验证码;
    url(r'^captcha/', include('captcha.urls')),
    # 激活用户url;
    url(r'^active/(?P<active_code>.*)/$',ActiveUserView.as_view(), name= "user_active"),
    # 忘记密码;
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    # 重新设置密码;
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    # 修改密码url; 用于passwordreset页面提交表单
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    # 课程机构页面;下面有专门配置的二级路由指向,所以先注释掉;
    # url(r'^org_list/$', OrgView.as_view(), name="org_list"),

    # 处理前端页面图片显示的url,使用Django自带的serve,传入参数告诉它去哪个路径找,我们有配置好的路径MEDIA_ROOT
    # 此处的serve方法是用来处理静态文件的;
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT }),
    # 注意:我们自己url响应我们的static;此处配置是连同404/500的设置;
    # url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),

    # 二级路由配置：课程机构app的url配置(因为课程机构中需要配置众多的url,所以进行单独的url设置);
    # 此处的命名空间是为了防止路由地址相同所引起的冲突,在具体的地址前面加上'org'的话,可以使url地址唯一性;
    url(r"^org/", include('organization.urls',namespace="org")),

    # 课程app的url配置;后面是命名空间;
    url(r"^course/", include('courses.urls', namespace="course")),

    # 用户中心的url配置;
    url(r"^users/", include('users.urls', namespace="users")),

    # 富文本相关url;
    url(r'^ueditor/',include('DjangoUeditor.urls' )),

]


# 全局404页面配置
# handler404 = 'users.views.page_not_found'

# 全局500页面配置
# handler500 = 'users.views.page_error'


