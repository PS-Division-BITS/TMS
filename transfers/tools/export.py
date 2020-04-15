from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import re
from io import BytesIO as IO
import xlsxwriter 
count=1
final=pd.DataFrame(columns=['Sr.No', 'Name', 'Stream'])
def getFile(request, choice):
    #The script doesn't work if the models are not refreshed. 
    #That's why objectCode and this header should be always be put here instead of top
    from transfers.models import UserProfile, PS2TSTransfer as psts, TS2PSTransfer as tsps
    #encodeed all the types in a map
    objectCode={'01':psts.objects.filter(sub_type=0),
    '10':tsps.objects.filter(sub_type=0),
    '0100':tsps.objects.filter(sub_type=1) ,
    '1110':tsps.objects.filter(sub_type= 2), 
    'xx11':psts.objects.filter(sub_type=1)}
    global count
    global final   
    final=pd.DataFrame(columns=['Sr.No', 'Name', 'Stream']) #always mention the column attribute if want to have data in particular order
    if choice==1:
        filename="PS To TS"
        makeFile(objectCode['01'],0)
    elif choice==2:
        filename="TS To PS"
        makeFile(objectCode['10'],0)
    elif choice==3:
        filename="PS-TS or TS-PS to TS-TS"
        makeFile(objectCode['xx11'],0)
    elif choice==4:
        filename="PS-TS to PS-PS"
        makeFile(objectCode['0100'],0)
    elif choice==5:
        filename="TS-TS to TS-PS"
        makeFile(objectCode['1110'],0)
    response=download(final,filename)
    #reset global vars
    count=1
    final=pd.DataFrame(columns=['Sr.No', 'Name', 'Stream']) 
    return response

def getFileHod(request, choice):
    from transfers.models import UserProfile, PS2TSTransfer as psts, TS2PSTransfer as tsps
    #encodeed all the types in a map
    objectCode={'01':psts.objects.filter(sub_type=0),
    '10':tsps.objects.filter(sub_type=0),
    '0100':tsps.objects.filter(sub_type=1) ,
    '1110':tsps.objects.filter(sub_type= 2), 
    'xx11':psts.objects.filter(sub_type=1)}
    global count
    global final    
    if choice==1:
        filename="PS To TS"
        final=pd.DataFrame(columns=['Sr.No', 'Name', 'Transfer Type','CGPA','Thesis Locale', 'Thesis Subject', 'Organization Name', 'Expected Outcome'])
        makeFile(objectCode['01'],1)
        makeFile(objectCode['xx11'],1)
    elif choice==2:
        filename="TS To PS"
        final=pd.DataFrame(columns=['Sr.No', 'Name', 'Transfer Type','CGPA', 'Reason for Transfer','Organization Name'])
        makeFile(objectCode['10'],2)
        makeFile(objectCode['1110'],2)
        makeFile(objectCode['0100'],2)
    response=download(final,filename)
    #reset global vars
    count=1
    if choice==1:
        final=pd.DataFrame(columns=['Sr.No', 'Name', 'Transfer Type','CGPA','Thesis Locale', 'Thesis Subject', 'Organization Name', 'Expected Outcome'])
    elif choice==2:
        final=pd.DataFrame(columns=['Sr.No', 'Name', 'Transfer Type', 'Reason for Transfer','Organization Name'])
    return response
    
def download(final,filename):
    #final is the dataframe that contains all the details of the students approved by the hod
    excel_file=IO() #create a io memory stream
    xlwriter=pd.ExcelWriter(excel_file,engine='xlsxwriter') #xlsxwriter is a requirement
    final.to_excel(xlwriter, f'{filename}', index=False) #chosen the sheetname to be the same as filename
    xlwriter.save()
    xlwriter.close()
    excel_file.seek(0) #place the pointer at the start of the file
    response=HttpResponse(excel_file.read(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']=f'attachment; filename={filename}.xlsx' #makes an http file response of the excel
    print(final) #for debugging
    
    return response

def makeFile(x,choice):
    for data in x:
            global count
            global final
            print(data.is_hod_approved)
            if data.is_hod_approved==1:
                print(data.is_hod_approved)
                temp={}
                if choice==0:
                    temp={'Sr.No':count, 'Name':data.applicant.user.first_name+' '+ data.applicant.user.last_name, 'Stream':data.get_sub_type_display()} #for psd folks
                elif choice==2:
                    temp={'Sr.No':count, 'Name':data.applicant.user.first_name+' '+ data.applicant.user.last_name, 'Transfer Type':data.get_sub_type_display(), 'CGPA':str(data.cgpa),'Reason for Transfer':data.reason_for_transfer,'Organization Name':data.name_of_org  } #for hod: tsps
                else:
                    temp={'Sr.No':count, 'Name':data.applicant.user.first_name+' '+ data.applicant.user.last_name, 'Transfer Type':data.get_sub_type_display(), 'CGPA':str(data.cgpa),'Thesis Locale':data.get_thesis_locale_display(), 'Thesis Subject': data.thesis_subject,'Organization Name': data.name_of_org, 'Expected Outcome': data.expected_deliverables }
                final=final.append(temp,ignore_index=True) #for hod: psts
                count=count+1
