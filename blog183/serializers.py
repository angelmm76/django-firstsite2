from django.contrib.auth.models import User
from .models import BlogPost, Comment, UserProfile
from rest_framework import serializers

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     bps = serializers.HyperlinkedRelatedField(view_name="blog:blogpost-list", 
#          many=True, read_only=True)

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'bps')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'date_joined')


class BlogPostSerializer(serializers.HyperlinkedModelSerializer):
    #authorname = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name="blog:user-detail", 
         read_only=True)

    class Meta:
        model = BlogPost
        fields = ('blogpost_title', 'blogpost_content', 'pub_date', 'author')
        # depth = 1


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name="blog:user-detail", 
         read_only=True)
    blogpost = serializers.HyperlinkedRelatedField(view_name="blog:blogpost-detail", 
         read_only=True)

    class Meta:
        model = Comment
        fields = ('user', 'blogpost', 'comment_content', 'created')
        # depth = 1