from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect;
from .models import Board, Topic, Post
from .forms import NewTopicForm

def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board': board})

def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()
    form = NewTopicForm(request.POST or None)  # 传入空表单会当做是get方法而不生成form.errors
    if form.is_valid():  # 使用form在后端验证数据
        # 保存topic对象
        topic = form.save(commit=False)   # ToDo: 把功能移到models中
        topic.board = board
        topic.starter = user
        topic.save()
        # 创建post对象
        post = Post.objects.create(
            message = form.cleaned_data.get('message'),
            topic = topic,
            created_by = user,
        )
        return redirect(board)
    return render(request, 'new_topic.html', {'board': board, 'form': form})


