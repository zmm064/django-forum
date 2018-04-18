from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect;
from django.db.models import Count
from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm

def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # topics查询集中包含有replies属性
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'topics.html', {'board': board, 'topics': topics})

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

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
