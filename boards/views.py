from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic

# def home(request):
#     boards = Board.objects.all()
#     return render(request, 'home.html', {'boards': boards})

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


# def board_topics(request, pk):
#     board = get_object_or_404(Board, pk=pk)
#     # topics查询集中包含有replies属性
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     # 默认返回第一页的数据
#     page = request.GET.get('page', 1)
#     paginator = Paginator(queryset, 20)
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         topics = paginator.page(1)
#     except EmptyPage:
#         topics = paginator.page(paginator.num_pages)

#     return render(request, 'topics.html', {'board': board, 'topics': topics})


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board'] = self.board
        return context

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset



# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic': topic})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.topic.views += 1
        self.topic.save()
        context['topic'] = self.topic
        return context

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    form = NewTopicForm(request.POST or None)  # 传入空表单会当做是get方法而不生成form.errors
    if form.is_valid():  # 使用form在后端验证数据
        # 保存topic对象
        topic = form.save(commit=False)   # ToDo: 把功能移到models中
        topic.board = board
        topic.starter = request.user
        topic.save()
        # 创建post对象
        post = Post.objects.create(
            message = form.cleaned_data.get('message'),
            topic = topic,
            created_by=request.user,
        )
        return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    # 将topic和form传过去
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.topic = topic
        post.created_by = request.user
        post.save()
        return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        # 限定用户可以修改的post
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)



