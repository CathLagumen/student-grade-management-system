from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .models import User, Subject, Grade
from .serializers import UserSerializer, SubjectSerializer, GradeSerializer
from .permission import IsAdminOrReadOnly

class RemoveStudentFromSubjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, subject_id, student_id):
        """
        Allows an admin to remove a student from a subject.
        Only if the student has not yet received a grade.
        """
        # ✅ Only admins can remove students
        if not request.user.is_admin:
            return Response(
                {"error": "Only admins can remove students from subjects."},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Check if subject exists
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if student exists
        try:
            student = User.objects.get(pk=student_id, is_student=True)
        except User.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check enrollment
        try:
            grade_record = Grade.objects.get(subject=subject, student=student)
        except Grade.DoesNotExist:
            return Response(
                {"error": "This student is not enrolled in the subject."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Prevent removal if grade already exists
        if grade_record.grade is not None:
            return Response(
                {"error": "Cannot remove student — they already have a grade."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Safe to remove
        grade_record.delete()
        return Response(
            {"message": f"Student {student.get_full_name()} was successfully removed from {subject.name}."},
            status=status.HTTP_200_OK
        )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        subject = self.get_object()
        if Grade.objects.filter(subject=subject).exists():
            return Response(
                {"error": "Cannot delete subject with associated grades."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubjectDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        If student -> show their grade for the subject
        If admin -> show all students and their grades (not paginated)
        """
        try:
            subject = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        # If admin: show all students with their grades
        if request.user.is_admin:
            grades = Grade.objects.filter(subject=subject).select_related('student')
            data = [
                {
                    "student": f"{grade.student.first_name} {grade.student.last_name}",
                    "email": grade.student.email,
                    "grade": grade.grade,
                    "remarks": grade.remarks,
                }
                for grade in grades
            ]
            return Response({
                "subject": subject.name,
                "students": data,
                "total_students": len(data)
            })

        # If student: show their own grade
        elif request.user.is_student:
            grade = Grade.objects.filter(subject=subject, student=request.user).first()
            if grade:
                return Response({
                    "subject": subject.name,
                    "grade": grade.grade,
                    "remarks": grade.remarks,
                })
            else:
                return Response({
                    "subject": subject.name,
                    "message": "You are not enrolled in this subject."
                }, status=status.HTTP_404_NOT_FOUND)

        # Otherwise (not admin or student)
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)


class PublicSubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

class UpdateStudentGradeView(APIView):
    """
    Allows an admin to update/change a student's grade for a specific subject.
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, subject_id, student_id):
        # ✅ Only admins can perform this action
        if not request.user.is_admin:
            return Response(
                {"error": "Only admins can update grades."},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ Get the subject
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Get the student
        try:
            student = User.objects.get(pk=student_id, is_student=True)
        except User.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Find grade record
        try:
            grade_record = Grade.objects.get(subject=subject, student=student)
        except Grade.DoesNotExist:
            return Response(
                {"error": "Student is not enrolled in this subject."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Validate the new grade
        new_grade = request.data.get("grade")
        if new_grade is None:
            return Response({"error": "Grade value is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_grade = float(new_grade)
        except ValueError:
            return Response({"error": "Grade must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= new_grade <= 100):
            return Response({"error": "Grade must be between 0 and 100."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Update and save
        grade_record.grade = new_grade
        grade_record.save()

        return Response(
            {"message": f"Updated {student.first_name}'s grade in {subject.name} to {new_grade}."},
            status=status.HTTP_200_OK
        )

class EnrollSubjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, subject_id):
        """
        Allows a student to enroll in a subject.
        Prevents duplicate enrollment.
        """
        # ✅ Only students can enroll
        if not request.user.is_student:
            return Response({"error": "Only students can enroll in subjects."}, status=status.HTTP_403_FORBIDDEN)

        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if already enrolled
        existing_enrollment = Grade.objects.filter(student=request.user, subject=subject).exists()
        if existing_enrollment:
            return Response({"error": "You are already enrolled in this subject."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create new enrollment with blank grade
        enrollment = Grade.objects.create(student=request.user, subject=subject)
        return Response({
            "message": f"Successfully enrolled in {subject.name}.",
            "subject": subject.name,
            "student": request.user.get_full_name(),
            "grade": enrollment.grade  # Should be null/None initially
        }, status=status.HTTP_201_CREATED)
    

