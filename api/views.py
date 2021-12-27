from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate ,login , logout
from rest_framework import status,permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from django.db.models import Count
from .models import *
import feedparser
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from time import gmtime
import time
from datetime import  timedelta
import datetime 




class Linkfetch(APIView):
    permission_classes=(permissions.IsAuthenticated,)  

  
    def get(self, request, format=None):
        user = request.user.id
        top_links = Link.objects.annotate(like_count=Count('subscribe')).order_by('-like_count').exclude(subscribe__id=user)[0:10]
        print(top_links)
        subscription = Link.objects.filter(subscribe__id=user).all()
        sub_data = Subscriptionserializer(subscription, many=True)
        top_data = Topsubscriptionserializer(top_links, many=True)

        return Response(data={"top_sub":top_data.data,"results":sub_data.data},template_name="index.html")


class Login(APIView):

    permission_classes=(permissions.AllowAny,)  
    def get(self,request):
        try:      
            return Response(data={"data":"True"},status=status.HTTP_202_ACCEPTED,template_name="register.html")
        except:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)


    def post(self,request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            data = User.objects.filter(username=username).exists()
            if not data:
                return Response(data={"data":"False","message":"Invalid Username"},status=status.HTTP_202_ACCEPTED)
            data = authenticate(username=username,password=password)
            if data != None:
                if User.objects.get(username=username).is_staff == False:
                    return Response(data={"data":"False","message":'Profile is not verified check your mail.'},status=status.HTTP_202_ACCEPTED)
                login(request,data)
                return Response(data={"data":"True"},status=status.HTTP_202_ACCEPTED)
            return Response(data={"data":"False","message":"Invalid password"},status=status.HTTP_202_ACCEPTED)
        except:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)


class Createuser(APIView):
    permission_classes=(permissions.AllowAny,)  
    def post(self, request):

        try:
            email=request.data.get('email')
            username = request.data.get('username')
            data = User.objects.filter(username=username).exists()
            if data:
                return Response(data={"data":"False","message":" User already exists"},status=status.HTTP_202_ACCEPTED)
            mail_data = User.objects.filter(email=email).exists()
            if mail_data:
                return Response(data={"data":"False","message":" Mail address  already exists"},status=status.HTTP_202_ACCEPTED)
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(username=username)
                token,created = Token.objects.get_or_create(user=user)
                send_mail_after_registration(email,token)

                return Response(data={"data":"True","message":"User registered check  mail to activate account"},status=status.HTTP_201_CREATED)
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)    
        except Exception as e:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)


class Logout(APIView):
    def post(self,request):

        try:
            logout(request)
            return Response(data={"data":"True"},status=status.HTTP_202_ACCEPTED)
        except:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)


class Subscribeapi(APIView):
    def post(self,request):
        try:
            event_id = request.data.get('event_id')
            user = request.user
            a = Link.objects.filter(id=event_id,subscribe__id=user.id).first()
            print(a)
            if a == None:
                b = Link.objects.get(id=event_id)
                b.subscribe.add(user)
                message ="Subscribed sucessfully" 
            else:
                a.subscribe.remove(user)  
                message ="unsubscribed sucessfully"             

            return Response(data={"data":"True","message":message},status=status.HTTP_202_ACCEPTED)
        except:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)



class Linkadd(APIView):
    def post(self,request):
        try:

            link = request.data.get('link')
            feed = feedparser.parse(link)       
            data = feed.get("entries")
            if not data:
                return Response(data={"data":"False","message":"Please enter a valid link !"},status=status.HTTP_202_ACCEPTED,template_name="sucess.html")
            title = feed.get("feed").get("title")
            title_test = Link.objects.filter(title=title,link=link).last()
            if  title_test==None:
                Link_obj = Link.objects.create(title=title,link=link)    
                Link_obj.save()
                Link_obj.subscribe.add(request.user)  
                return Response(data={"data":"True","message":"Subscribed sucessfully"},status=status.HTTP_202_ACCEPTED,template_name="sucess.html")
            title_test.subscribe.add(request.user)    
            return Response(data={"data":"True","message":"Subscribed sucessfully"},status=status.HTTP_202_ACCEPTED,template_name="sucess.html")
    

        except:
            return Response(data={"data":"False","message":"Oops something went wrong !"},status=status.HTTP_202_ACCEPTED)



class Verify(APIView):
    def get(self,request,auth_token):
        try:
            user = Token.objects.get(key=auth_token).user
            user.is_staff=True
            user.save()
            return Response(data={"data":"True"},status=status.HTTP_202_ACCEPTED,template_name="sucess.html")
        except:
            return Response(data={"data":"False"},status=status.HTTP_202_ACCEPTED,template_name="error.html")



def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/api/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )          




def bulk_notification():
    links = Link.objects.all()
    for link in links:
        feed = feedparser.parse(link.link)
        entries = []
        data = feed.get("entries")
        now = gmtime()
        for section in data:
            if section.get("published_parsed") != None:
                if (section.published_parsed[0],section.published_parsed[1],section.published_parsed[2]) == (now[0],now[1],now[2]):
                    if datetime.timedelta(seconds=time.mktime(now)-time.mktime(section.get("published_parsed")))  <  timedelta(minutes=60):
                        entries.append(section)
        if len(entries)!= 0:
            final_data = []
            count = 1
            for i in entries:
                final_data.append(str(count)+". "+i.get("title")+i.get("summary")+i.get("links")[0].get("href"))
                count=count+1
            final_data = "                                                                                                                                                       ".join(final_data)   
            usr_list = User.objects.filter(links__id=link.id,is_staff=True).exclude(email='')
            email_list = [usr.email for usr in usr_list ]
            subject = "Latest news @" + link.title
            message = final_data
            email_from = settings.EMAIL_HOST_USER
            recipient_list = email_list
            send_mail(subject, message , email_from ,recipient_list ) 
    return None        














