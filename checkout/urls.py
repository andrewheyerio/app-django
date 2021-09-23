from django.urls import path, include

from .views import LinkAPIView, OrderAPIView

urlpatterns = [
    path('links/<str:code>', LinkAPIView.as_view()),
    path('orders/<str:code>', OrderAPIView.as_view()),

]
