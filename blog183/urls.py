from django.conf.urls import url, include
from django.conf import settings

from . import views

app_name = 'blog'
urlpatterns = [
    # url('^', include('django.contrib.auth.urls')),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    # url(r'^$', views.index, name='index'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^page/(?P<page>[0-9]+)/$', views.PageIndexView.as_view(), name='page'),
    # url(r'^(?P<blogpost_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/comment/$', views.comment, name='comment'),
    # url(r'^(?P<pk>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<pk>[0-9]+)/edit/$', views.EditView.as_view(), name='edit'),
    url(r'^(?P<pk>[0-9]+)/pdf/$', views.pdf, name='pdf'),
    # url(r'^(?P<blogpost_id>[0-9]+)/comment/$', views.comment, name='comment'),
    url(r'^newpost/$', views.newpost, name='newpost'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about/$', views.about, name='about'),
    url(r'^archive/$', views.ArchiveIndexView.as_view(), name='archive'),
    #url(r'^archive/$', views.archive, name='archive'),
    url(r'^archive/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.ArchiveDetailView.as_view(),
         name='archive_detail'),
    # url(r'^archive/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', views.archive_detail,
    #      name='archive_detail'),
]