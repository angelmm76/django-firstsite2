from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth import views, authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from .models import BlogPost, Comment, UserProfile
from .forms import SignupForm, EditForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from .serializers import UserSerializer, BlogPostSerializer, CommentSerializer

from reportlab.pdfgen import canvas

import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def signup(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form = SignupForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(request.POST["password1"])
            new_user.save()
            # g = Group.objects.get(name='BlogUser')
            # g.user_set.add(new_user)
            # user = authenticate(username=username, password=password)
            new_user = authenticate(username=request.POST['username'], 
                password=request.POST['password1'])
            login(request, new_user)
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            return render(request, "blog/signup.html", {'form': form, })
    if request.method == 'GET':
        # form = UserCreationForm()
        form = SignupForm()
        return render(request, "blog/signup.html", {'form': form, })

class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    queryset = BlogPost.objects.order_by('-pub_date')[:5]
    
    # def get_queryset(self):
	# 	return BlogPost.objects.order_by('-pub_date')[:5]
	# latest_post_list = BlogPost.objects.order_by('-pub_date')[:5]
	# context = {'latest_post_list': latest_post_list}
	# return render(request, 'blog/index.html', context)

class PageIndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    queryset = BlogPost.objects.all().order_by('-pub_date')
    paginate_by = 5

    # def get_queryset(self):
    #     item = 5 * (int(self.kwargs['page']) - 1)
    #     return BlogPost.objects.all().order_by('-pub_date')
        # return BlogPost.objects.order_by('-pub_date')[item:item+5]

class DetailView(generic.DetailView):
    model = BlogPost
    template_name = 'blog/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        bp = super(DetailView, self).get_object()
        comments = Comment.objects.filter(blogpost_id=bp.id)
        comments = comments.order_by('-created')[:5]
        context['comments_list'] = comments
        return context

# def detail(request, blogpost_id):
#     post = get_object_or_404(BlogPost, pk=blogpost_id)
#     return render(request, 'blog/detail.html', {'post': post})

@login_required(login_url='blog:login_view')
def comment(request, pk):
    if request.method == 'GET':
        bp = get_object_or_404(BlogPost, pk=pk)
        return render(request, 'blog/comment.html', {'blogpost': bp})
    if request.method == 'POST':
        try:
            co = request.POST['comment']
            bp = get_object_or_404(BlogPost, pk=pk)
            user = request.user
            comment = Comment(blogpost=bp, user=user, comment_content=co,
                created=timezone.now())
        except (KeyError, Comment.DoesNotExist):
            # Redisplay the new comment form.
            return render(request, 'blog/pk/comment.html', {
                'error_message': "Error :(",
            })
        else:
            comment.save()
            return HttpResponseRedirect(reverse('blog:detail', args=(pk,)))

# def comment(request, blogpost_id):
#    return HttpResponse("You're commenting on post %s." % blogpost_id)

@login_required(login_url='blog:login_view')
def newpost(request):
    if request.method == 'GET':
	    return render(request, 'blog/newpost.html')
    if request.method == 'POST':
        try:
            subject = request.POST['subject']
            content = request.POST['content']
            author = request.user
            image = request.FILES.get('image', None)
            #mage = request.FILES['image']
            # image = None
            bp = BlogPost(blogpost_title=subject, blogpost_content=content, 
                author= author, image=image, pub_date=timezone.now())
        except (KeyError, BlogPost.DoesNotExist):
            # Redisplay the new post form.
            return render(request, 'blog/newpost.html', {
                'error_message': "Error :( " + str(KeyError) +
                 str(request.FILES.keys()),
            })
        else:
            if len(subject)!=0 and len(content)!=0: 
                bp.save()
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                # return HttpResponseRedirect('/blog/%s' % str(bp.id))
                return HttpResponseRedirect(reverse('blog:detail', args=(bp.id,)))
            else:
                return render(request, 'blog/newpost.html', {
                'error_message': "The post must have title and content", })


@login_required(login_url='blog:login_view')
def edit(request, pk):
    bp = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'GET':
        form = EditForm(request.POST, instance=bp)
        return render(request, "blog/edit.html", {'bp': bp, 'form': form, })
    if request.method == 'POST':
        form = EditForm(request.POST, instance=bp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blog:detail', args=(bp.id,)))
        # try:
        #     subject = request.POST['subject']
        #     content = request.POST['content']
        #     author = request.user
        #     image = request.FILES['image']
        #     bp = BlogPost(blogpost_title=subject, blogpost_content=content, 
        #         author= author, image=image, pub_date=timezone.now())
        # except (KeyError, BlogPost.DoesNotExist):
        #     # Redisplay the edit post form.
        #     bp = get_object_or_404(BlogPost, pk=pk)
        #     return render(request, 'blog/edit.html', {'bp': bp, 
        #         'error_message': "Error :(" + str(KeyError) +
        #          str(request.FILES.keys()),
        #     })
        else:
            bp.save()
            return HttpResponseRedirect(reverse('blog:detail', args=(bp.id,)))

class EditView(generic.edit.UpdateView):
    model = BlogPost
    fields = ['blogpost_title', 'blogpost_content', 'image']
    template_name = 'blog/edit.html'

def pdf(request, pk):
    bp = get_object_or_404(BlogPost, pk=pk)
    filename = str(pk) + '.pdf'
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    # Open pdf in browser
    # response['Content-Disposition'] = 'filename=' + filename
    # Save file pop-up
    response['Content-Disposition'] = 'attachment; filename=' + filename
    # response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 750, "First Site Blog")
    p.drawString(100, 700, bp.blogpost_title)
    p.drawString(100, 670, bp.blogpost_content)
    if bp.image:
        p.drawImage(bp.image.path, 100, 550, width=100, height=100, mask=None)
    p.drawString(100, 500, "By " + str(bp.author) + ", " + str(bp.pub_date))

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

def contact(request):
    if request.method == 'GET':
        return render(request, 'blog/contact.html')
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        from_email = request.POST.get('from_email', '')

        if subject and message and from_email:
            try:
                send_mail(subject, message, from_email, ['angelmm_hup@yahoo.es'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            # In reality we'd use a form class
            # to get proper validation errors.
            return HttpResponse('Make sure all fields are entered and valid.')

# def archive(request):
#     return render(request, 'blog/archive.html')

class ArchiveIndexView(generic.ListView):
    template_name = 'blog/archive.html'
    context_object_name = 'month_list'
    pubdates = [(p.pub_date.year, p.pub_date.month, p.pub_date.strftime("%B")) 
                for p in BlogPost.objects.all()]
    #queryset = list(set(pubdates))
    queryset = sorted(set(pubdates))

def archive_detail(request, year, month):
    return HttpResponse("Year %s, month %s posts." % (year, month))

class ArchiveDetailView(generic.ListView):
    template_name = 'blog/archive_detail.html'
    context_object_name = 'post_list'
    #queryset = BlogPost.objects.order_by('-pub_date')[:5]
    
    def get_queryset(self):
        posts = BlogPost.objects.filter(pub_date__month =self.kwargs['month']).filter(
            pub_date__year =self.kwargs['year'])
        return posts.order_by('-pub_date')

def about(request):
    return render(request, 'blog/about.html')

def login_view(request):
    if request.method == 'GET':
        return render(request, 'blog/login-view.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        req = request.META['HTTP_REFERER']    

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('blog:index'))
        else:
            error = "Your username and password didn't match. Please try again."
            return render(request, 'blog/login-view.html', {'error': error})

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse('blog:index'))

# API REST
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

# APIPI REST
#@csrf_exempt
@api_view(['GET', 'POST'])
def blogpost_list(request):
    """
    List all blogposts, or create a new blogpost
    """
    if request.method == 'GET':
        blogposts = BlogPost.objects.all()
        serializer = BlogPostSerializer(blogposts, many=True)
        return Response(serializer.data)
        #return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        # data = JSONParser().parse(request)
        # serializer = BlogPostSerializer(data=data)
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            #return JsonResponse(serializer.data, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #return JsonResponse(serializer.errors, status=400)

#@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def blogpost_detail(request, pk):
    """
    Retrieve, update or delete a blogpost
    """
    try:
        bp = BlogPost.objects.get(pk=pk)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        #return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = BlogPostSerializer(bp)
        return Response(serializer.data)
        #return JsonResponse(serializer.data)

    elif request.method == 'PUT':
    #     data = JSONParser().parse(request)
    #     serializer = BlogPostSerializer(bp, data=data)
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            #return JsonResponse(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        bp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        #return HttpResponse(status=204)
