from random import Random
from users.models import EmailVerifyRecord
# 导入Django自带的发送邮件模块;
from django.core.mail import send_mail
# 导入setting中发送邮件的配置;
from Mxonline.settings import EMAIL_FROM


# 生成随机字符串;缺省参数设置为8位;
def random_str(random_length=8):
    str = ''
    # 生成字符串的可选字符集;
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    # 实例化随机类:取出具体的random方法;
    random = Random()
    for i in range(random_length):
        # 在字符集中做随机取值;
        str += chars[random.randint(0, length)]
    return str


# 发送注册邮件;
# 两个参数：接收内容的邮箱/邮件发送的种类(此处默认设置的是注册);
def send_register_email(email, send_type="register"):
    # 发送之前先保存到数据库，到时候查询链接是否存在

    # 实例化一个EmailVerifyRecord对象
    email_record = EmailVerifyRecord()
    # 生成随机的code放入链接
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    # 保存至数据库;
    email_record.save()

    # 定义邮件内容:
    # 邮件标题;
    email_title = ""
    # 邮件主体内容;
    email_body = ""

    # 对邮件发送种类进行判断;
    if send_type == "register":
        email_title = "注册激活链接"
        # 链接里加入随机生成的验证码;
        email_body = "请点击下面的链接激活你的账号: http://127.0.0.1:8000/active/{0}".format(code)

        # 使用Django内置函数完成邮件发送;四个参数：标题，邮件内容，邮件发送者，接收者list;
        # 函数send_mail会返回一个True/Faulse的值,此处设置send_status作为接收的变量;
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])

        # 如果是True,则表示发送成功;
        if send_status:
            pass

    elif send_type == "forget":
        email_title = "找回密码链接"
        email_body = "请点击下面的链接重置密码: http://127.0.0.1:8000/reset/{0}".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])

        if send_status:
            pass

