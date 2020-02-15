from django.urls import path
from django.conf.urls import url

from transfers.views import (redirect_views, student_views,
    hod_views, supervisor_views, assoc_dean_views)


urlpatterns = [
    path('login-redirect/', redirect_views.login_redirect_view),
    path('student/PS2TS/', student_views.PS2TSFormView.as_view()),
    path('student/TS2PS/', student_views.TS2PSFormView.as_view()),
    path('student/dashboard/', student_views.StudentDashboardView.as_view()),
    path('hod/home/', hod_views.HODHomeView.as_view()),
    path('supervisor/home/', supervisor_views.SupervisorHomeView.as_view()),
    path('validate_supervisor_email/', student_views.validate_supervisor_email),
    path('hod/get-hod-data/', hod_views.get_hod_data),
    path('assoc_dean/home/', assoc_dean_views.AssocDeanView.as_view()),
]