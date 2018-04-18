'''
运行 Django 测试时会即时创建一个新的数据库，应用所有的model(模型)迁移 ，
运行测试完成后会销毁这个用于测试的数据库。
'''

from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth.models import User

from .views import home, board_topics, new_topic
from .models import Board, Topic, Post
from .forms import NewTopicForm

class HomeTests(TestCase):
    def setUp(self):
        url = reverse('home')
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        '''我们测试的是请求该URL后返回的响应状态码。状态码200意味着成功'''
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        '''确定URL / 返回 home 视图'''
        view = resolve('/')
        self.assertEquals(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        '''测试 response 主体部分是否包含给定的文本'''
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

    
class BoardTopicsTests(TestCase):
    def setUp(self):
        '''创建了一个 Board 实例来用于测试'''
        Board.objects.create(name='Django', description='Django board.')

    def test_board_topics_view_success_status_code(self):
        '''测试 Django 是否对于现有的 Board 返回 status code 200'''
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        '''测试 Django 是否对于不存在于数据库的 Board 返回 status code 404'''
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        '''测试 Django 是否使用了正确的视图函数去渲染 topics'''
        view = resolve('/boards/1/')
        self.assertEquals(view.func, board_topics)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))





class NewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        # 创建用于测试的 User 实例
        User.objects.create_user(username='john', email='john@doe.com', password='123')

    def test_new_topic_view_success_status_code(self):
        '''检查发给 view 的请求是否成功'''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        '''检查当 Board 不存在时 view 是否会抛出一个 404 的错误'''
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        '''检查是否正在使用正确的 view'''
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        '''确保导航能回到 topics 的列表'''
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        '''保证我们的 HTML 包含 csrf_token'''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        '''发送有效的数据并检查视图函数是否创建了 Topic 和 Post 实例'''
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data_empty_fields(self):
        ''' 类似于上一个测试，但是这次我们发送一些无效数据 '''
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):
        ''' 抓取上下文的表单实例，检查它是否是一个 NewTopicForm '''
        url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):
        ''' 确保数据无效的时候表单会显示错误 '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {'sdf':1})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

