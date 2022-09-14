from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.db.models import Max
from django.shortcuts import redirect
from .models import Question
from .models import Answer, Answer_BOW

# auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect


# from rest_framework.decorators import api_view
from django.http import HttpResponse

account_creation_failed = False
account_login_failed = False
password_repeat_failed = False


from rest_framework import viewsets
from .serializers import QuestionSerializer
# from rest_framework.decorators import action


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()[:10]

    # The viewsets.ModelViewSet provides methods to handle CRUD operations by default.
    # We just need to do specify the serializer class and the queryset

new_user = False

def index(request):
    recent_questions = Question.objects.order_by('?')[:20]
    template = loader.get_template('DiscH_prototype/index.html')

    if request.user.is_authenticated:
        request.session['first_name'] = request.user.first_name
        request.session['last_name'] = request.user.last_name
        request.session['login_state'] = True
    else:
        request.session['login_state'] = False
        request.session['first_name'] = None
        request.session['last_name'] = None

    global new_user
    context = {
        'recent_questions': recent_questions,
        'new_user': new_user,
        'login_state': request.session['login_state'],
        'first_name': request.session['first_name'],
        'last_name': request.session['last_name'],
    }
    new_user = False

    if request.method == 'POST':
        request.session['login_state'] = False
        logout(request)
        return redirect('/DiscH_prototype/starting')

    return HttpResponse(template.render(context, request))

def starting(request):
    recent_questions = Question.objects.order_by('?')[:20]
    template = loader.get_template('DiscH_prototype/new/starting.html')

    if request.user.is_authenticated:
        request.session['first_name'] = request.user.first_name
        request.session['last_name'] = request.user.last_name
        request.session['login_state'] = True
    else:
        request.session['login_state'] = False
        request.session['first_name'] = None
        request.session['last_name'] = None

    global new_user
    context = {
        'recent_questions': recent_questions,
        'new_user': new_user,
        'login_state': request.session['login_state'],
        'first_name': request.session['first_name'],
        'last_name': request.session['last_name'],
    }
    new_user = False

    if request.method == 'POST':
        request.session['login_state'] = False
        logout(request)
        return redirect('/DiscH_prototype/starting')

    # context = {}
    return HttpResponse(template.render(context, request))



def question(request, question_id):  # later add question_id
    if request.user.is_authenticated:
        try:
            question_selected = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise Http404("Question does not exist")

        template = loader.get_template('DiscH_prototype/detail.html')
        context = {
            'question_selected': question_selected,
            'login_state': request.session['login_state'],
            'first_name': request.session['first_name'],
            'last_name': request.session['last_name']
        }

        if request.method == 'POST':
            BOW = request.POST.get('category_BOW')
            if BOW is None:
                category = request.POST.get('category')
                if category is not None:
                    try:
                        latest_answer_id = Answer.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                        ans = Answer(answer_id=latest_answer_id, answer_category_num=category, answer_justification='none were given',
                                     answer_upvote=0, account_id_id=1, question_id_id=question_id)
                    except:
                        ans = Answer(answer_id=1, answer_category_num=category, answer_justification='none were given', answer_upvote=0, account_id_id=1, question_id_id=question_id)
                        ans.save()
                        return HttpResponse('category: {}\t answer_id: 1\t first response!'.format(category))
                    question_selected.num_response = question_selected.num_response + 1
                    ans.save()
                    question_selected.save()
                else:
                    return redirect('/DiscH_prototype/')

            else:
                BOW_Justification = request.POST.get('justification_category_BOW')
                BOW_comment_part = request.POST.get('comment_part')
                try:
                    latest_answer_id = Answer_BOW.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                    ans = Answer_BOW(answer_id=latest_answer_id, answer_category_num=BOW,
                                answer_justification=BOW_Justification, answer_text_comment=BOW_comment_part,
                                answer_upvote=0, account_id_id=1, question_id_id=question_id)
                except:
                    ans = Answer_BOW(answer_id=1, answer_category_num=BOW, answer_justification=BOW_Justification,
                                    answer_text_comment=BOW_comment_part,
                                answer_upvote=0, account_id_id=1, question_id_id=question_id)
                    ans.save()
                # question_selected.num_response = question_selected.num_response + 1
                # not num responses
                ans.save()
                question_selected.save()
                redirect('/DiscH_prototype')

        return HttpResponse(template.render(context, request))
    else:
        return redirect('/DiscH_prototype/login/')


