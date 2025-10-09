from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Subject, Grade


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_student', 'is_staff')
    list_filter = ('is_admin', 'is_student', 'is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('User Type', {'fields': ('is_admin', 'is_student')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_admin', 'is_student'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'grade', 'semester', 'school_year', 'created_at')
    list_filter = ('subject', 'semester', 'school_year', 'created_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'subject__name')
    
    fieldsets = (
        ('Student and Subject', {'fields': ('student', 'subject')}),
        ('Grade Information', {'fields': ('grade', 'semester', 'school_year', 'remarks')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(User, UserAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Grade, GradeAdmin)