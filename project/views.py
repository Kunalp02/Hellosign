from django.http import HttpResponse
from django.shortcuts import render, redirect
import json
# from hellosign_sdk import HSClient
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

def home(request):
    print(request.META['HTTP_HOST'])
    return render(request, 'index.html')

@csrf_exempt
def callback(request):
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

  