from utils.mixin_utils import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course, CourseResource, Video

from operation.models import UserFavorite, UserCourse, CourseComments


# 课程列表页;
class CourseListView(View):
    # 先写get函数,此处所写的函数跟之前的方式是一样的：将单独的get/post方法写做一个函数;
    def get(self, request):
        # 获取所有课程;
        all_course = Course.objects.all()
        # 热门课程推荐
        hot_courses = Course.objects.all().order_by("-students")[:3]

        # 全局搜索功能;
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # 多重条件结合筛选需用上Q,其与| and or都是做相应的匹配的;
            # 这里的筛选条件应该可以加上：name/desc/detail,即可以根据课程的名称、描述、课程详情来做筛选;
            all_course = all_course.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                detail__icontains=search_keywords))

        # 对页面中的'最热门'/'参与人数'进行排序;
        # 此处[request.GET.get('sort', "")]是从前台的a标签中的sort=xxx进行判断取值;
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                # 根据学习人数进行倒序排序;
                all_course = all_course.order_by("-students")
            elif sort == "hot":
                # 根据点击数进行倒序排序;
                all_course = all_course.order_by("-click_nums")

        # 对课程进行分页(此处的分页器设置与机构列表页是一样的操作);
        # 尝试获取前台get请求传递过来的page参数;如果是不合法的配置参数则默认返回第一页;
        # 分页的代码必须写在后边,因为它在所有数据处理好的情况下才做的最终分页,否则分页器会失效;
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 此处调用了分页器,指从all_course中取4个出来，每页显示4个
        p = Paginator(all_course, 3, request=request)
        # 经过page处理过的courses不再是queryset类型的值,而是一个purepage对象(只显示页数);
        courses = p.page(page)

        return render(request, "course-list.html", {
            # 返回至前端页面时,类似org-list,在做循环的时候需加上一个object_list变量;
            "all_course": courses,
            "sort": sort,
            "hot_courses": hot_courses,
            "search_keywords": search_keywords
        })


# 课程详情处理view;
class CourseDetailView(View):
    def get(self, request, course_id):
        # 此处的id为数据库表默认为我们添加的值;
        course = Course.objects.get(id=int(course_id))

        # 增加课程点击数;
        course.click_nums += 1
        # 保存至数据库中;
        course.save()

        # 设置是否收藏的字段做判断;然后在前端页面代码中做条件判断;
        # 是否收藏课程;暂时默认设置为False;
        has_fav_course = False
        # 是否收藏机构;暂时默认设置为False;
        has_fav_org = False

        # 必须是用户已登录我们才需要判断(因为未登陆情况下是无法识别是谁做的收藏);
        if request.user.is_authenticated:
            # 过滤中设置3个叠加条件以保证筛选的唯一性;
            # 收藏的是课程;
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            # 收藏的是机构(course.course_org.id--此处调用的外键引用);
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 取出标签,找到tag标签相同的course;
        # 此处tag的值即是一个单独的课程标签设置;跟最上面的一对一course取值类似;
        tag = course.tag
        # 如果有tag,则对其进查找取值;
        if tag:
            # 从1开始否则会推荐自己;暂时只取出一个;
            relate_courses = Course.objects.filter(tag=tag)[1:2]
        else:
            relate_courses = []

        return render(request, "course-detail.html", {
            "course": course,
            "relate_courses": relate_courses,
            # 在前端代码中做条件判断及显示;
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
        })


# 课程章节信息*********************************************************************;
# 在进行点击‘开始学习’时,做一个用户登录的验证:LoginRequiredMixin;所以给view加一个登录权限;
# 若是用户未登录,则跳转至登录页面;只有在登录之后才能进入'开始学习'的页面;
# 在utils中加入一个mixin_utils.py文件;
class CourseInfoView(LoginRequiredMixin, View):
    # 此处是进行登录验证判断的两个类属性(用作mixin_utils.py中函数的参数);
    # login_url = '/login/'
    # redirect_field_name = 'next'

    # 重载get方法;
    def get(self, request, course_id):
        # 此处的id为表默认为我们添加的值。
        course = Course.objects.get(id=int(course_id))

        # 此处是将user和course做关联;
        # 查询用户是否开始学习了该课程[因为已经进行了登录权限的验证,所以可以直接取值user=request.user,];
        # 如果还未学习则加入用户学习的课程列表中;
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 通过添加两个类属性参数的方式来创建实例;
            user_course = UserCourse(user=request.user, course=course)
            # 课程的学习人数+1;
            course.students += 1
            # 分别保存至数据库;
            course.save()
            user_course.save()

        # 通过上面所获取的课程名来查询其对应课程资源;
        all_resources = CourseResource.objects.filter(course=course)
        # 选出学了这门课的学生关系;
        user_courses = UserCourse.objects.filter(course=course)
        # 从关系中取出user_id;
        user_ids = [user_course.user_id for user_course in user_courses]
        # 这些用户学了的课程,外键会自动有id，取到字段
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id;
        course_ids = [user_course.course_id for user_course in all_user_courses]

        # 获取学过该课程的用户学过的其他课程;‘__’双下划线表示的是一种关联关系;
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course.id)[:4]

        # 是否收藏课程
        return render(request, "course-video.html", {
            "course": course,
            "all_resources": all_resources,
            "relate_courses": relate_courses,
        })


