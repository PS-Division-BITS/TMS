from django.core.mail import send_mail

from .constants import UserType, TransferType
from .models import PS2TSTransfer, TS2PSTransfer


def get_application_status(userprofile):
    status = None
    alias = None
    has_applied = None
    error = None
    try:
        ps2ts = PS2TSTransfer.objects.filter(applicant=userprofile)
        ts2ps = TS2PSTransfer.objects.filter(applicant=userprofile)
        if ps2ts.count() == 1:
            alias = TransferType.PS2TS.value
            has_applied = 1
            error = 0
            status = _get_ps2ts_application_status(userprofile, ps2ts)
        elif ts2ps.count() == 1:
            alias = TransferType.TS2PS.value
            has_applied = 1
            status = _get_ts2ps_application_status(userprofile. ts2ps)
            error = 0
        else:
            status = -1
            has_applied = 0
            error = 0
    except Exception as e:
        status = -1
        has_applied = 0
        error = 1
    
    return (alias, has_applied, status, error)

def _get_ps2ts_application_status(userprofile, ps2ts):
    application = ps2ts[0]
    # until both supervisor and hod approves the application, the status remains 0
    if not application.is_supervisor_approved or not application.is_hod_approved:
        return 0
    else:
        return 1

def _get_ts2ps_application_status(userprofile, ts2ps):
    application = ts2ps[0]
    if not application.is_hod_approved:
        return 0
    else:
        return 1

def notify_ps2ts(request):
    body = ""
    data=PS2TSTransfer.objects.filter(applicant = request.user.userprofile)[0]
    print(str(data.hod_email))
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nThesis Locale: " + data.get_thesis_locale_display()+
    "\nThesis Subject: " + data.thesis_subject+
    "\nOrganization Name: " + data.name_of_org+
    "\nExpected Outcome: " + data.expected_deliverables)
    mail(data,request,body)

def notify_ts2ps(request):
    body = ""
    data=TS2PSTransfer.objects.filter(applicant = request.user.userprofile)[0]
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nReason For Transfer: " + data.reason_for_transfer+
    "\nOrganization Name: " + data.name_of_org)
    mail(data,request,body)

def mail(data, request, body):
    send_mail("Transfer Application: " + request.user.username, body,
        'psdmail2020@gmail.com',[str(data.hod_email)],
        fail_silently=False)

def update_application(applicant, approved_by):
    try:
        transfer_form = PS2TSTransfer.objects.get(applicant=applicant)
        if approved_by == UserType.SUPERVISOR.value:
            transfer_form.is_supervisor_approved = True
        else:
            transfer_form.is_hod_approved = True
        transfer_form.save()
        return True
    except Exception as e:
        return False
