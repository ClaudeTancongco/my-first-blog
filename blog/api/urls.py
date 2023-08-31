from django.urls import path
from .views import blog


urlpatterns = [
    path('', blog.BlogListCreateView.as_view()),
    
] 