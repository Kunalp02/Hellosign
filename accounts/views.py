from django.shortcuts import render, redirect, HttpResponseRedirect
from .forms import RegistrationForm, UserForm
from .models import Account, Document
from django.contrib import messages, auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import requests
from hellosign_sdk import ApiClient, ApiException, Configuration, apis, models
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt



configuration = Configuration(
    # Configure HTTP basic authorization: api_key
    # username="8d4d5e8b52faa297cbd76ffdab1358e4c159048d002451bb588d0d46879a23c4", kunalpatil970730@gmail.com
    username = "a73de67ea35687b530fa5387d258bff8eb28b2dba13d64038478693b72de6548" # patilkunal970730@gmail.com
    # or, configure Bearer (JWT) authorization: oauth2
    # access_token="YOUR_ACCESS_TOKEN",
)
# file_url=[f'https://73dd-203-153-35-117.in.ngrok.io{doc_path.document.url}'],




@csrf_exempt
def callback(request):
    if request.method == "POST":
        response = HttpResponse("Hello API Event Received")
        try:
            data = json.loads(request.POST.get('json'))
            event = data['event']
            event_type = event['event_type']
            print(event_type)
        except:
            message = sys.exc_info()[0]
            print("Unexpected error:", message)
            logging.debug("Exception thrown - parseHelloSignData")

        return response
    return render(request, 'accounts/status.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.is_active = True
            user.save()

        
            messages.success(request, 'Thanks for registering with us')
            # return redirect('/accounts/login/?command=verification&email='+email)
            return redirect('login')
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            return redirect('send_file')
        else:
            messages.warning(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    # user_client = HSClient(email_address=email_address, password=password)    
    user_account = HSClient(email_address=request.user.email, password=request.user.password)
    print(user_account)
    return render(request, 'accounts/dashboard.html')


@login_required(login_url='login')
def send_file(request):
    if request.method == 'POST':
        domain = request.META['HTTP_HOST']
        email = request.POST['signer_email']
        document = request.FILES['document']
        title = request.POST['doc_title']
        print(request.user.id)
        print(email)
        doc = Document()
        doc.user = request.user
        doc.document = document
        doc.doc_title = request.POST['doc_title']

        doc.save()
        
        # print(doc_path.document.path)

        # print(request.META['HTTP_HOST'] + doc_path.document.url)
        # print(request.user.email)
        # print(doc)


        with ApiClient(configuration) as api_client:
            api = apis.SignatureRequestApi(api_client)
            doc_path = Document.objects.get(user=request.user, id=doc.id)
            print(doc_path.document.url)

            signer_1 = models.SubSignatureRequestSigner(
                email_address=email,
                name="KP",
                order=0,
            )

            # signer_2 = models.SubSignatureRequestSigner(
            #     email_address="jill@example.com",
            #     name="Jill",
            #     order=1,
            # )

            signing_options = models.SubSigningOptions(
                draw=True,
                type=True,
                upload=True,
                phone=True,
                default_type="draw",
            )

          
            data = models.SignatureRequestSendRequest(
                title=title,
                subject="Demo",
                message="Please sign in the document",
                signers=[signer_1],
                cc_email_addresses=[
                    "kunalpatil970730@gmail.com"
                ],
                file_url=[f'https://{domain}{doc_path.document.url}'],
                metadata={
                    "custom_id": 1234,
                    "custom_text": "NDA #9",
                },
                signing_options=signing_options,
                test_mode=True,
            )

            try:
                response = api.signature_request_send(data)
                request_id = response['signature_request']['signature_request_id']
                doc.signature_request = request_id
                doc.save()
                signing_url = response['signature_request']['signing_url']
                return redirect('check_status')
            except ApiException as e:
                print("Exception when calling HelloSign API: %s\n" % e)


    return render(request, 'accounts/send_file.html')


@login_required(login_url='login')
def check_status(request):
    user = request.user
    docs = Document.objects.filter(user=user).order_by('-created_at')
    print(docs)
    for doc in docs:
        
        with ApiClient(configuration) as api_client:
            api = apis.SignatureRequestApi(api_client)

            signature_request_id = doc.signature_request
            if signature_request_id is not None:
                try:
                    response = api.signature_request_get(signature_request_id) # to check status of current file
                    pprint(response)
                    # print(response['signature_request']['is_complete'])
                    if response['signature_request']['is_complete'] == True:
                        # doc = Document.objects.get(user=user, signature_request=signature_request_id)
                        doc.status = True
                        doc.final_copy = response['signature_request']['final_copy_uri']
                        doc.signing_url = response['signature_request']['signing_url']  
                        doc.signer_email = response['signature_request']['signatures'][0]['signer_email_address']
                        doc.save()
                    else:
                        pass
                except ApiException as e:
                    print("Exception when calling HelloSign API: %s\n" % e)
                    print(doc.signature_request, doc.signer_email, doc.document)


    context = {
        'docs' : docs,
    }
    return render(request, 'accounts/status.html', context)

@login_required(login_url='login')
def download_file(request, signature_request):
    print(signature_request)
    with ApiClient(configuration) as api_client:
        api = apis.SignatureRequestApi(api_client)

        signature_request_id = signature_request

        try:
            response = api.signature_request_files(signature_request_id, get_url=True, file_type="pdf")
            pprint(response)
        except ApiException as e:
            print("Exception when calling HelloSign API: %s\n" % e)
    
    # return redirect('check_status')
    return redirect(response.file_url)


