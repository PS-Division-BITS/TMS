from django.urls import path
from django.conf.urls import url

from transfers.views import (redirect_views, student_views,
    hod_views, supervisor_views, assoc_dean_views, psd_views, fillUser, export_views)


# view related urls
urlpatterns = [
    # student urls
    path('login-redirect/', redirect_views.login_redirect_view),
    path('student/PS2TS/', student_views.PS2TSFormView.as_view()),
    path('student/TS2PS/', student_views.TS2PSFormView.as_view()),
    path('student/dashboard/', student_views.StudentDashboardView.as_view()),
    path('validate_supervisor_email/', student_views.validate_supervisor_email),
    # hod urls
    path('hod/home/', hod_views.HODHomeView.as_view()),
    path('hod/get-hod-data/', hod_views.get_hod_data),
    path('hod/approve-transfer-request/', hod_views.approve_transfer_request),
    # supervisor urls
    path('supervisor/home/', supervisor_views.SupervisorHomeView.as_view()),
    path('supervisor/get-supervisor-data/', supervisor_views.get_supervisor_data),
    path('supervisor/approve-transfer-request/', supervisor_views.approve_transfer_request),
    # AD urls
    path('assoc-dean/home/', assoc_dean_views.AssocDeanHomeView.as_view()),
    path('assoc-dean/reject-transfer-request/',assoc_dean_views.reject_transfer_request),
    # psd urls
    path('psd/dashboard/', psd_views.PSDview.as_view()),
    path('psd/get-PSD-data/', psd_views.get_PSD_data),
    # FIXME: These two views should be inside psd_views
    path('psd/populate-data/',fillUser.fill),
    path('psd/download-transfers/',export_views.exp),
    # Show deadline in header
    path('get-deadline', psd_views.get_PSD_data),
]

# data related urls (usually requested by ajax calls in already rendered templates)
urlpatterns += [
    # hod urls
    path('data/get-application-data/', redirect_views.application_data_redirect_view),
    path('data/approve-transfer-request/', redirect_views.approve_transfer_request_redirect_view),
    path('data/export-hod/',hod_views.export_hod, name='hodExp'),
    # AD urls
    path('data/assoc-dean/get-transfer-lists/type/<type>/', assoc_dean_views.AssocDeanLisApplicationstView.as_view()),
    # psd urls
    path('data/psd/get-data/', psd_views.get_form_data),
    path('data/reject-transfer-request/', redirect_views.reject_transfer_request_redirect_view),
]
