from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


# Create your views here.
def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """显示所有的主题"""
    local_topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': local_topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """获取单个主题及其所有的条目"""
    local_topic = Topic.objects.get(id=topic_id)
    # 确认请求的主题属于当前用户
    if not check_topic_owner(request, local_topic):
        raise Http404

    entries = local_topic.entry_set.order_by('-date_added')
    context = {'topic': local_topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        # 未提交数据，创建一个新表单
        form = TopicForm()
    else:
        # POST提交的数据，对数据进行处理
        form = TopicForm(request.POST)
        if form.is_valid():
            local_new_topic = form.save(commit=False)
            local_new_topic.owner = request.user
            local_new_topic.save()
            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """在特定的主题中添加新条目"""
    local_topic = Topic.objects.get(id=topic_id)
    # 添加新条目之前先检查此条目是否属于该用户主题下的
    if not check_topic_owner(request, local_topic):
        raise Http404

    if request.method != 'POST':
        # 未提交数据，创建一个空表单
        form = EntryForm()
    else:
        # POST提交的数据，对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            local_new_entry = form.save(commit=False)
            local_new_entry.topic = local_topic
            local_new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))

    context = {'topic': local_topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """编辑既有条目"""
    local_entry = Entry.objects.get(id=entry_id)
    local_topic = local_entry.topic
    # 编辑之前先检查此条目是否属于该用户主题下的
    if not check_topic_owner(request, local_topic):
        raise Http404

    if request.method != 'POST':
        # 初次请求，使用当前条目填充表单
        form = EntryForm(instance=local_entry)
    else:
        # POST提交的数据，对数据进行处理
        form = EntryForm(instance=local_entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[local_topic.id]))

    context = {'entry': local_entry, 'topic': local_topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


def check_topic_owner(request, p_topic):
    return request.user == p_topic.owner
