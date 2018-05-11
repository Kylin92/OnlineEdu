from django import forms
# 引入验证码field
from captcha.fields import CaptchaField
from users.models import UserProfile


# 说明：之所以创建forms.py,是对前端页面接收数据的验证,省去多余的python代码;

# 登录表单验证
class LoginForm(forms.Form):
    # True表示用户名密码不能为空
    username = forms.CharField(required=True)
    # min_length规定密码的最少字符数;
    password = forms.CharField(required=True, min_length=5)


# 验证码form & 注册表单form
class RegisterForm(forms.Form):
    # 所有的字段都需与前端所需的内容保持一致;
    # 此处email与前端name需保持一致;
    email = forms.EmailField(required=True)
    # 密码不能小于5位
    password = forms.CharField(required=True, min_length=5)
    # 注册时显示的验证码;启用debug时,若是验证码输入错误,则在调试结果中显示为中文提示信息;
    captcha = CaptchaField(error_messages={'invalid':u'验证码错误'})
    # 不同的字段在前端生成不同的input框;


# 激活时验证码实现
class ActiveForm(forms.Form):
    # 激活时不对邮箱密码做验证
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


# 忘记密码--验证码
class ForgetForm(forms.Form):
    # 此处email与前端name需保持一致;
    email = forms.EmailField(required=True)
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


# 重置密码的form实现
class ModifyPwdForm(forms.Form):
    # 密码不能小于5位
    password1 = forms.CharField(required=True, min_length=5)
    # 密码不能小于5位
    password2 = forms.CharField(required=True, min_length=5)


# 用于文件上传，修改头像
class UploadImageForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['image']


# 用于个人中心修改个人信息
class UserInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['nick_name','gender','birthday','address','mobile']


