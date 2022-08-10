from django.contrib import admin


from .models import Profile, Post, LikePost, FollowersCount

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'id_user', 'user']


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'caption', 'no_of_likes', 'created_at']


class LikePostAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_id', 'username']


class FollowersCountAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'user']



admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(LikePost, LikePostAdmin)
admin.site.register(FollowersCount, FollowersCountAdmin)