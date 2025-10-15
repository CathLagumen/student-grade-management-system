
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicSubjectListView, UserViewSet, SubjectViewSet, GradeViewSet, SubjectDetailView, EnrollSubjectView, RemoveStudentFromSubjectView
from .views import UpdateStudentGradeView


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('public/subjects/', PublicSubjectListView.as_view(), name='public-subjects-list'),
    path('subjects/<int:pk>/details/', SubjectDetailView.as_view(), name='subject-detail'),
    path('subjects/<int:subject_id>/enroll/', EnrollSubjectView.as_view(), name='enroll-subject'),
    path('subjects/<int:subject_id>/remove/<int:student_id>/', RemoveStudentFromSubjectView.as_view(), name='remove-student'),
    path('subjects/<int:subject_id>/update-grade/<int:student_id>/', UpdateStudentGradeView.as_view(), name='update-grade'),



]
