from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect

from transfers.constants import CampusType, UserType, TransferType
from transfers.models import PS2TSTransfer, UserProfile
from transfers.forms import PS2TSTransferForm, TS2PSTransferForm

from transfers.utils.student_utils import (
    get_application_status, notify_ps2ts, notify_ts2ps,
    get_branch_from_branch_code,
    get_authority_comments, validate_contact
)
from transfers.utils.shared_utils import get_deadline_status
import pandas as pd 

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from transfers.decorators import student_required

@method_decorator([login_required, student_required], name='dispatch')
class StudentDashboardView(generic.TemplateView):
    template_name = 'transfers/student_dashboard.html'
    context = {}

    def get(self, request, *args, **kwargs):
        # Status of application remains 0 until both
        # supervisor and hod approve the application
        current_userprofile = request.user.userprofile
        (application_type, has_applied, application_status,
            error) = get_application_status(current_userprofile)
        (comments_from_hod, comments_from_supervisor, 
            comments_from_ad) = get_authority_comments(current_userprofile)
        # for testing purposes
        deadline_status_ps2ts = get_deadline_status(TransferType.PS2TS.value)
        deadline_status_ts2ps = get_deadline_status(TransferType.TS2PS.value)
        self.context['application_type'] = application_type
        self.context['has_applied'] = has_applied
        self.context['application_status'] = application_status
        self.context['error'] = error
        self.context['comments_from_hod'] = comments_from_hod
        self.context['comments_from_supervisor'] = comments_from_supervisor
        self.context['comments_from_ad'] = comments_from_ad
        self.context['deadline_status_ps2ts']=1 if deadline_status_ps2ts else 0
        self.context['deadline_status_ts2ps']=1 if deadline_status_ts2ps else 0
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        current_userprofile = request.user.userprofile
        (application_type, has_applied, application_status,
            error) = get_application_status(current_userprofile)
        deadline_status_ps2ts = get_deadline_status(TransferType.PS2TS.value)
        deadline_status_ts2ps = get_deadline_status(TransferType.TS2PS.value)
        self.context['application_type'] = application_type
        self.context['has_applied'] = has_applied
        self.context['application_status'] = application_status
        self.context['error'] = error
        self.context['deadline_status_ps2ts']=1 if deadline_status_ps2ts else 0
        self.context['deadline_status_ts2ps']=1 if deadline_status_ts2ps else 0
        return render(request, self.template_name, self.context)

@method_decorator([login_required, student_required], name='dispatch')
class PS2TSFormView(generic.FormView):
    form_class = PS2TSTransferForm
    initial = {'key': 'value'}
    template_name = 'transfers/PS2TS.html'
    context = {}

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        # is supervisor email valid (present in DB)?
        invalid_supervisor_email = False
        invalid_contact = False
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form,
            'hod_email_list': hod_email_list,
            'invalid_supervisor_email': invalid_supervisor_email,
            'invalid_contact': invalid_contact,
        }
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if not get_deadline_status(TransferType.PS2TS.value):
            return redirect('/TMS/student/dashboard/')
        post = request.POST.copy()
        post['applicant'] = request.user.userprofile
        request.POST = post
        form = self.form_class(request.POST)
        # is supervisor email valid (present in DB)?
        invalid_supervisor_email = False
        contact = post['contact']
        invalid_contact = False
        if not validate_contact(contact):
            invalid_contact = True
        if form.is_valid() and not invalid_contact:
            email = form.cleaned_data.get('supervisor_email')
            supervisor_email_qs = UserProfile.objects.filter(
                user_type=UserType.SUPERVISOR.value, user__email=email)
            if supervisor_email_qs:
                current_user = request.user.userprofile
                current_user.contact = contact
                current_user.save()
                form.save()
                data=PS2TSTransfer.objects.filter(applicant = request.user.userprofile)[0]
                notify_ps2ts(data, "supervisor")
                return redirect('/TMS/student/dashboard/')
            else:
                invalid_supervisor_email = True
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form,
            'hod_email_list': hod_email_list,
            'invalid_supervisor_email': invalid_supervisor_email,
            'invalid_contact': invalid_contact,
        }
        return render(request, self.template_name, self.context)
        
@method_decorator([login_required, student_required], name='dispatch')
class TS2PSFormView(generic.FormView):
    form_class = TS2PSTransferForm
    initial = {'key': 'value'}
    template_name = 'transfers/TS2PS.html'
    context = {}

    def get(self, request, *args, **kwargs):
        invalid_contact = False
        form = self.form_class(initial=self.initial)
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form, 
            'hod_email_list': hod_email_list,
            'invalid_contact': invalid_contact,
        }
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if not get_deadline_status(TransferType.TS2PS.value):
            return redirect('/TMS/student/dashboard/')
        post = request.POST.copy()
        post['applicant'] = request.user.userprofile
        request.POST = post
        form = self.form_class(request.POST)
        contact = post['contact']
        invalid_contact = False
        if not validate_contact(contact):
            invalid_contact = True
        if form.is_valid() and not invalid_contact:
            current_user = request.user.userprofile
            current_user.contact = contact
            current_user.save()
            form.save()
            notify_ts2ps(request)
            return redirect('/TMS/student/dashboard/')
        hod_file = pd.read_csv('hod_list.csv')
        hod_1 = hod_file[(hod_file["Campus"]==request.user.userprofile.campus) & ((hod_file["Department"]==request.user.username[4:6]) | (hod_file["Department"]==request.user.username[6:8]))]
        hod_email_list = hod_1['Email'].tolist()
        self.context = {
            'student_name': request.user.get_full_name(),
            'student_ID': request.user.username,
            'student_branch': get_branch_from_branch_code(request.user.username[4:6])+get_branch_from_branch_code(request.user.username[6:8]),
            'contact': request.user.userprofile.contact,
            'form': form, 
            'hod_email_list': hod_email_list,
            'invalid_contact': invalid_contact,
        }
        return render(request, self.template_name, self.context)


def validate_supervisor_email(request):
    email = request.GET.get('email', None)
    supervisor_email_list = UserProfile.objects.filter(
        user_type=UserType.SUPERVISOR.value, user__email=email
    )
    name = ''
    campus = ''
    is_valid = False
    if supervisor_email_list:
        is_valid = True
        name = supervisor_email_list[0].user.get_full_name()
        campus = supervisor_email_list[0].campus
        if campus == CampusType.GOA.value:
            campus = "BITS Pilani, Goa Campus"
        elif campus == CampusType.HYD.value:
            campus = "BITS Pilani, Hyderabad Campus"
        elif campus == CampusType.PILANI.value:
            campus = "BITS Pilani, Pilani Campus"
    data = {
        'is_valid': is_valid,
        'name': name,
        'campus': campus
    }
    return JsonResponse(data)
