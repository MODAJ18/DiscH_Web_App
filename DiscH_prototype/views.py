from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.db.models import Max, Sum, ImageField
from django.shortcuts import redirect
from .models import Question, Comment
from .models import Answer, Answer_BOW, Achievement, Profile
import datetime

# auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib import messages

from itertools import chain

from .forms import GeeksForm

# from rest_framework.decorators import api_view
import random


# logging
import logging
logger = logging.getLogger("mylogger")

# plotting
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import numpy as np
import pandas as pd

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

def starting(request):
    recent_questions = Question.objects.order_by('?')[:20]
    template = loader.get_template('DiscH_prototype/new/Starting.html')
    picture = None

    if request.user.is_authenticated:
        request.session['first_name'] = request.user.first_name
        request.session['last_name'] = request.user.last_name
        request.session['login_state'] = True

        if request.GET.get('search'):
            search_value = request.GET.get('search')
            try:
                q = int(Question.objects.filter(question_id=search_value)[0].question_id)
            except:
                q = None

            if q:
                return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
            else:
                return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

        posts = request.POST
        if 'image_upload' in posts:
            form = GeeksForm(request.POST, request.FILES)
            if form.is_valid():
                img = form.cleaned_data.get("upload_image")

            prev_profile = Profile.objects.filter(user_id=request.user.id)
            if len(prev_profile) > 0:
                prev_profile.delete()
                messages.add_message(request, messages.INFO, 'profile image has changed')

            try:
                latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
            except:
                profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
            profile_new.save()
            return redirect(request.path)

        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
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
    context['form'] = GeeksForm()
    new_user = False
    if picture:
        context['picture'] = picture

    if request.method == 'POST':
        request.session['login_state'] = False
        logout(request)
        return redirect('/DiscH_prototype/starting')

    return HttpResponse(template.render(context, request))

def questions(request):
    if request.user.is_authenticated:
        template = loader.get_template('DiscH_prototype/new/Questions.html')
        recent_questions = Question.objects.order_by('?')[:8]

        if request.method == 'POST':
            posts = request.POST
            if 'image_upload' in posts:
                form = GeeksForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data.get("upload_image")

                prev_profile = Profile.objects.filter(user_id=request.user.id)
                if len(prev_profile) > 0:
                    prev_profile.delete()
                    messages.add_message(request, messages.INFO, 'profile image has changed')

                try:
                    latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                    profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
                except:
                    profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
                profile_new.save()
                return redirect(request.path)

            request.session['login_state'] = False
            logout(request)
            return redirect('/DiscH_prototype/starting')

        if request.GET.get('search'):
            search_value = request.GET.get('search')
            try:
                q = int(Question.objects.filter(question_id=search_value)[0].question_id)
            except:
                q = None

            if q:
                return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
            else:
                return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

        # if request.GET.get('search'):
        #     search_value = request.GET.get('search')
        #     try:
        #         q = Question.objects.filter(question_id=search_value)
        #     except:
        #         q = None
        #     if q:
        #         return redirect(f"/DiscH_prototype/questions/{search_value}/")

        context = {'recent_questions': recent_questions,
                    'login_state': request.session['login_state']
        }
        context['form'] = GeeksForm()
        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
        context['picture'] = picture
        
        return HttpResponse(template.render(context, request))
    else: 
        return redirect('/DiscH_prototype/Login/')

def reg(request):
    template = loader.get_template('DiscH_prototype/new/Register.html')

    global account_creation_failed, new_user, password_repeat_failed
    request.session['account_creation_failed'] = account_creation_failed
    request.session['password_repeat_failed'] = password_repeat_failed

    if request.GET.get('search'):
        search_value = request.GET.get('search')
        try:
            q = int(Question.objects.filter(question_id=search_value)[0].question_id)
        except:
            q = None

        if q:
            return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
        else:
            return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

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

