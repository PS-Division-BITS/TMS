from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic

from transfers.constants import UserType, CampusType, ApplicationsStatus, TransferType
from transfers.models import PS2TSTransfer, UserProfile, TS2PSTransfer
from transfers.utils.shared_utils import update_application, clean_list

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from transfers.decorators import hod_required
from django.http import HttpResponse
from transfers.tools.export import getFileHod

@method_decorator([login_required, hod_required], name='dispatch')
class HODHomeView(generic.TemplateView):
    template_name = 'transfers/common.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name)


@login_required
@hod_required
def get_hod_data(request):
    response = {}
    try:
        current_user = request.user
        current_user_alias = 'Head Of Department'
        campus_alias = CampusType._member_names_[current_user.userprofile.campus]
        application_type = int(request.GET.get('application_type'))
        if application_type == TransferType.TS2PS.value:
            # applications where approval is pending
            pending_applications_qs = TS2PSTransfer.objects.filter(
                hod_email = current_user.email,
                is_hod_approved = ApplicationsStatus.PENDING.value,
            ).values(
                'applicant__user__username',
                'applicant__user__first_name', 'applicant__user__last_name',
                'cgpa', 'reason_for_transfer', 'name_of_org',
                'is_hod_approved',
            )
            pending_applications_list = list(pending_applications_qs)
            pending_applications_list = clean_list(pending_applications_list)
            # approved applications
            approved_applications_qs = TS2PSTransfer.objects.filter(
                hod_email = current_user.email,
                is_hod_approved__gt = ApplicationsStatus.PENDING.value,
            ).values(
                'applicant__user__username',
                'applicant__user__first_name', 'applicant__user__last_name',
                'cgpa', 'name_of_org', 'reason_for_transfer',
                'is_hod_approved',
            )
            approved_applications_list = list(approved_applications_qs)
            approved_applications_list = clean_list(approved_applications_list)
            response['error'] = False
            response['message'] = 'success'
            response['data'] = {}
            response['data']['user'] = {
                'username': current_user.username,
                'designation': current_user_alias,
                'campus': campus_alias,
                'email': current_user.email
            }
            attributes_for_display = [
                {'display': 'Student ID', 'prop':'applicant__user__username'},
                {'display':'Student First Name','prop':'applicant__user__first_name'},
                {'display':'Student Last Name','prop':'applicant__user__last_name'},
                {'display':'CGPA','prop':'cgpa'},
                {'display':'Transfer reason','prop':'reason_for_transfer'},
                {'display':'Organisation','prop':'name_of_org'},
                {'display':'Status', 'prop':'status'}
            ]
            response['data']['student_pending_attributes'] = attributes_for_display[:-1]
            response['data']['student_approved_attributes'] = attributes_for_display
            response['data']['data_pending'] = [a for a in pending_applications_list]
            response['data']['data_approved']= [a for a in approved_applications_list]
        else:
            # applications where approval is pending
            pending_applications_qs = PS2TSTransfer.objects.filter(
                hod_email = current_user.email,
                is_supervisor_approved__gt = ApplicationsStatus.PENDING.value,
                is_hod_approved = ApplicationsStatus.PENDING.value,
            ).values(
                'applicant__user__username',
                'applicant__user__first_name', 'applicant__user__last_name',
                'cgpa', 'thesis_locale', 'supervisor_email',
                'thesis_subject', 'name_of_org', 'expected_deliverables',
                'is_hod_approved', 'comments_from_supervisor',
            ).order_by('applicant')
            # updating with supervisor details
            supervisor_emails = PS2TSTransfer.objects.filter(
                hod_email = current_user.email,
                is_supervisor_approved__gt = ApplicationsStatus.PENDING.value,
                is_hod_approved = ApplicationsStatus.PENDING.value,
            ).values('supervisor_email',
            ).order_by('applicant')
            supervisor_details = []
            print(supervisor_emails)
            for supervisor_email in list(supervisor_emails):
                print(supervisor_email)
                obj = User.objects.get(
                    email=supervisor_email['supervisor_email'],
                    userprofile__user_type=UserType.SUPERVISOR.value,
                )
                supervisor_details.append({'supervisor_name': obj.get_full_name()})
            pending_applications_list = list(pending_applications_qs)
            for x, y in zip(pending_applications_list, supervisor_details):
                x.update(y)
            pending_applications_list = clean_list(pending_applications_list)
            # approved applications
            approved_applications_qs = PS2TSTransfer.objects.filter(
                hod_email = current_user.email,
                is_supervisor_approved__gt = ApplicationsStatus.PENDING.value,
                is_hod_approved__gt = ApplicationsStatus.PENDING.value,
            ).values(
                'applicant__user__username',
                'applicant__user__first_name', 'applicant__user__last_name',
                'cgpa', 'thesis_locale', 'supervisor_email',
                'thesis_subject', 'name_of_org', 'expected_deliverables',
                'is_hod_approved', 'comments_from_supervisor',
            ).order_by('applicant')
            # updating with supervisor wmail
            supervisor_emails = PS2TSTransfer.objects.filter(
                hod_email = current_user.email,
                is_supervisor_approved__gt = ApplicationsStatus.PENDING.value,
                is_hod_approved__gt = ApplicationsStatus.PENDING.value,
            ).values('supervisor_email',
            ).order_by('applicant')
            supervisor_details = []
            for supervisor_email in supervisor_emails:
                obj = User.objects.get(
                    email=supervisor_email['supervisor_email'],
                    userprofile__user_type=UserType.SUPERVISOR.value,
                )
                supervisor_details.append({'supervisor_name': obj.get_full_name()})
            approved_applications_list = list(approved_applications_qs)
            for x, y in zip(pending_applications_list, supervisor_details):
                x.update(y)
            approved_applications_list = clean_list(approved_applications_list)
            response['error'] = False
            response['message'] = 'success'
            response['data'] = {}
            response['data']['user'] = {
                'username': current_user.username,
                'designation': current_user_alias,
                'campus': campus_alias,
                'email': current_user.email
            }
            attributes_for_display = [
                {'display': 'Student ID', 'prop':'applicant__user__username'},
                {'display':'Student First Name','prop':'applicant__user__first_name'},
                {'display':'Student Last Name','prop':'applicant__user__last_name'},
                {'display':'CGPA','prop':'cgpa'},
                {'display':'Supervisor Name', 'prop': 'supervisor_name'},
                {'display':'Supervisor Email', 'prop':'supervisor_email'},
                {'display':'Thesis Location','prop':'thesis_locale_alias'},
                {'display':'Thesis Subject','prop':'thesis_subject'},
                {'display':'Organisation','prop':'name_of_org'},
                {'display':'Expected Deliverables','prop':'expected_deliverables'},
                {'display':'Supervisor comments','prop':'comments_from_supervisor'},
                {'display':'Status', 'prop':'status'}
            ]
            response['data']['student_pending_attributes'] = attributes_for_display[:-1]
            response['data']['student_approved_attributes'] = attributes_for_display
            response['data']['data_pending'] = [a for a in pending_applications_list]
            response['data']['data_approved']= [a for a in approved_applications_list]
    except Exception as e:
        print(e)
        response['data'] = {
            'username': current_user.username,
            'designation': current_user_alias,
            'campus': campus_alias,
            'email': current_user.email
        }
        response['error'] = True
        response['message'] = 'error'
    finally:
        return JsonResponse(response, safe=False)


def approve_transfer_request(request):
    applicant = request.GET['student_username']
    status = request.GET['status']
    approved_by = request.user.userprofile.user_type
    application_type = int(request.GET.get('application_type'))
    comments = request.GET.get('comments')
    saved = update_application(applicant, application_type, approved_by, status, comments)
    response = {}
    if saved:
        response['error'] = False
        response['message'] = 'Application approved.'
    else:
        response['error'] = True
        response['message'] = 'Failed to approve application!'
    return JsonResponse(response, safe=False)

@login_required
@hod_required
def export_hod(request):
    if request.method=='GET':
        if request.user.is_superuser or request.user.userprofile.user_type==2:
            print(request.GET['type'])
            response=getFileHod(request, int(request.GET['type']))
        else:
            response=HttpResponse("You don't have acces to this page")
        return response

