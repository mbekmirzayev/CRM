import csv

from django.contrib import admin
from django.contrib.admin import AdminSite, TabularInline
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.http import HttpResponse

from apps.models import Enrollment
from apps.models import User, Category, Course, Group
from apps.models.payments import Payment


class CRMAdminSite(AdminSite):
    site_header = "Education CRM Dashboard"

    def each_context(self, request):
        context = super().each_context(request)
        context['total_students'] = User.objects.filter(role='student').count()
        context['total_courses'] = Course.objects.count()
        context['total_revenue'] = Payment.objects.filter(
            status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return context


class EnrollmentStatusChart(ModelAdmin):
    title = "Enrollment Status"
    queryset = Enrollment.objects.all()
    labels = 'status'
    values = 'id'


# users.py
@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'role', 'first_name', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Enrollment)
class EnrollmentModelAdmin(ModelAdmin):
    list_display = ('group', 'student', 'created_at')
    list_filter = ('group',)
    actions = ['mark_completed', 'export_as_csv']

    @admin.action(description="Mark selected enrollments as completed")
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)


class EnrollmentInline(TabularInline):
    model = Enrollment
    extra = 0
    fields = ('student', 'group')


class PaymentInline(TabularInline):
    model = Payment
    extra = 0
    fields = ('student', 'amount', 'status')

@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ("id", "status", "organization", "course", 'name', 'start_time', 'end_time')
    inlines = [EnrollmentInline]

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ('title', 'students_count', 'revenue')
    search_fields = ('title',)
    inlines = [PaymentInline]

    @admin.display(description="Students count")
    def students_count(self, obj):
        return Enrollment.objects.filter(course=obj).count()

    @admin.display(description="Revenue")
    def revenue(self, obj):
        from django.db.models import Sum
        return Payment.objects.filter(
            course=obj, status='paid'
        ).aggregate(Sum('amount'))['amount__sum'] or 0


@admin.register(Payment)
class PaymentModelAdmin(ModelAdmin):
    list_display = ('student', 'course', 'amount', 'status')
    actions = ['mark_paid', 'export_as_csv']

    @admin.action(description="Mark selected payments as paid")
    def mark_paid(self, request, queryset):
        queryset.update(status='paid')


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename={meta.model_name}.csv'
        )

        writer = csv.writer(response)
        writer.writerow(field_names)

        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected as CSV"


admin.site.unregister(Group)