def Login(request):
    template = loader.get_template('DiscH_prototype/new/Log-In.html')
    global account_login_failed
    request.session['account_login_failed'] = account_login_failed

    if request.GET.get('search'):
        search_value = request.GET.get('search')
        try:
            q = int(Question.objects.filter(question_id=search_value)[0].question_id)
        except:
            q = None

        if q:
            return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
        else:
            return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

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

    if request.user.is_authenticated:
        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
        context['picture'] = picture
        context['form'] = GeeksForm()
        if request.method == 'POST':
            posts = request.POST
            if 'image_upload' in posts:
                form = GeeksForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data.get("upload_image")

                prev_profile = Profile.objects.filter(user_id=request.user.id)
                if len(prev_profile) > 0:
                    prev_profile.delete()
                    messages.add_message(request, messages.INFO, 'profile image has changed')

                try:
                    latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                    profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
                except:
                    profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
                profile_new.save()
                return redirect(request.path)

            request.session['login_state'] = False
            logout(request)
            return redirect('/DiscH_prototype/starting')

        current_user_id = request.user.id

        if request.GET.get('search'):
            search_value = request.GET.get('search')
            try:
                q = int(Question.objects.filter(question_id=search_value)[0].question_id)
            except:
                q = None

            if q:
                return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
            else:
                return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

        # TODO: add in a list
        recent_user_answers = Answer.objects.filter(account_id_id=current_user_id).order_by('-date')[:10]


        question_answered = Answer.objects.filter(account_id_id=current_user_id)
        # remove questions with achievements already added
        questions_achievement = Achievement.objects.filter(account_id_id=current_user_id)
        for question_achievement in questions_achievement:
            question_answered = question_answered.exclude(question_id_id=question_achievement.question_id_id)
        logger.info(question_answered.count())
        # each question he answered --> count categories --> check if his category is represetative
        most_common_categories = {}
        for qa in question_answered:
            qa_qid = qa.question_id_id
            qa_categories = Answer.objects.filter(question_id_id=qa_qid)

            categs = []
            for qa_category in qa_categories:
                qa_category = qa_category.answer_category_num
                categs.append(qa_category)

            # get most common category for question
            most_common_category = max(categs, key=categs.count)
            most_common_categories[qa_qid] = most_common_category
            qa_user_category = qa.answer_category_num

            # logger.info(f'user categories: {qa_user_category}')
            logger.info(f'most common categories: {most_common_category} from {categs}')

            bronze_cond = (qa_user_category == most_common_category) and (categs.count(most_common_category) >= 5)
            silver_cond = bronze_cond and (qa.answer_justification != "none were given")
            gold_cond = silver_cond and (qa.answer_upvote > 10)

            if gold_cond:
                # grant bronze model
                try:
                    ach_id = Achievement.objects.aggregate(Max('achievement_id'))['achievement_id__max'] + 1
                    medal = Achievement(achievement_id=ach_id, achievement_type='gold medal', achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=200)
                except:
                    medal = Achievement(achievement_id=1, achievement_type='gold medal', achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=200)
                medal.save()
            elif silver_cond:
                try:
                    ach_id = Achievement.objects.aggregate(Max('achievement_id'))['achievement_id__max'] + 1
                    medal = Achievement(achievement_id=ach_id, achievement_type='silver medal',
                                        achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=75)

                except:
                    medal = Achievement(achievement_id=1, achievement_type='silver medal',
                                        achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=75)
                medal.save()
            elif bronze_cond:
                try:
                    ach_id = Achievement.objects.aggregate(Max('achievement_id'))['achievement_id__max'] + 1
                    medal = Achievement(achievement_id=ach_id, achievement_type='bronze medal',
                                        achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=50)
                except:
                    medal = Achievement(achievement_id=1, achievement_type='bronze medal',
                                        achievement_date=datetime.date.today(),
                                        account_id_id=request.user.id, question_id_id=qa_qid, value=50)
                medal.save()

        # gold medals, silver medals, and bronze letter letters, num of points collected last 30 days
        user_acheivs = Achievement.objects.filter(account_id_id=request.user.id)
        gold_count = 0
        silver_count = 0
        bronze_count = 0
        points_acc = 0

        for ua in user_acheivs:
            if ua.achievement_type == 'gold medal':
                gold_count += 1
            elif ua.achievement_type == 'silver medal':
                silver_count += 1
            elif ua.achievement_type == 'bronze medal':
                bronze_count += 1
            points_acc += ua.value

        # TODO: add info in 'various metrics' section
        context['points_acc'] = points_acc
        context['gold_count'] = gold_count
        context['silver_count'] = silver_count
        context['bronze_count'] = bronze_count

        logger.info('achievements set')
        logger.info(user_acheivs)

        # make leaderboard (table of user names / ranking)
        leaderboard_entries = Achievement.objects.values('account_id_id').annotate(total_points=Sum('value')).order_by('-total_points')[:10]
        names = []
        for i in leaderboard_entries:
            id_of_name = i['account_id_id']
            name = User.objects.filter(id=id_of_name).values()[0]['first_name']
            names.append(name)
        logger.info('x')
        logger.info(leaderboard_entries)
        logger.info(names)

            # TODO: make leaderboard table from this
        context['leaderboard_entries'] = leaderboard_entries
        context['names'] = names


        # make performance graph (recent medals, recent # answered questions = (on fire, doing well, decline) (use point plot)
        current_user_points_y = list(map(lambda x: x.value, list(user_acheivs)))
        current_user_points_x = list(map(lambda x: str(x.achievement_date), list(user_acheivs)))
        current_user_points = pd.DataFrame(current_user_points_x, columns=['date'])
        current_user_points['value'] = current_user_points_y
        current_user_points = current_user_points.groupby(['date']).sum().reset_index()
        # x = current_user_points.values().value
            # TODO: make graph from this
        logger.info("LIST")
        # logger.info(pd.to_datetime(current_user_points_x['date'], unit='d'))
        logger.info(current_user_points_x)

        graphs = []
        # Adding linear plot of y1 vs. x.
        # fig.update_xaxes(
        #     dtick="D1",  # sets minimal interval to day
        #     tickformat="%d.%m.%Y",  # the date format you want
        # )
        graphs.append(
            go.Scatter(x=pd.to_datetime(current_user_points['date'], format='%Y-%m-%d'), y=current_user_points['value'])
        )
        # Setting layout of the figure.
        layout = {
            'title': 'Points Scored over the last 30 days',
            'xaxis_title': 'Time',
            'yaxis_title': 'Points',
            'height': 420,
            'width': 530,
            # 'tickformat':"%b %d\n%Y",
            # 'tickmode': 'linear',
            'xaxis_tickformat': "%Y-%m-%d"
        }
        # Getting HTML needed to render the plot.
        plot_div = plot({'data': graphs, 'layout': layout},
                        output_type='div')
        context['plot_div'] = plot_div


        return HttpResponse(template.render(context, request))
    else:
        return redirect('/DiscH_prototype/Login/')

