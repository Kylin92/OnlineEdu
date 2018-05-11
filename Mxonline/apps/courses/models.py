from django.db import models
from datetime import datetime
from organization.models import CourseOrg, Teacher
from DjangoUeditor.models import UEditorField


class Course(models.Model):
    DEGREE_CHOICES = (
        ("cj", u"初级"),
        ("zj", u"中级"),
        ("gj", u"高级")
    )
    # 指向该课程来自哪个机构;注意后面最好是加上null、blank;
    course_org = models.ForeignKey(CourseOrg,on_delete=models.CASCADE, verbose_name=u"所属机构",null=True,blank=True)
    # 课程页面右侧关联的讲师;[在数据库已经有相应记录的情况下,需允许该字段默认值为空]
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,verbose_name=u"讲师", null=True, blank=True)

    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    # TextField允许我们不输入长度。可以输入到无限大。暂时定义为TextFiled，之后更新为富文本
    # detail = models.TextField(verbose_name=u'课程详情')
    # 此处配置的富文本字段;imagePath是图片的存储路径;filePath是文件的上传路径;所加的都是相对路径;
    detail = UEditorField(verbose_name=u"课程详情", width=600, height=300, imagePath="courses/ueditor/", filePath="courses/ueditor/",default='')

    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    degree = models.CharField(choices=DEGREE_CHOICES, max_length=2, verbose_name=u"难度")
    # 使用分钟做后台记录(存储最小单位)前台转换
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    # 保存学习人数:点击开始学习才算
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")

    # 该两个字段与所添加的课程讲师相关联;
    you_need_know = models.CharField(max_length=300, default=u"知识改变命运", verbose_name=u"课程须知")
    teacher_tell = models.CharField(max_length=300, default=u"爱拼才会赢", verbose_name=u"老师告诉你")
    image = models.ImageField(
        upload_to="courses/%Y/%m",
        verbose_name=u"封面图",
        max_length=100)
    # 保存点击量，点进页面就算
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    category = models.CharField(max_length=20, verbose_name=u"课程类别", default=u"后端开发")
    # 课程标签,用作课程详情页中的相关课程推荐使用(同一个类别的课程具有相同的标签);
    tag = models.CharField(max_length=15, verbose_name=u"课程标签", default=u"")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    # 可以用下面的函数替代前端代码中的标签:course.lesson_set.count
    # def get_zj_nums(self):
    #     # 获取课程章节数的方法,此处的self即是本类的实例;
    #     return self.lesson_set.all().count()

    # 获取学习这门课程的用户
    # 替代标签:course.usercourse_set.get_queryset|slice:":5";
    # def get_learn_users(self):
    #     # 谁的里面添加了它做外键，他都可以取出来
    #     return self.usercourse_set.all()[:5]

    def __str__(self):
        return self.name


# 章节
class Lesson(models.Model):
    # 因为一个课程对应很多章节,所以在章节表中将课程设置为外键;
    # 作为一个字段来让我们可以知道这个章节对应那个课程;
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    # 在调用类的实例时显示我们所需要的中文名称;
    def __str__(self):
        return '《{0}》课程的章节 >> {1}'.format(self.course,self.name)

    # 获取章节下的所有视频;[无须在前端设置复杂的逻辑处理代码]
    def get_lesson_video(self):
        return self.video_set.all()


# 每章视频
class Video(models.Model):
    # 因为一个章节对应很多视频,所以在视频表中将章节设置为外键.
    # 作为一个字段来存储让我们可以知道这个视频对应哪个章节.
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name=u"章节")

    # 此处的视频默认链接在后面需做好修改;
    url = models.CharField(max_length=200, default="http://blog.mtianyan.cn/", verbose_name=u"访问地址")
    name = models.CharField(max_length=100, verbose_name=u"视频名")

    # 使用分钟做后台记录(存储最小单位)前台转换
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}章节的视频 >> {1}'.format(self.lesson,self.name)


# 课程资源
class CourseResource(models.Model):
    # 因为一个课程对应很多资源,所以在课程资源表中将课程设置为外键;
    # 作为一个字段来让我们可以知道这个资源对应哪个课程;
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")

    # 这里定义成文件类型的filefield，后台管理系统中会直接有上传的按钮;
    # FileField也是一个字符串类型，要指定最大长度。
    download = models.FileField(
        upload_to="course/resource/%Y/%m",
        verbose_name=u"资源文件",
        max_length=100)

    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '《{0}》课程的资源: {1}'.format(self.course,self.name)



