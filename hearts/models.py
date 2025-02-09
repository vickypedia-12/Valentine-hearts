from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ZODIAC_CHOICES = [
        ('ARI', 'Aries'), ('TAU', 'Taurus'), ('GEM', 'Gemini'),
        ('CAN', 'Cancer'), ('LEO', 'Leo'), ('VIR', 'Virgo'),
        ('LIB', 'Libra'), ('SCO', 'Scorpio'), ('SAG', 'Sagittarius'),
        ('CAP', 'Capricorn'), ('AQU', 'Aquarius'), ('PIS', 'Pisces'),
    ]
    GENDER_CHOICES = [
        ('MALE', 'Male'), 
        ('FEMALE', 'Female'), 
        ('OTHER', 'Other'),
    ]
    PREFERENCE_CHOICES = [
        ('MALE', 'Men'), 
        ('FEMALE', 'Women'), 
        ('BOTH', 'Both'),
        ('OTHER', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True) 
    interests = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=True)
    preferences = models.CharField(max_length=6, choices=PREFERENCE_CHOICES, blank=True)
    zodiac_sign = models.CharField(max_length=3,choices=ZODIAC_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            return age
        return None

class Question(models.Model):
    text = models.CharField(max_length=100)
    choices = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
    def create_default_questions(cls):
        questions = [
            {
                "text": "What's your idea of a perfect date?",
                "choices": ["Dinner and movie", "Adventure activity", "Quiet evening at home", "Cultural event"]
            },
            {
                "text": "How do you prefer to communicate?",
                "choices": ["Texting", "Phone calls", "Face to face", "Social media"]
            },
            {
                "text": "What's most important in a relationship?",
                "choices": ["Trust", "Communication", "Romance", "Common interests"]
            },
            {
                "text": "How do you spend your free time?",
                "choices": ["Outdoor activities", "Reading/Gaming", "Socializing", "Creative hobbies"]
            },
            {
                "text": "What's your love language?",
                "choices": ["Words of affirmation", "Physical touch", "Acts of service", "Quality time", "Gifts"]
            }
        ]
        
        for q in questions:
            cls.objects.get_or_create(
                text=q["text"],
                defaults={"choices": q["choices"]}
            )
        

class QuestionResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)  

    class Meta: 
        unique_together = ['user', 'question']

    def __str__(self):
        return f"{self.user.username}'s response to {self.question.text}"

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matcher')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matched')
    compatibility_score = models.FloatField()
    revealed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reveal_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        sender_name = "Anonymous" if self.is_anonymous else self.sender.username
        return f"Message from {sender_name} to {self.receiver.username}"