def about(request):
    template = loader.get_template('DiscH_prototype/new/About.html')
    context = {'login_state': request.session['login_state'],}
    context['form'] = GeeksForm()

    if request.user.is_authenticated:
        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
        context['picture'] = picture

        if request.method == 'POST':
            posts = request.POST
            if 'image_upload' in posts:
                form = GeeksForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data.get("upload_image")

                prev_profile = Profile.objects.filter(user_id=request.user.id)
                if len(prev_profile) > 0:
                    prev_profile.delete()
                    messages.add_message(request, messages.INFO, 'profile image has changed')

                try:
                    latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                    profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
                except:
                    profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
                profile_new.save()
                return redirect(request.path)

            request.session['login_state'] = False
            logout(request)
            return redirect('/DiscH_prototype/starting')

    if request.GET.get('search'):
        search_value = request.GET.get('search')
        try:
            q = int(Question.objects.filter(question_id=search_value)[0].question_id)
        except:
            q = None

        if q:
            return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
        else:
            return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

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
        context['form'] = GeeksForm()
        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
        context['picture'] = picture

        comments = Comment.objects.filter(question_id_id=question_id).select_related('account')
        if comments:
            context['comments'] = comments
        else:
            context['comments'] = None
        comment_account_ids = comments.values('account_id')
        comment_profile_pictures = []
        gold_medals_i = []
        silver_medals_i = []
        bronze_medals_i = []
        points_i = []
        own_user_account_map = []

        # information related to every user
        for cai in comment_account_ids:
            acc_id_i = cai['account_id']
            if request.user.id == acc_id_i:
                own_user_account_map.append(acc_id_i)
            else:
                own_user_account_map.append(None)

            try:
                comment_profile = Profile.objects.filter(user_id=acc_id_i)
            except:
                comment_profile = None

            if comment_profile:
                comment_picture = '/media/' + str(comment_profile[0].profile_pic)
            else:
                comment_picture = '/media/images/profile/default-profile-photo.jpg'
            comment_profile_pictures.append(comment_picture)
            user_acheivs_i = Achievement.objects.filter(account_id_id=acc_id_i)
            gold_count = 0
            silver_count = 0
            bronze_count = 0
            points_acc = 0
            for ua_i in user_acheivs_i:
                if ua_i.achievement_type == 'gold medal':
                    gold_count += 1
                elif ua_i.achievement_type == 'silver medal':
                    silver_count += 1
                elif ua_i.achievement_type == 'bronze medal':
                    bronze_count += 1
                points_acc += ua_i.value
            gold_medals_i.append(gold_count)
            silver_medals_i.append(silver_count)
            bronze_medals_i.append(bronze_count)
            points_i.append(points_acc)

        context['comment_profile_pictures'] = comment_profile_pictures
        context['gold_medals_i'] = gold_medals_i
        context['silver_medals_i'] = silver_medals_i
        context['bronze_medals_i'] = bronze_medals_i
        context['points_i'] = points_i
        context['own_user_account_map'] = own_user_account_map

        # # current user pic
        # comment_profile = Profile.objects.filter(user_id=acc_id_i)
        # result_list = chain(comments, profiles)

        if request.GET.get('search'):
            search_value = request.GET.get('search')
            try:
                q = int(Question.objects.filter(question_id=search_value)[0].question_id)
            except:
                q = None

            if q:
                return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
            else:
                return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

        if request.method == 'POST':
            posts = request.POST
            if ('category_BOW' in posts) or ('category' in posts):
                BOW = request.POST.get('category_BOW')
                if BOW is None:
                    category = request.POST.get('category')
                    prev_answer = Answer.objects.filter(question_id_id=question_id, account_id_id=request.user.id)
                    if len(prev_answer) > 0:
                        # prev_answer_id = prev_answer[0].answer_id
                        # print(random.randint(0, 9))
                        # prev_answer.order_by('?')[:1].update(answer_category_num=category, answer_upvote=0)
                        prev_answer.update(answer_category_num=category, answer_upvote=0)
                        messages.add_message(request, messages.WARNING,
                                             'your previous answer to this question have been replaced!')
                        # return HttpResponse(prev_answer_id + ' changed-->' + new_changed_info)

                    else:
                        if category is not None:
                            try:
                                latest_answer_id = Answer.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                                ans = Answer(answer_id=latest_answer_id, answer_category_num=category,
                                             answer_justification='none were given', answer_upvote=0,
                                             account_id_id=request.user.id, question_id_id=question_id, date=datetime.date.today())
                            except:
                                ans = Answer(answer_id=1, answer_category_num=category, answer_justification='none were given',
                                             answer_upvote=0, account_id_id=request.user.id, question_id_id=question_id,
                                             date=datetime.date.today())
                                ans.save()
                                return redirect('/DiscH_prototype/questions/')
                            # question_selected.num_response = question_selected.num_response + 1
                            ans.save()
                            question_selected.save()
                        else:
                            logout_state = request.POST.get('logout')
                            if logout_state is not None:
                                request.session['login_state'] = False
                                logout(request)
                                return redirect('/DiscH_prototype/starting')
                            messages.info(request, "you haven't provided a proper response!")
                            # return HttpResponseRedirect(request.path_info)
                            # return redirect('/DiscH_prototype/questions/')
                    # return redirect('/DiscH_prototype/questions/')
                else:
                    prev_answer_BOW = Answer_BOW.objects.filter(question_id_id=question_id, account_id_id=request.user.id)
                    BOW_Justification = request.POST.get('justification_category_BOW')
                    BOW_comment_part = request.POST.get('comment_part')

                    if len(prev_answer_BOW) > 2:
                        # prev_answer_BOW.order_by('?').values_list('pk', flat=True)[0:1]
                        # prev_answer_BOW.order_by('?')[:1].update(answer_category_num=BOW, answer_justification=BOW_Justification, answer_text_comment=BOW_comment_part,
                        #                                     answer_upvote=0)
                        random_id = prev_answer_BOW.order_by('?')[:1].get().answer_id
                        prev_answer_BOW.filter(answer_id=random_id).update(answer_category_num=BOW,
                                                                           answer_justification=BOW_Justification,
                                                                           answer_text_comment=BOW_comment_part,
                                                                           answer_upvote=0)
                        messages.add_message(request, messages.WARNING, 'beware! one of your Bag-Of-Word responses have been replaced!')
                    if len(prev_answer_BOW) == 2:
                        messages.add_message(request, messages.WARNING, 'you only have 1 more Bag-Of-W  ord selection for the question, \
                                If you have more than that, some of your BOW responses are going to be replaced')
                    else:
                        try:
                            latest_answer_id = Answer_BOW.objects.aggregate(Max('answer_id'))['answer_id__max'] + 1
                            ans = Answer_BOW(answer_id=latest_answer_id, answer_category_num=BOW,
                                             answer_justification=BOW_Justification, answer_text_comment=BOW_comment_part,
                                             answer_upvote=0, account_id_id=request.user.id, question_id_id=question_id, date=datetime.date.today())
                        except:
                            ans = Answer_BOW(answer_id=1, answer_category_num=BOW, answer_justification=BOW_Justification,
                                             answer_text_comment=BOW_comment_part,
                                             answer_upvote=0, account_id_id=request.user.id, question_id_id=question_id, date=datetime.date.today())
                            ans.save()
                        # question_selected.num_response = question_selected.num_response + 1
                        # not num responses
                        ans.save()
                        question_selected.save()
            elif 'post_comment' in posts:
                comment_text = posts['question_comment']
                try:
                    latest_comment_id = Comment.objects.aggregate(Max('comment_id'))['comment_id__max'] + 1
                    comme = Comment(comment_id=latest_comment_id, comment=comment_text,
                                     upvote_num=0, account_id=request.user.id, question_id_id=question_id)
                except:
                    comme = Comment(comment_id=1, comment=comment_text,
                                    upvote_num=0, account_id=request.user.id, question_id_id=question_id)
                comme.save()
                return redirect(request.path)
            elif 'remove_comment' in posts:
                id_comment_to_remove = posts['remove_comment']
                Comment.objects.filter(comment_id=id_comment_to_remove).delete()
                return redirect(request.path)
            elif 'image_upload' in posts:
                form = GeeksForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data.get("upload_image")

                prev_profile = Profile.objects.filter(user_id=request.user.id)
                if len(prev_profile) > 0:
                    prev_profile.delete()
                    messages.add_message(request, messages.INFO, 'profile image has changed')

                try:
                    latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                    profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
                except:
                    profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
                profile_new.save()
                return redirect(request.path)
            else:
                return HttpResponse('unknown post')

        return HttpResponse(template.render(context, request))
    else:
        return redirect('/DiscH_prototype/Login/')

    return HttpResponse(template.render(context, request))

