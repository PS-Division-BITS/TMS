# This file will contain utility functions that are not strictly related to a single user types and other places
from transfers.constants import UserType, ApplicationsStatus, ThesisLocaleType, TransferType
from transfers.models import DeadlineModel, PS2TSTransfer, TS2PSTransfer
from transfers.constants import TransferType
from django.utils import timezone as datetime
from transfers.utils.student_utils import notify_ps2ts


def update_application(applicant, application_type, approved_by, status, comments):
    try:
        print('Hey??')
        print(application_type)
        if int(application_type) == TransferType.TS2PS.value:
            transfer_form = TS2PSTransfer.objects.get(applicant__user__username=applicant)
        else:
            transfer_form = PS2TSTransfer.objects.get(applicant__user__username=applicant)
        if approved_by == UserType.SUPERVISOR.value:
            transfer_form.is_supervisor_approved = int(status)
            transfer_form.comments_from_supervisor = comments
            if int(status) == ApplicationsStatus.APPROVED.value and int(application_type) == TransferType.PS2TS.value:
                notify_ps2ts(transfer_form,"hod")
        elif approved_by == UserType.HOD.value:
            transfer_form.is_hod_approved = int(status)
            transfer_form.comments_from_hod = comments
        elif approved_by == UserType.AD.value:
            transfer_form.is_ad_approved = int(status)
            transfer_form.comments_from_ad = comments
        transfer_form.save()
        return True
    except Exception as e:
        print('Error in shared_utils.update_application')
        print(e) # left for debugging
        return False

def clean_list(application_list):
    for data in application_list:
        try:
            if 'thesis_locale' in data:
                data['thesis_locale_alias'] = ThesisLocaleType._member_names_[data.pop('thesis_locale')]
            if 'is_supervisor_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_supervisor_approved')]
                data['status'] = status_alias
            elif 'is_hod_approved' in data:
                status_alias = ApplicationsStatus._member_names_[data.pop('is_hod_approved')]
                data['status'] = status_alias
        except Exception as e:
            print('error in shared_utils.clean_list')
            print(e) # left for debugging
    return application_list

def get_deadline_status(form_type):
    try:
        update_psd = DeadlineModel.objects.all().first()
    except:
        update_psd = DeadlineModel.objects.create()
    status = False
    if form_type == TransferType.PS2TS.value:
        if update_psd.is_active_PS2TS:
            if datetime.now() < update_psd.deadline_PS2TS:
                update_psd.is_active_PS2TS = True
                status = True
            else:
                update_psd.is_active_PS2TS = False
                status = False
        else:
            update_psd.is_active_PS2TS = False
            status = False
    else:
        if update_psd.is_active_TS2PS:
            if datetime.now() < update_psd.deadline_TS2PS:
                update_psd.is_active_TS2PS = True
                status = True
            else:
                update_psd.is_active_TS2PS = False
                status = False
        else:
            update_psd.is_active_TS2PS = False
            status = False
    update_psd.save()
    return status
