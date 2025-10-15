from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SubjectViewSet, GradeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