def questions(request):
    if request.user.is_authenticated:
        template = loader.get_template('DiscH_prototype/new/Questions.html')
        recent_questions = Question.objects.order_by('?')[:5]

        if request.method == 'POST':
            request.session['login_state'] = False
            logout(request)
            return redirect('/DiscH_prototype/starting')

        context = {'recent_questions': recent_questions,
                    'login_state': request.session['login_state']
        }
        
        return HttpResponse(template.render(context, request))
    else: 
        return redirect('/DiscH_prototype/Login/')



def addAccount(request):
    template = loader.get_template('DiscH_prototype/signup.html')
    global account_creation_failed, new_user 
    request.session['account_creation_failed'] = account_creation_failed
    
    if request.method == 'POST':
        # return HttpResponse(request.POST.get('fname'))  # a bit of testing
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if fname and lname and email and password:
            if User.objects.filter(email=email):
                account_creation_failed = True
                request.session['account_creation_failed'] = account_creation_failed
                return redirect('/DiscH_prototype/addA/')
            else:
                account_creation_failed = False
                request.session['account_creation_failed'] = account_creation_failed
                user = User.objects.create_user(username=fname + ' ' + lname, email=email, password=password, first_name=fname, last_name=lname)
                user.set_password(password)
                user.save()
                request.session['new_user'] = True
                new_user = True
                return redirect('/DiscH_prototype/')

    context = {'account_creation_failed': request.session['account_creation_failed']}

    return HttpResponse(template.render(context, request))

def reg(request):
    template = loader.get_template('DiscH_prototype/new/Register.html')

    global account_creation_failed, new_user, password_repeat_failed
    request.session['account_creation_failed'] = account_creation_failed
    request.session['password_repeat_failed'] = password_repeat_failed

    if request.method == 'POST':
        # return HttpResponse(request.POST.get('fname'))  # a bit of testing
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('text')
        rpassword = request.POST.get('text-1')
        if password != rpassword:
            password_repeat_failed = True
            account_creation_failed = False
            return redirect('/DiscH_prototype/reg/')
            
        else:
            password_repeat_failed = False
            

        if fname and lname and email and password:
            if User.objects.filter(email=email):
                account_creation_failed = True
                request.session['account_creation_failed'] = account_creation_failed
                return redirect('/DiscH_prototype/reg/')
            else:
                account_creation_failed = False
                request.session['account_creation_failed'] = account_creation_failed
                username = fname + ' ' + lname
                user = User.objects.create_user(username=username, email=email, password=password, first_name=fname, last_name=lname)
                user.set_password(password)
                user.save()
                request.session['new_user'] = True
                new_user = True

                user = authenticate(request, username=username, password=password)
                login(request, user)
                return redirect('/DiscH_prototype/starting/')

    context = {
                'account_creation_failed': request.session['account_creation_failed'],
                'password_repeat_failed': request.session['password_repeat_failed'], 
    }
    password_repeat_failed = False
    account_creation_failed = False

    return HttpResponse(template.render(context, request))

def login_acc(request):
    template = loader.get_template('DiscH_prototype/login.html')
    global account_login_failed
    request.session['account_login_failed'] = account_login_failed

    if request.method == 'POST':
        email = request.POST['email']
        username = User.objects.get(email=email).username
        password = request.POST['password']
        if email and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/DiscH_prototype/')
            else:
                account_login_failed = True
                request.session['account_login_failed'] = account_login_failed
                return redirect('/DiscH_prototype/login/')

    context = {'account_login_failed': account_login_failed}
    return HttpResponse(template.render(context, request))

