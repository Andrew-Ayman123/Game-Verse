from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.db.models import QuerySet
import regex as re
from .models import LeaderBoard, LeaderBoardItem
import random
import time
from django.utils import timezone
import json
# Create your views here.


def home(request: HttpRequest):
    if request.method == 'POST':
        
        name = request.POST.get('name').strip()
        if name and re.match('^[A-Za-z0-9]+[A-Za-z0-9 ]*$', name):
            request.session['name'] = name
            if request.POST.get('Math Game'):
                return HttpResponseRedirect('math')
            elif request.POST.get('Wordle'):
                
                return HttpResponseRedirect('wordle')

    return render(request, 'main/home.html', {
        'games': {
            'Math Game': 'images/math_game.jpg',
            'Wordle': 'images/wordle_game.png',
        }
    }
    )


def game(request: HttpRequest, html_file_path: str, leaderboard_name: str, attrs: dict):
    name = request.session.get('name')
    if not attrs:
        attrs['startAnimation']=True
    if name is None:
        return HttpResponseRedirect('./')
    leaderboard = LeaderBoard.objects.get(name=leaderboard_name)
    if attrs.get('success'):
        score=attrs.get('score')
        max_score_item=LeaderBoardItem.objects.filter(name=name,leaderboard=leaderboard_name).order_by('-score').first()
        if max_score_item is None or score>max_score_item.score:
            if (max_score_item is not None):
                max_score_item.delete()
            leaderboard.leaderboarditem_set.create(
                name=name,
                date=timezone.now(),
                score=score
            ).save()

    leaderboard_items: QuerySet = leaderboard.leaderboarditem_set.all().order_by(
        '-score')[:10]
    
    leaderboard_items_list: list = [
        (val['name'], val['date'], val['score'])for val in leaderboard_items.values()]

    # leaderboard_items_list.extend([('','','') for _ in range(10-len(leaderboard_items_list))])
    attrs = {**{'name': name, 'leaderboard': leaderboard_items_list,'leaderboardLength':len(leaderboard_items_list)}, **attrs}

    return render(request, html_file_path, attrs)


def math_game(request: HttpRequest):
    attrs = {}
    session_math_key = 'math-attrs'
    if request.method == 'POST':
        if request.POST.get('start'):

            equation = '{} {} {} {} {} {} {} '.format(
                random.randint(0, 99),
                random.choice(['+', '-']),
                random.randint(0, 99),
                random.choice(['+', '-']),
                random.randint(0, 99),
                random.choice(['+', '-']),
                random.randint(0, 99)
            )
            res = int(eval(equation))
            attrs['equation'] = equation
            attrs['equationRes'] = res
            attrs['timeRemaining'] = 120
            attrs['time'] = float(time.time())
            request.session[session_math_key] = attrs

        elif request.POST.get('submit'):
            original_attrs = request.session.get(session_math_key)
            if original_attrs:
                request.session[session_math_key] = None
                user_val = request.POST.get('math-result')
                if user_val:
                    if int(user_val) == original_attrs['equationRes']:
                        # calculate score
                        score = int((
                            original_attrs['timeRemaining'] - (time.time()-original_attrs['time']))*100)

                        if score < 0:
                            score = 0
                            attrs['score'] = score
                            attrs['message'] = f'Sad :(, Time ran out'
                            attrs['success'] = False
                        else:
                            attrs['score'] = score
                            attrs['message'] = f'Bravo !!, Score: {score}'
                            attrs['success'] = True

                    else:
                        # wrong answer with socre 0
                        score = 0
                        attrs['score'] = score
                        attrs['message'] = f'Sad :(, Incorrect Answer'
                        attrs['success'] = False

    return game(request, 'main/math_game.html', 'math', attrs)


def wordle_game(request: HttpRequest):
    attrs = {}
    session_wordle_key = 'wordle-attrs'
    if request.method == 'POST':
        if request.POST.get('start'):
            with open('main/assets/json/wordle_words_secret.json') as f:
                word = random.choice(json.load(f)['words']).lower()
            attrs['word'] = word
            attrs['guesses'] = 6
            attrs['time'] = float(time.time())
            request.session[session_wordle_key] = attrs

        elif request.POST.get('submit'):
            original_attrs = request.session.get(session_wordle_key)
            if original_attrs:
                request.session[session_wordle_key] = None
                if 'success-from-consumer' in original_attrs:
                    score = int((
                        300 - (time.time()-original_attrs['time']))*100)
                    if score >= 0:
                        score = int(((original_attrs['guesses']+1)/6) * score)
                        attrs['score'] = score
                        attrs['message'] = f'Bravo !!, Score: {score}. Correct Answer: {original_attrs["word"]}'
                        attrs['success'] = True
                    else:
                        score = 0
                        attrs['score'] = score
                        attrs['message'] = f'Sad :(, Time ran out. Correct Answer: {original_attrs["word"]}'
                        attrs['success'] = False
                else:

                    attrs['score'] = 0
                    attrs['message'] = f'Sad :(, Guesses ran out. Correct Answer: {original_attrs["word"]}'
                    attrs['success'] = False
        
    return game(request, 'main/wordle_game.html', 'wordle', attrs)
