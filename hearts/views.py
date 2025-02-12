from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import Profile, Question, QuestionResponse, Match, Message
from .forms import UserRegistrationForm, ProfileForm, QuestionnaireForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            login(request, user)
            return redirect('hearts:home')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
    
    return render(request, 'hearts/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def home(request):
    total_users = User.objects.count()
    total_matches = Match.objects.count()
    context = {
        'total_users': total_users,
        'total_matches': total_matches,
        'is_valentine': False, 
    }
    return render(request, 'hearts/home.html', context)

@login_required
def profile(request):
    profile = Profile.objects.get(user = request.user)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('hearts:profile')
    else: 
        profile_form = ProfileForm(instance=profile)
    context = {
        'profile': profile,
        'profile_form': profile_form,
    }
    return render(request, 'hearts/profile.html', context)

@login_required
def questionnaire(request):
    if Question.objects.count() == 0:
        Question.create_default_questions()
    
    questions = Question.objects.all()
    answered_questions = QuestionResponse.objects.filter(user=request.user).values_list('question', flat=True)
    unanswered_questions = questions.exclude(id__in=answered_questions)
    
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, questions=questions, user=request.user)
        if form.is_valid():
            for field_name, answer in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = Question.objects.get(id=question_id)
                    # Only create response if it doesn't exist
                    QuestionResponse.objects.get_or_create(
                        user=request.user,
                        question=question,
                        defaults={'answer': answer}
                    )
            return redirect('hearts:matches')
    else:
        form = QuestionnaireForm(questions=questions, user=request.user)
    
    progress = 0
    if questions.count() > 0:
        progress = (len(answered_questions) / questions.count()) * 100
    
    context = {
        'form': form,
        'progress': progress,
        'total_questions': questions.count(),
        'answered_questions': len(answered_questions),
    }
    return render(request, 'hearts/questionnaire.html', context)

@login_required
def matches(request):
    ZODIAC_COMPATIBILITY = {
        'ARI': ['LEO', 'SAG', 'GEM', 'AQU'],
        'TAU': ['VIR', 'CAP', 'CAN', 'PIS'],
        'GEM': ['LIB', 'AQU', 'ARI', 'LEO'],
        'CAN': ['SCO', 'PIS', 'TAU', 'VIR'],
        'LEO': ['ARI', 'SAG', 'GEM', 'LIB'],
        'VIR': ['TAU', 'CAP', 'CAN', 'SCO'],
        'LIB': ['GEM', 'AQU', 'LEO', 'SAG'],
        'SCO': ['CAN', 'PIS', 'VIR', 'CAP'],
        'SAG': ['ARI', 'LEO', 'LIB', 'AQU'],
        'CAP': ['TAU', 'VIR', 'SCO', 'PIS'],
        'AQU': ['GEM', 'LIB', 'ARI', 'SAG'],
        'PIS': ['CAN', 'SCO', 'TAU', 'CAP']
    }

    user_profile = Profile.objects.get(user=request.user)
    user_responses = QuestionResponse.objects.filter(user=request.user)
    
    if not user_responses.exists():
        return render(request, 'hearts/matches.html', {
            'message': 'Please complete the questionnaire to find matches!',
            'has_matches': False
        })

    # Filter potential matches based on gender preferences
    potential_matches = Profile.objects.filter(
        Q(gender__in=[user_profile.preferences]) & 
        Q(preferences__in=[user_profile.gender]) &  
        ~Q(user=request.user) 
    )

    matches = []
    for profile in potential_matches:
        their_responses = QuestionResponse.objects.filter(user=profile.user)
        if their_responses.exists():
            # Calculate questionnaire compatibility
            matching_answers = 0
            total_questions = min(user_responses.count(), their_responses.count())
            
            for ur in user_responses:
                their_answer = their_responses.filter(question=ur.question).first()
                if their_answer and ur.answer == their_answer.answer:
                    matching_answers += 1
            
            questionnaire_compatibility = (matching_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate zodiac compatibility
            zodiac_compatibility = 0
            if profile.zodiac_sign in ZODIAC_COMPATIBILITY.get(user_profile.zodiac_sign, []):
                zodiac_compatibility = 100
            elif user_profile.zodiac_sign in ZODIAC_COMPATIBILITY.get(profile.zodiac_sign, []):
                zodiac_compatibility = 80
            else:
                zodiac_compatibility = 40

            # Calculate interest compatibility
            interest_compatibility = 0
            user_interests = set(user_profile.interests.lower().split(','))
            their_interests = set(profile.interests.lower().split(','))
            common_interests = user_interests.intersection(their_interests)
            interest_compatibility = len(common_interests) * 20  # Max 100 if 5 interests match

            # Calculate age difference
            age_difference_compatibility = 0
            user_age = user_profile.get_age()
            their_age = profile.get_age()
            age_difference = None
            if user_age and their_age:
                age_difference = abs(user_age - their_age)
                if age_difference <= 5:
                    age_difference_compatibility = 100
                elif age_difference <= 10:
                    age_difference_compatibility = 70
                else:
                    age_difference_compatibility = 40

            # Calculate overall compatibility (30% questionnaire, 30% zodiac, 20% interests, 20% age)
            overall_compatibility = (questionnaire_compatibility * 0.3) + (zodiac_compatibility * 0.3) + (interest_compatibility * 0.2) + (age_difference_compatibility * 0.2)
            
            # Create or update match record
            match, created = Match.objects.get_or_create(
                user1=request.user,
                user2=profile.user,
                defaults={'compatibility_score': overall_compatibility}
            )
            
            if not created:
                match.compatibility_score = overall_compatibility
                match.save()
            
            matches.append({
                'profile': profile,
                'compatibility': overall_compatibility,
                'questionnaire_compatibility': questionnaire_compatibility,
                'zodiac_compatibility': zodiac_compatibility,
                'interest_compatibility': interest_compatibility,
                'age_difference': age_difference,
                'match_id': match.id,
                'revealed': match.revealed,
                'zodiac_match': profile.zodiac_sign in ZODIAC_COMPATIBILITY.get(user_profile.zodiac_sign, [])
            })

    # Sort matches by overall compatibility
    matches.sort(key=lambda x: x['compatibility'], reverse=True)
    
    return render(request, 'hearts/matches.html', {
        'matches': matches,
        'has_matches': True,
        'user_zodiac': user_profile.zodiac_sign
    })

@login_required
def reveal_match(request, match_id):
    try:
        match = Match.objects.get(id=match_id, user1=request.user)
        if request.method == 'POST':
            match.revealed = True
            match.save()
            messages.success(request, 'Match revealed successfully!')
        return redirect('hearts:matches')
    except Match.DoesNotExist:
        messages.error(request, 'Match not found.')
        return redirect('hearts:matches')

@login_required
def messages(request):
    return render(request, 'hearts/messages.html')

@login_required
def confessions(request):
    return render(request, 'hearts/confessions.html')