"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from accounts import views as accounts_views
from boards import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup/$', accounts_views.signup, name='signup'),
    # 需在setting中配置登陆后的跳转页面
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # 需在setting中配置退出后的跳转页面
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^boards/(?P<pk>\d+)/$', views.board_topics, name='board_topics'),
    url(r'^boards/(?P<pk>\d+)/new/$', views.new_topic, name='new_topic'),
     # ToDo: 这url虽然有层次但不够简洁
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/$', views.topic_posts, name='topic_posts'),
    url(r'^boards/(?P<pk>\d+)/topics/(?P<topic_pk>\d+)/reply/$', views.reply_topic, name='reply_topic'),
    url(r'^admin/', admin.site.urls),
]


password_reset = [
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            # 带有表单的页面，用于启动重置过程
            template_name='password_reset.html',
            # 发送给用户的电子邮件正文
            email_template_name='password_reset_email.html',
            # 电子邮件的主题行，它应该是单行文件
            subject_template_name='password_reset_subject.txt'
            ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(
            # 一个成功的页面，表示过程已启动，指示用户检查其邮件
            template_name='password_reset_done.html'
            ),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            # 检查通过电子邮件发送token的页面
            template_name='password_reset_confirm.html'
            ),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            # 告诉用户重置是否成功的页面
            template_name='password_reset_complete.html'
            ),
        name='password_reset_complete')
]

password_change = [
    url(r'^settings/password/$', 
        # 如果用户没有登录，Django会将他们重定向到登录页面
        # 我们必须在settings.py中定义我们应用程序的登录URL
        auth_views.PasswordChangeView.as_view(
            template_name='password_change.html'
            ),
        name='password_change'),
    url(r'^settings/password/done/$', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'
            ),
        name='password_change_done'),
]

urlpatterns.extend(password_reset)
urlpatterns.extend(password_change)