# 课程视频播放;
# 此处大部分内容与CourseInfoView是一样的;在重写的时候注意其区别及联系;
class VideoPlayView(LoginRequiredMixin, View):
    # login_url = '/login/'
    # redirect_field_name = 'next'

    def get(self, request, video_id):
        # 通过前台传入的video_id获取到当前所点击查看的video;
        video = Video.objects.get(id=int(video_id))
        # 获取到video之后,通过两个表中的两个外键找到对应的course;
        course = video.lesson.course

        # 下面的代码操作跟CourseInfoView基本一样;注意细小的差别点;
        # 查询用户是否开始学习了该课，如果还未学习则将其添加至加至用户课程表中;
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            # 如果没有学习该课程,则根据现有条件添加一条记录;
            user_course = UserCourse(user=request.user, course=course)
            # 保存至数据库中;
            user_course.save()

        # 查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        # 选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)
        # 从关系中取出user_id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 这些用户学了的课程,外键会自动有id，取到字段
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course_id for user_course in all_user_courses]
        # 获取学过该课程用户学过的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course.id)[:4]
        # 是否收藏课程
        return render(request, "course-play.html", {
            "course": course,
            "all_resources": all_resources,
            "relate_courses": relate_courses,
            "video": video,
        })


# 添加课程评论[常规方式];**********************************************
# 此处与下面的ajax方式添加评论并无冲突;all_comments的获取还是得从此类中得出;
class CommentsView(LoginRequiredMixin, View):
    # login_url = '/login/'
    # redirect_field_name = 'next'

    def get(self, request, course_id):
        # 此处的id为表默认为我们添加的值;因为传进来的course_id是str类型,所以我们必须对其进行int类型的转换;
        # 因为是获取课程下的所有评论,所以我们首先得获取现在是处在哪个课程中;因为CourseComments中有一个指向course外键;
        # 所以此处的course_id即对应的是Course表中的id;Course.objects是由所有课程名组成的一个列表[queryset];
        course = Course.objects.get(id=int(course_id))
        # 获取该课程下的所有课程资源;此处的course同样是外键关联;
        all_resources = CourseResource.objects.filter(course=course)

        # [先获取该课程下的所有评论信息,所组成的是一个列表]按所添加的时间给评论做倒序排列;
        all_comments = CourseComments.objects.filter(course=course).order_by("-add_time")

        # 获取用户与课程之间的关系：[<UserCourse:用户(kylin)学习了django入门>...];    ???为什么这里取不到所有的关系???
        user_courses = UserCourse.objects.filter(course=course)
        # 从关系中通过列表推导式取出user_id(用户与课程的关系表中有两个关联的外键字段:user/course,所以user_id也是在数据库中所自动生成的);
        user_ids = [user_course.user_id for user_course in user_courses]
        # 获取所有的用户与课程的关联关系;这里的user_id是数据库通过外键所自动加上的;(双下划线表示的是一种关联关系)
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 这里是通过同样的方式在获取所有的课程与用户关系之后,在取出与course做外键关联的所有course_id;
        course_ids = [user_course.course_id for user_course in all_user_courses]
        # 获取学过该课程用户学过的其他课程,按点击数进行降序排列;
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course.id)[:4]

        # 是否收藏课程
        return render(request, "course-comment.html", {
            "course": course,
            "all_resources": all_resources,
            "all_comments": all_comments,
            "relate_courses": relate_courses,
        })


# ajax方式添加评论;
class AddCommentsView(View):
    # 使用的是较为安全的post方法;
    def post(self, request):
        # 对是否登录进行判断;
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的;括号中的信息内容将提交给ajax代码进行解析处理;
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        # 根据前端页面中传过来的课程id取到对应的课程id值[这样就知道评论的是哪个课程];课程id默认设置为0;
        course_id = request.POST.get("course_id", 0)
        # 从前端页面中获取评论内容;
        comments = request.POST.get("comments", "")

        # 课程id非0,且有评论提交的情况下;
        if int(course_id) > 0 and comments:
            # 实例化一个类实例;及给对应的课程评论表中添加一条数据记录;
            course_comments = CourseComments()
            # get只能取出一条数据,如果有多条抛出异常,没有数据也抛异常;
            # filter取一个列表出来:queryset;没有数据返回空的queryset不会抛异常;
            # 根据上面的course_id,获取到对应的课程;
            course = Course.objects.get(id = int(course_id))
            # 外键存入要存入对象
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            # 将该条记录保存至数据库中;
            course_comments.save()

            # 返回给前端页面中的ajax进行处理;
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')

        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')
