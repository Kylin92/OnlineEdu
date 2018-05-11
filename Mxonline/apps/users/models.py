from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser


# 用户信息;
# 继承AbstractUser,是因为其内部已经有自定义好的一些字段,我们直接继承就行;
class UserProfile(AbstractUser):
    # 昵称
    nick_name = models.CharField(max_length=50, verbose_name=u"昵称", default="")
    # 生日，可以为空
    birthday = models.DateField(verbose_name=u"生日", null=True, blank=True)

    # 性别,此处在前端页面展示的是多选样式;
    gender=models.CharField(
        max_length=6,
        verbose_name=u'性别',
        choices=(('male',u'男'),('female',u'女')),
        default='female')

    # 地址
    address = models.CharField(max_length=100, verbose_name="地址", default="")
    # 电话
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name=u"电话")

    # 头像 默认使用default.png;
    # imageField实际上也是charField,所以也需加上max_length;
    image = models.ImageField(
        upload_to="image/%Y/%m",
        default=u"image/default.png",
        max_length=100,
        verbose_name=u"头像"
    )

    # meta信息(元数据)，即后台栏目名称;
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    # 重载__str__方法，打印实例会打印username，username为继承自AbstractUser
    def __str__(self):
        return self.username

    # 顶部小喇叭:获取用户未读消息的数量;
    def unread_nums(self):
        from operation.models import UserMessage
        # 改进取出未读数字;
        return UserMessage.objects.filter(has_read=False, user=self.id).count()

# 邮箱验证码;
class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    # 未设置null = true,blank = true 默认不可为空
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")

    # 发送类型的种类需做好设计;
    send_type = models.CharField(choices=(
                                        ("register", u"注册"),
                                        ("forget", u"找回密码"),
                                        ("update_email", u"修改邮箱"),
                                        ),
                                 max_length=20,
                                 verbose_name=u"验证码类型")

    # 这里的now得去掉(),不去掉会根据编译时间;而不是根据实例化时间;
    send_time = models.DateTimeField(default=datetime.now, verbose_name=u"发送时间")

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name

    # 重载str方法使后台不再直接显示object
    # 在python2中是用__unicode__调用;在python3中则是__str__;
    def __str__(self):
        return '{0}({1})'.format(self.code, self.email)


# 轮播图;
class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name=u"标题")

    image = models.ImageField(
        upload_to="banner/%Y/%m",
        verbose_name=u"轮播图",
        max_length=100)
    url = models.URLField(max_length=200, verbose_name=u"访问地址")

    # 默认index很大靠后,想要靠前修改index值;
    index = models.IntegerField(default=100, verbose_name=u"顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"轮播图"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}(位于第{1}位)'.format(self.title, self.index)

