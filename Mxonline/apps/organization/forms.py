import re
from django import forms
from operation.models import UserAsk


# 说明：因为'我要学习'的提交表单是在机构列表页当中,所以需从operation模型中导入UserAsk模型;
# 并建立Form模型;


# 普通版本的form操作创建表单;
# class UserAskForm(forms.Form):
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     phone = forms.CharField(required=True, max_length=11, min_length=11)
#     course_name = forms.CharField(required=True, min_length=5, max_length=50)


# 进阶版本的modelform：具有model的基本功能,可以直接将数据保存至数据库中;
class UserAskForm(forms.ModelForm):
    # 继承之余还可以新增字段
    # mywantname=forms.CharField(required=True, min_length=2, max_length=20)

    # 声明是由哪个model转换而来;
    class Meta:
        model = UserAsk
        # 可以用列表选取需要用到的model中的字段;
        fields = ['name','mobile','course_name']

    # 自定义的验证方式:对手机号的验证直接在form表单中完成;
    # 手机号的正则表达式验证:函数的命名需以clean开头+需要验证的字段;
    def clean_mobile(self):
        # cleaned_data是form的内置变量,表示已经对该mobile字段clean了,且cleaned_data是一个字典形式的数据存储样式;
        mobile = self.cleaned_data['mobile']
        # 手机号码的正则表达式:用过滤器将相应号码分为3段可能性;
        REGEX_MOBILE = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(REGEX_MOBILE)
        # 判断前端输过来的号码数据是否与正则中规定的样式匹配;
        if p.match(mobile):
            return mobile
        else:
            # 抛出自定义的错误提示信息;
            raise forms.ValidationError(u"手机号码非法", code="mobile_invalid")