def Login(request):
    template = loader.get_template('DiscH_prototype/new/Log-In.html')
    global account_login_failed
    request.session['account_login_failed'] = account_login_failed

    if request.method == 'POST':
        email = request.POST['email']

        try:
            username = User.objects.get(email=email).username
        except:
            account_login_failed = True
            request.session['account_login_failed'] = account_login_failed
            return redirect('/DiscH_prototype/Login/')

        password = request.POST['password']
        if email and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/DiscH_prototype/starting/')
            else:
                account_login_failed = True
                request.session['account_login_failed'] = account_login_failed
                return redirect('/DiscH_prototype/Login/')

    context = {'account_login_failed': account_login_failed}
    account_login_failed = False
    return HttpResponse(template.render(context, request))



def dashboard(request):
    template = loader.get_template('DiscH_prototype/new/Dashboard.html')
    context = {'login_state': request.session['login_state'],}
    return HttpResponse(template.render(context, request))

def about(request):
    template = loader.get_template('DiscH_prototype/new/About.html')
    context = {'login_state': request.session['login_state'],}
    return HttpResponse(template.render(context, request))

def question_page(request, question_id):
    if request.user.is_authenticated:
        try:
            question_selected = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise Http404("Question does not exist")

        template = loader.get_template('DiscH_prototype/new/question_page.html')
        context = {
            'question_selected': question_selected,
            'login_state': request.session['login_state'],
            'first_name': request.session['first_name'],
            'last_name': request.session['last_name']
        }

        if request.method == 'POST':
            BOW = request.POST.get('category_BOW')
            if BOW is None:
                category = request.POST.get('category')
                if category is not None:
                    try:
                        latest_answer_id = Answer.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                        ans = Answer(answer_id=latest_answer_id, answer_category_num=category, answer_justification='none were given',
                                     answer_upvote=0, account_id_id=1, question_id_id=question_id)
                    except:
                        ans = Answer(answer_id=1, answer_category_num=category, answer_justification='none were given', answer_upvote=0, account_id_id=1, question_id_id=question_id)
                        ans.save()
                        return redirect('/DiscH_prototype/questions/')
                    question_selected.num_response = question_selected.num_response + 1
                    ans.save()
                    question_selected.save()
                else:
                    logout_state = request.POST.get('logout')
                    if logout_state is not None:
                        request.session['login_state'] = False
                        logout(request)
                        return redirect('/DiscH_prototype/starting')
                    
                    messages.info(request, "you haven't provided a proper response!")
                    return HttpResponseRedirect(request.path_info)
                    # return redirect('/DiscH_prototype/questions/')
                return redirect('/DiscH_prototype/questions/')
            else:
                BOW_Justification = request.POST.get('justification_category_BOW')
                BOW_comment_part = request.POST.get('comment_part')
                try:
                    latest_answer_id = Answer_BOW.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                    ans = Answer_BOW(answer_id=latest_answer_id, answer_category_num=BOW,
                                answer_justification=BOW_Justification, answer_text_comment=BOW_comment_part,
                                answer_upvote=0, account_id_id=1, question_id_id=question_id)
                except:
                    ans = Answer_BOW(answer_id=1, answer_category_num=BOW, answer_justification=BOW_Justification,
                                    answer_text_comment=BOW_comment_part,
                                answer_upvote=0, account_id_id=1, question_id_id=question_id)
                    ans.save()
                # question_selected.num_response = question_selected.num_response + 1
                # not num responses
                ans.save()
                question_selected.save()
                return redirect('/DiscH_prototype/questions/')

        return HttpResponse(template.render(context, request))
    else:
        return redirect('/DiscH_prototype/Login/')


    return HttpResponse(template.render(context, request))


def public(request):
    return HttpResponse("You don't need to be authenticated to see this")

def private(request):
    return HttpResponse("You should not see this message if not authenticated!")