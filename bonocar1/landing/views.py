from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Comment
from .forms import BlogPostForm, CommentForm
from django.contrib.auth import logout
from django.contrib import messages


# Create your views here.
def index(request):
    print("Index View is rendering")
    return render(request, 'landing/index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'landing/signup.html',{'form':form})

@login_required
def blog_list(request):
    query = request.GET.get('q')
    if query:
        blogs = BlogPost.objects.filter(title__icontains=query)
    else:
        blogs = BlogPost.objects.all()
    return render(request, 'landing/blog_list.html', {'blogs': blogs})
@login_required
def blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'landing/blog_form.html', {'form': form})

@login_required
def blog_update(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    if blog.author != request.user:
        return redirect('blog_list')
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm(instance=blog)
    return render(request, 'landing/blog_form.html', {'form': form})

@login_required
def blog_delete(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    if blog.author == request.user:
        blog.delete()
    return redirect('blog_list')

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.all() #gets all comments for this post
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('blog_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'landing/blog_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def like_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('blog_detail', pk=pk)


# def custom_logout(request):
#     logout(request)
#     messages.success(request, "You have been logged out successfully.")
#     return redirect('index')