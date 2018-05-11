from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from courses.models import Course
from operation.models import UserFavorite
from organization.forms import UserAskForm
from organization.models import CourseOrg, CityDict, Teacher
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# 课程机构列表功能;
class OrgView(View):
    def get(self, request):
        # 查找到所有的课程机构,对应的是数据库中所有的数据记录;
        all_orgs = CourseOrg.objects.all()

        # 热门机构,如果不加负号会是由小到大(按点击数倒序排列),取前三个;
        hot_orgs = all_orgs.order_by("-click_nums")[:3]

        # 全局搜索功能;
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                address__icontains=search_keywords))

        # 取出所有的城市;
        all_city = CityDict.objects.all()

        # 取出筛选的城市,默认值为空(括号中的city是前端页面传过来的值：city={{ city.id }});
        city_id = request.GET.get('city', "")

        # 如果选择了某个城市,也就是前端传过来了值;
        if city_id:
            # 外键city在数据库中叫city_id
            # 我们就在机构中作进一步筛选
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选:获取从前端页面传过来的值;
        category = request.GET.get('ct', "")
        if category:
            # 我们就在机构中作进一步筛选类别;
            all_orgs = all_orgs.filter(category=category)

        # 进行排序(学习人数/课程数);此处的sort同样是获取前端传过来的值;
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                # 倒序排列;
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        # 总共有多少家机构使用count进行统计(位置相当重要:若是放在前面则是会过早地做统计)
        org_nums = all_orgs.count()

        # 对课程机构进行分页*****************(暂时不要求理解,会用就行);
        # 应用的是第三方的分页器;
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            # 此处括号中的page是自动生成的参数;
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 配置安装包中的objects实际上是数据库中所有的数据记录：all_orgs;
        # 这里指从all_orgs中取4个出来，每页显示4个
        p = Paginator(all_orgs, 4, request=request)
        # 将people换成orgs,其会自动进行分页;
        orgs = p.page(page)

        return render(request, "org-list.html", {
            # 将all_orgs换成orgs,这样即不会传递数据库中所有的数据记录;
            "all_orgs": orgs,
            "all_city": all_city,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort,
            "search_keywords": search_keywords,
        })


# 用户添加'我要学习';
class AddUserAskView(View):
    # 处理表单提交当然post
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        # 判断该form是否有效
        if userask_form.is_valid():
            # 这里是modelform和form的区别,它有model的属性save;
            # 当commit为true时,提交保存至数据库中：将Form中的field传输至所调用的model中,并保存到数据库;
            # 这样就不需要把一个一个字段取出来然后存到model的对象中之后save;
            user_ask = userask_form.save(commit=True)

            # 数据的提交是ajax的异步形式,不做整个页面的刷新,所以在返回的时候不应该是页面,而应该是json的数据;
            # 因为在前端操作的时候是ajax方式提交过来的,所以返回页面也是无效的;
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器的;

            # 注意此处的数据发送格式:前面是提交的状态,后面是指明json字符串的所属格式(因为浏览器接收到的是一串json字符串);
            # content_type='application/json'这个是固定的浏览器支持的格式;浏览器会对这串数据进行解析;
            return HttpResponse("{'status': 'success'}", content_type='application/json')

        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            # return HttpResponse("{'status': 'fail', 'msg':{0}}".format(userask_form.errors),  content_type='application/json')
            # 因为userask_form.errors中的提示信息较多,所以在此处统一设置错误提示为'添加出错';
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


# 课程机构首页;
class OrgHomeView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "home"

        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 课程的点击数+1;
        course_org.click_nums += 1
        course_org.save()

        # 向前端传值说明用户是否收藏,默认设置是false未收藏;
        # 机构详情页左侧的4个标签都是要做has_fav的判断的;
        has_fav = False
        # 必须是用户已登录我们才需要判断;
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                # 修改成已收藏;
                has_fav = True

        # 通过课程机构找到相关联的所有课程;注意其格式:这是django中所有外键都有的反向查询功能;
        all_courses = course_org.course_set.all()[:4]
        all_teacher = course_org.teacher_set.all()[:2]

        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teacher': all_teacher,
            'course_org': course_org,
            "current_page": current_page,
            # 将判断的值带入前端页面中做判断及显示;
            "has_fav": has_fav
        })


# 机构课程列表页;
class OrgCourseView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "course"
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 通过课程机构找到课程;外键的反向查询功能;
        all_courses = course_org.course_set.all()

        # 向前端传值说明用户是否收藏
        has_fav = False

        # 必须是用户已登录我们才需要判断;
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        })


# 机构介绍详情页;
class OrgDescView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "desc"
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))

        # 向前端传值说明用户是否收藏
        has_fav = False

        # 必须是用户已登录我们才需要判断;
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            "current_page": current_page,
            "has_fav": has_fav,
        })


