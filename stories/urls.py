from django.urls import path
from .views import story_test, story_list, add_story, \
    story_detail, add_comment, upload_image, markdown_to_html,\
    test_ace_editor, unpublish_story, publish_story, search

urlpatterns = [
    path('story_test/<int:id>/', story_test, name='story_test'),
    path('story_list/', story_list, name='story_list'),
    path('add_story/', add_story, name='add_story'),
    path('unpublish_story/<int:story_id>/', unpublish_story, name='unpublish_story'),
    path('publish_story/<int:story_id>/', publish_story, name='publish_story'),
    path('edit_story/<int:story_id>/', add_story, name='edit_story'),  # edit existing story
    path('story_detail/<int:story_id>/', story_detail, name='story_detail'),  # view existing story
    path('story_detail/<int:story_id>/add_comment/', add_comment, name='add_comment'),
    path('upload_image/', upload_image, name='upload_image'),
    path('markdown_to_html/', markdown_to_html, name='markdown_to_html'),
    path('test_ace_editor/', test_ace_editor, name='test_ace_editor'),
    path('search/', search, name='search')
]