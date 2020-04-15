from django.shortcuts import render
from django.views import generic
from django.http import JsonResponse
from django.shortcuts import redirect
from django.http import HttpResponse

from transfers.constants import CampusType, UserType, TransferType
from transfers.models import PS2TSTransfer, UserProfile
from transfers.forms import PS2TSTransferForm, TS2PSTransferForm

from transfers.utils import get_application_status, notify_ps2ts, notify_ts2ps, get_deadline_status
from transfers.tools.populate import populate
from transfers.tools.export import *

def exp(request):
	if request.method=='GET':
		return render(request, 'transfers/export.html')
	if request.method=='POST':
		if request.user.is_superuser:
			print(request.POST['type'])
			response=getFile(request, int(request.POST['type']))
		else:
			response=HttpResponse("You don't have acces to this page")
	return response