def search_page(request, search_term='none'):
    if request.user.is_authenticated:
        context = {
            'login_state': request.session['login_state'],
        }
        template = loader.get_template('DiscH_prototype/new/Search.html')
        context['form'] = GeeksForm()


        if request.GET.get('search'):
            search_value = request.GET.get('search')
            try:
                q = int(Question.objects.filter(question_id=search_value)[0].question_id)
            except:
                q = None

            if q:
                return redirect(f"/DiscH_prototype/questions/{int(search_value)}/")
            else:
                return redirect(f"/DiscH_prototype/questions/search/{search_value}/")

        if request.method == 'POST':
            posts = request.POST
            if 'image_upload' in posts:
                form = GeeksForm(request.POST, request.FILES)
                if form.is_valid():
                    img = form.cleaned_data.get("upload_image")

                prev_profile = Profile.objects.filter(user_id=request.user.id)
                if len(prev_profile) > 0:
                    prev_profile.delete()
                    messages.add_message(request, messages.INFO, 'profile image has changed')

                try:
                    latest_profile_id = Profile.objects.aggregate(Max('id'))['id__max'] + 1
                    profile_new = Profile.objects.create(id=latest_profile_id, profile_pic=img, user_id=request.user.id)
                except:
                    profile_new = Profile.objects.create(id=1, profile_pic=img, user_id=request.user.id)
                profile_new.save()
                return redirect(request.path)

            request.session['login_state'] = False
            logout(request)
            return redirect('/DiscH_prototype/starting')

        picture = Profile.objects.filter(user_id=request.user.id)
        if picture:
            picture = picture[0].profile_pic
        else:
            picture = None
        context['picture'] = picture
        # return HttpResponse(picture)

        q = Question.objects.filter(description__contains=search_term)[:10]
        context['questions_found'] = q
        return HttpResponse(template.render(context, request))
        # return HttpResponse(search_term)
    else:
        return redirect('/DiscH_prototype/Login/')



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
                user = User.objects.create_user(username=fname + ' ' + lname, email=email, password=password,
                                                first_name=fname, last_name=lname)
                user.set_password(password)
                user.save()
                request.session['new_user'] = True
                new_user = True
                return redirect('/DiscH_prototype/')

    context = {'account_creation_failed': request.session['account_creation_failed']}

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


def public(request):
    return HttpResponse("You don't need to be authenticated to see this")
def private(request):
    return HttpResponse("You should not see this message if not authenticated!")