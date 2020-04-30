# Student user utility functions
from django.core.mail import send_mail
from transfers.constants import UserType, TransferType, ThesisLocaleType, ApplicationsStatus
from django.http import JsonResponse
from transfers.models import PS2TSTransfer, TS2PSTransfer, DeadlineModel
from django.utils import timezone as datetime

import re 
def validate_contact(value): 
    Pattern = re.compile("(0/91)?[7-9][0-9]{9}")
    return Pattern.match(value) 
    
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
            status = _get_ts2ps_application_status(userprofile, ts2ps)
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
    if application.is_supervisor_approved == ApplicationsStatus.REJECTED.value or \
        application.is_hod_approved == ApplicationsStatus.REJECTED.value or \
        application.is_ad_approved == ApplicationsStatus.REJECTED.value:
        return ApplicationsStatus.REJECTED.value
    elif application.is_supervisor_approved == ApplicationsStatus.PENDING.value or \
        application.is_hod_approved == ApplicationsStatus.PENDING.value:
        return ApplicationsStatus.PENDING.value
    else:
        return ApplicationsStatus.APPROVED.value

def _get_ts2ps_application_status(userprofile, ts2ps):
    application = ts2ps[0]
    if application.is_hod_approved == ApplicationsStatus.REJECTED.value or \
        application.is_ad_approved == ApplicationsStatus.REJECTED.value:
        return ApplicationsStatus.REJECTED.value
    elif application.is_hod_approved == ApplicationsStatus.PENDING.value:
        return ApplicationsStatus.PENDING.value
    else:
        return ApplicationsStatus.APPROVED.value

def get_branch_from_branch_code(branch_code):
    switcher = {
        'A1': 'B.E. Chemical Engineering',
        'A2': 'B.E. Civil Engineering',
        'A3': 'B.E. Electrical and Electronics Engineering',
        'A4': 'B.E. Mechanical Engineering',
        'A5': 'B. Pharm.',
        'A7': 'B.E. Computer Science Engineering',
        'A8': 'B.E. Electronics and Instrumentation Engineering',
        'A9': 'B.E. Biotechnology',
        'AA': 'B.E. Electronics and Communication Engineering',
        'AB': 'B.E. Manufacturing Engineering',
        'B1': 'M.Sc. Biology + ',
        'B2': 'M.Sc. Chemistry + ',
        'B3': 'M.Sc. Economics + ',
        'B4': 'M.Sc. Mathematics + ',
        'B5': 'M.Sc. Physics + ',
        'C2': 'M.Sc. General Studies + ',
        'C5': 'M.Sc. Engineering Technology + ',
        'C6': 'M.Sc. Information Systems + ',
        'C7': 'M.Sc. Finance + ',
        'PS': '',
    }
    return switcher.get(branch_code, "Invalid branch code")
def notify_ps2ts(data, receiver):
    body = ""
    print(str(data.hod_email))
    topHod="Dear Sir/Madam,\n\nGreetings from Practice School Division!\n\nPlease find below the details of the student who has applied for PS to TS transfer and also got recommended by supervisor/co-supervisor for the Thesis work.  The last date to submit the recommendation is April 26th, 2020.\n"
    topSup="Dear Sir/Madam,\nGreetings from Practice School Division!\nPlease find below the details of the student who has applied for PS to TS transfer and has proposed your name as the supervisor/co-supervisor for the Thesis work.  The last date to submit the recommended is April 26th, 2020. \n"
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nThesis Locale: " + data.get_thesis_locale_display()+
    "\nThesis Subject: " + data.thesis_subject+
    "\nOrganization Name: " + data.name_of_org+
    "\nExpected Outcome: " + data.expected_deliverables)
    
    bottomHod="\n\nYou are kindly requested to recommend/not recommend the above student for further approval using the Transfer Management System.\n\nLink to access the Transfer Management System: http://bits-pilani.in/TMS/login/ \n\nAssociate Dean\nPractice School Division\n"
    bottomSup="\n\nFor supervisor: Visit http://bits-pilani.in/TMS/login/ and proceed as follows:\nStep 1:\n\nYour Username will be your PSRN and Password needs to be retrieved by following the below process.\n\nNote for password generation: Click on the ‘Forgot Password’ option, and then enter your registered BITS email id, you will receive instruction to set a new password.\n\nSupervisor can also update the profile by clicking “view profile “available on the right-hand side top corner.\n\nStep 2: \n\nClick the appropriate tab (PS to TS transfer) to view all the details entered by student. The form is same for both single degree and Dual Degree students (both semester Thesis). Details of students who wish to do TS with your supervision will also be available in the portal.\n\t• By clicking the student card, applicant’s details will be visible (Student ID, Student Name, CGPA, supervisor email, Thesis type, Thesis subject, Thesis location, Organization details, Expected deliverables).\n\nStep 3:\n\t• Supervisor can view all the details and has an option either to forward the request or not to forward the requests to the concerned HoD. The details of “forwarded” and “Not-forwarded” requests can be seen by clicking the toggle menu.\n\t• Hence, students seeking transfer need to mention the corresponding HoD details while filling up the form.\nAssociate Dean\nPractice School Division\n"
    email=""
    if receiver=="hod":
        body=topHod+body+bottomHod
        email=str(data.hod_email)
    else:
        body=topSup+body+bottomSup
        email=str(data.supervisor_email)
    username=str(data.applicant.user.username)
    mail(email,username,body)

def notify_ts2ps(request):
    body = ""
    data=TS2PSTransfer.objects.filter(applicant = request.user.userprofile)[0]
    topHod="Dear Sir/Madam,\n\nGreetings from Practice School Division!\n\nPlease find below the details of the student who has applied for TS to PS transfer.  The last date to submit the recommendation is April 26th, 2020.\n"
    body =  str("\nID: " + data.applicant.user.username+
    "\nName: " + data.applicant.user.first_name + " " +data.applicant.user.last_name +
    "\nTransfer Type: " + data.get_sub_type_display()+
    "\nCGPA: " + str(data.cgpa)+
    "\nReason For Transfer: " + data.reason_for_transfer+
    "\nOrganization Name: " + data.name_of_org)
    bottomHod="\n\nYou are kindly requested to recommend/not recommend the above student for further approval using the Transfer Management System.\n\nLink to access the Transfer Management System: http://bits-pilani.in/TMS/login/ \n\nAssociate Dean\nPractice School Division\n"
    body=topHod+body+bottomHod
    mail(str(data.hod_email),str(data.applicant.user.username),body)

def mail(email, username, body):
    send_mail("Transfer Application: " + username, body,
        'psdiary.bits@gmail.com',[email],
        fail_silently=False)
    print(f"Sent to {email}")


def get_authority_comments(userprofile):
    ps2ts = PS2TSTransfer.objects.filter(applicant=userprofile)
    ts2ps = TS2PSTransfer.objects.filter(applicant=userprofile)
    comments_from_ad = ""
    comments_from_supervisor = ""
    comments_from_hod = ""
    if ps2ts.count() == 1:
        comments_from_hod = ps2ts[0].comments_from_hod
        comments_from_supervisor = ps2ts[0].comments_from_supervisor
        comments_from_ad = ps2ts[0].comments_from_ad
    elif ts2ps.count() == 1:
        comments_from_hod = ts2ps[0].comments_from_hod
        comments_from_ad = ts2ps[0].comments_from_ad
    return (comments_from_hod, comments_from_supervisor, comments_from_ad)
