from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponseRedirect
from shipment_tracking.models import ShipmentTracking
from company.models import CompanyDetails
from orders.models import Order
from payment.models import Payment
import threading
import time
from shipment.models import CNFInfo as CNF
from payment.models import Payment
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
def send_delayed_email(subject, text_content, html_content, from_email, to):
    def send_email():
        time.sleep(5)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    threading.Thread(target=send_email).start()

# def send_delayed_email(subject, message, recipient_list):
#     def send_email():
#         # Wait for 5 seconds
#         time.sleep(5)
#         # Send the email
#         msg = EmailMessage(subject, message,to=recipient_list)
#         msg.send()
#         print('sent')
#     # Start a new thread to send the email
#     threading.Thread(target=send_email).start()
    
def view_shipment(request, pk):
    shipment_tracking = get_object_or_404(ShipmentTracking, pk=pk)
    if request.method=='POST':
        
        subject="Kindly Update the Tracking with the given Secret Key"
        order=get_object_or_404(Order, order_no=shipment_tracking.order_no)
        
        company=get_object_or_404(CompanyDetails, customer_no=order.company)
        recipient_list = [company.email]
        
        checklist = [
                    shipment_tracking.order_delivered,
                    shipment_tracking.payment_lc
                    ]
        
        if checklist[0]==False:
            unique_id=shipment_tracking.buyer_unique_id
        else:
            unique_id=shipment_tracking.buyer_payment_unique_id
        message="<p> Here is your link http://127.0.0.1:8000/shipment-tracking/update/"+str(pk)+"/ . and your secret code to update the tracking is <strong>"+unique_id+"</strong>. Thank you for helping."    
                
        send_delayed_email(subject,"This is an important message", message,settings.EMAIL_HOST_USER,recipient_list)
                
        
    return render(request, 'shipment_tracking/view_shipment.html', {'shipment_tracking': shipment_tracking})
    


def shipment_confirm_update_buyer(request, pk):
    shipment_tracking = get_object_or_404(ShipmentTracking, id=pk)
    checklist = [shipment_tracking.ready, shipment_tracking.shipped, shipment_tracking.reached_overseas,
                 shipment_tracking.order_delivered, shipment_tracking.payment_lc
                 ]
    if checklist[0]==False:
        status="is Ready"
    elif checklist[1]==False:
        status="is Shipped"
    elif checklist[2]==False:
        status="has Reached Overseas"
    elif checklist[3]==False:
        status="is Delivered"
    elif checklist[4]==False:
        status="has got Payment"
    else:
        status=None
    
    
    
    if request.method == 'POST':
        
        
        if checklist[3]==False:
            unique_code = request.POST.get("code")
            if shipment_tracking.buyer_unique_id==unique_code:
                Order.objects.filter(order_no=shipment_tracking.order_no).update(delivered_on =datetime.now(),order_delivery_status=True)
                ShipmentTracking.objects.filter(pk=pk).update(order_delivered  =True, order_delivered_date  =datetime.now())
                return redirect('thank_you')
        elif checklist[4]==False:
            unique_code = request.POST.get("code")
            if shipment_tracking.buyer_payment_unique_id==unique_code:
                Payment.objects.filter(order_no=shipment_tracking.order_no).update(paid_date=datetime.now(),payment_status=True)
                ShipmentTracking.objects.filter(pk=pk).update(payment_lc  =True, order_payment_lc_date  =datetime.now())
                return redirect('thank_you')
    return render(request, 'tracking_order/confirm_update.html', {'shipment_tracking': shipment_tracking, 
                                                                  'status':status, 
                                                                  })

def shipment_confirm_update_cnf(request, pk):
    shipment_tracking = get_object_or_404(ShipmentTracking, id=pk)
    checklist = [shipment_tracking.ready, shipment_tracking.shipped, shipment_tracking.reached_overseas,
                 shipment_tracking.order_delivered, shipment_tracking.payment_lc
                 ]
    if checklist[0]==False:
        status="is Ready"
    elif checklist[1]==False:
        status="is Shipped"
    elif checklist[2]==False:
        status="has Reached Overseas"
    
    else:
        status=None
    
    
    
    if request.method == 'POST':
        
        if checklist[0]==False:
            carton_description=request.POST.get('carton')
            #print(carton_description)
            if carton_description==None or carton_description=="":
                return HttpResponseRedirect(request.path_info)
            ShipmentTracking.objects.filter(pk=pk).update(ready=True, order_ready_date=datetime.now(),carton_description=carton_description)
            message="<p> Your order status has been updated. Check it here: http://127.0.0.1:8000/shipment-tracking/view/"+str(pk)+"/ . "    
            subject = "Your Order Status Updated"
            order=get_object_or_404(Order, order_no=shipment_tracking.order_no)
        
            company=get_object_or_404(CompanyDetails, customer_no=order.company)
            recipient_list = [company.email]
            send_delayed_email(subject,"This is an important message", message,settings.EMAIL_HOST_USER,recipient_list)
            return redirect('thank_you')
        if checklist[1]==False:
            
            container_description = request.POST.get('container')
            if container_description==None or container_description=="":
                return HttpResponseRedirect(request.path_info)
            ShipmentTracking.objects.filter(pk=pk).update(shipped=True, order_shipped_date=datetime.now(),container_description=container_description )
            message="<p> Your order status has been updated. Check it here: http://127.0.0.1:8000/shipment-tracking/view/"+str(pk)+"/ . "    
            subject = "Your Order Status Updated"
            order=get_object_or_404(Order, order_no=shipment_tracking.order_no)
        
            company=get_object_or_404(CompanyDetails, customer_no=order.company)
            recipient_list = [company.email]
            send_delayed_email(subject,"This is an important message", message,settings.EMAIL_HOST_USER,recipient_list)
            return redirect('thank_you')
        if checklist[2]==False:
            
            ShipmentTracking.objects.filter(pk=pk).update(reached_overseas =True, order_reached_overseas_date =datetime.now())
            
            message="<p> Your order status has been updated. Check it here: http://127.0.0.1:8000/shipment-tracking/view/"+str(pk)+"/ . "    
            subject = "Your Order Status Updated"
            order=get_object_or_404(Order, order_no=shipment_tracking.order_no)
        
            company=get_object_or_404(CompanyDetails, customer_no=order.company)
            recipient_list = [company.email]
            send_delayed_email(subject,"This is an important message", message,settings.EMAIL_HOST_USER,recipient_list)
            return redirect('thank_you')
        
    return render(request, 'tracking_order/confirm_update.html', {'shipment_tracking': shipment_tracking, 
                                                                  'status':status, 
                                                                  })



def tracking_list(request):
    shipment_trackings=ShipmentTracking.objects.all()
    return render(request, 'tracking_order/tracking-list.html', {'shipment_trackings':shipment_trackings})

def tracking_list_cnf(request):
    try:
        cnf = get_object_or_404(CNF, email=request.user.email)
        shipment_trackings=ShipmentTracking.objects.filter(cnf_no=cnf.cnf_no)
    except:
        shipment_trackings=None
    return render(request, 'tracking_order/tracking-list.html', {'shipment_trackings':shipment_trackings})

def thank_you(request):
    return render(request, 'tracking_order/thank_you.html')