# 机构讲师列表页;
class OrgTeacherView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "teacher"
        # 根据id取到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 通过课程机构找到课程。内建的变量，找到指向这个字段的外键引用
        all_teachers = course_org.teacher_set.all()
        # 向前端传值说明用户是否收藏
        has_fav = False

        # 必须是用户已登录我们才需要判断;
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


# 用户收藏与取消收藏功能;
class AddFavView(View):
    def post(self, request):
        # 表明你收藏的不管是课程，讲师，还是机构。他们的id默认值取0,是因为空串转int报错;
        # 此处运用get获取的fav_id/fav_type是从前台ajax传过来的值;
        id = request.POST.get('fav_id', 0)

        # 取到你收藏的类别，从前台提交的ajax请求中取
        type = request.POST.get('fav_type', 0)

        # 收藏与已收藏取消收藏：在确认是否收藏之前需判断用户是否登录;
        # 判断用户是否登录:即使没登录会有一个匿名的user(是一个匿名的类,django中自带的一个类);
        # is_authenticated此方法是判断用户是否已经登录(在前端页面中是做条件判断使用);
        if not request.user.is_authenticated:
            # 未登录时返回json信息提示未登录,此时不能做收藏;跳转到登录页面的操作是在ajax中完成的;
            # 此处的HttpResponse定义的是一个跟ajax对应的数据接口;此处的jason数据将传至前端的function(data)中进行解读及操作;
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        # 此处是取出已登录用户的信息;此处的fav_id与fav_type需换换成int类型;所以对应的在上面进行id/type取值时需默认设置为‘0’;
        # 参数user是当前登录的用户,从前端发送的数据中取出来;后面的两个参数是用作联合查询,以保证所收藏对象的唯一性;
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))

        if exist_records:
            # 如果收藏记录已经存在,我们可以理解为用户的意图是'取消收藏';
            # 做取消收藏的操作:直接删除该记录;
            exist_records.delete()

            if int(type) == 1:
                course = Course.objects.get(id=int(id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = CourseOrg.objects.get(id=int(id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            # 取消收藏之后在页面中显示‘收藏’(因为还是可以做收藏点击的操作,相应恶业务逻辑需做好了解);
            return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')

        # 如果收藏记录不存在,则做相应的创建添加,保存至数据库中;
        else:
            user_fav = UserFavorite()
            # 如果id/type是0的话就不能做添加的转换,所以先过滤掉未取到id、type的默认情况;
            if int(type) > 0 and int(id) > 0:
                # 此处仍然是要对前台所取到的id/type做int类型的转换;
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                # 将前端的user获取过来;
                user_fav.user = request.user
                # 保存至书数据库;
                user_fav.save()

                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()

                # 成功添加之后在页面中显示‘已收藏’;
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')

            # id/type是0的情况下,不做保存于不做删除,在页面中提示收藏出错;
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


# 课程讲师列表页;
class TeacherListView(View):
    def get(self, request):
        all_teacher = Teacher.objects.all()
        # 排序功能;
        sort = request.GET.get("sort", "")
        if sort:
            if sort == "hot":
                all_teacher = all_teacher.order_by("-click_nums")

        # 全局搜索功能;
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作;i代表不区分大小写;
            # or操作使用Q[当有多个条件用作过滤时,则启用Q作为条件的组合应用]
            all_teacher = all_teacher.filter(
                Q(name__icontains=search_keywords) | Q(work_company__icontains=search_keywords))

        # 讲师排行榜;
        rank_teacher = Teacher.objects.all().order_by("-fav_nums")[:5]

        # 用count统计讲师的数量;
        teacher_nums = all_teacher.count()

        # 对讲师进行分页
        # 尝试获取前台get请求传递过来的page参数
        # 如果是不合法的配置参数默认返回第一页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # 此处调用分页器:从all_teacher中取4个出来,每页显示4个;
        p = Paginator(all_teacher, 4, request=request)
        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teacher": teachers,
            "teacher_nums": teacher_nums,
            "sort": sort,
            "rank_teachers": rank_teacher,
            "search_keywords": search_keywords,
        })


# 教师详情页面;
# 说明：具体的操作跟org-detail类似;相应的代码可以做对比参考;
class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()
        # 通过teacher这个外键进行反向查询,获取该讲师所讲的所有课程;
        all_course = teacher.course_set.all()

        # 讲师排行榜;
        rank_teacher = Teacher.objects.all().order_by("-fav_nums")[:5]

        # 是否对讲师进行收藏;
        has_fav_teacher = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_fav_teacher = True

        # 是否对机构进行收藏;
        has_fav_org = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_fav_org = True

        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_course": all_course,
            "rank_teacher": rank_teacher,
            "has_fav_teacher": has_fav_teacher,
            "has_fav_org": has_fav_org,
        })
