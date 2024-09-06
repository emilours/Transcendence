from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models, transaction
from django.conf import settings
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# ================================================================================================================================================================
# ===                                                                 CUSTOM USER                                                                             ====
# ================================================================================================================================================================

class CustomUserManager(BaseUserManager):
    @transaction.atomic
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    display_name = models.CharField(max_length=100, unique=True) 
    avatar = models.FileField(upload_to='static/img/avatars/', default='static/img/avatars/defaultPusheen.png')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_online = models.BooleanField(default=True)

    victories = models.PositiveIntegerField(default=0)
    defeats = models.PositiveIntegerField(default=0)

    friends_count = models.PositiveIntegerField(default=0)
    sent_requests_count = models.PositiveIntegerField(default=0)
    received_requests_count = models.PositiveIntegerField(default=0)
    accepted_requests_count = models.PositiveIntegerField(default=0)
    declined_requests_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    # TESTS TO BE DONE
    def clean(self):
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({'email': 'This mail address is already in use.'})
        
        if CustomUser.objects.filter(display_name=self.display_name).exclude(pk=self.pk).exists():
            raise ValidationError({'display_name': 'This display name is already in use.'})
    
    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)

        if created and not hasattr(self, 'friend_list'):
            FriendList.objects.get_or_create(user=self)

# # ================================================================================================================================================================
# # ===                                                      FRIEND LIST                                                                                         ===
# # ================================================================================================================================================================

class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend_list")
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friend_lists")

    def __str__(self):
        return f"{self.user.username}'s Friend List"

    def add_friend(self, account):
        if account != self.user and account not in self.friends.all():
            with transaction.atomic():
                self.friends.add(account)
                friend_list = FriendList.objects.get(user=account)
                friend_list.friends.add(self.user)

    def remove_friend(self, account):
        if account != self.user and account in self.friends.all():
            with transaction.atomic():
                self.friends.remove(account)
                friend_list = FriendList.objects.get(user=account)
                friend_list.friends.remove(self.user)

    # def unfriend(self, removee):
    #     self.remove_friend(removee)
    #     try:
    #         friends_list = FriendList.objects.get(user=removee)
    #         friends_list.remove_friend(self.user)
    #     except FriendList.DoesNotExist:
    #         pass

    def unfriend(self, removee):
        self.remove_friend(removee)
        try:
            friends_list = FriendList.objects.get(user=removee)
            friends_list.remove_friend(self.user)
            FriendRequest.objects.filter(
                (models.Q(sender=self.user) & models.Q(receiver=removee)) |
                (models.Q(sender=removee) & models.Q(receiver=self.user))
            ).delete()
        except FriendList.DoesNotExist:
            pass

    def is_mutual_friend(self, friend):
        return friend in self.friends.all()

    def friend_count(self):
        count = self.friends.count()
        return count

# # ================================================================================================================================================================
# # ===                                                      FRIEND REQUEST                                                                                      ===
# # ================================================================================================================================================================

from django.db import models, transaction

class FriendRequest(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ], default='pending')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.sender.sent_requests_count += 1
            self.receiver.received_requests_count += 1
            self.sender.save()
            self.receiver.save()
        super().save(*args, **kwargs)

    @transaction.atomic
    def accept(self):
        if self.status == 'pending':
            self.status = 'accepted'
            self.sender.friends_count += 1
            self.receiver.friends_count += 1
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1
            self.sender.save()
            self.receiver.save()
        
        sender_friend_list, _ = FriendList.objects.get_or_create(user=self.sender)
        receiver_friend_list, _ = FriendList.objects.get_or_create(user=self.receiver)
        
        sender_friend_list.add_friend(self.receiver)
        receiver_friend_list.add_friend(self.sender)
        
        self.save()

    @transaction.atomic
    def decline(self):
        if self.status == 'pending':
            self.status = 'declined'
            self.receiver.declined_requests_count += 1
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1
            self.sender.save()
            self.receiver.save()
            self.save()

    @transaction.atomic
    def cancel(self):
        if self.status == 'pending':
            self.status = 'declined'
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1
            self.sender.save()
            self.receiver.save()
            self.save()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.status == 'pending':
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1
            self.sender.save()
            self.receiver.save()
        super(FriendRequest, self).delete(*args, **kwargs)

    @staticmethod
    def count_declined_requests(user):
        return (
            FriendRequest.objects.filter(sender=user, status='declined').count() +
            FriendRequest.objects.filter(receiver=user, status='declined').count()
        )

# # ================================================================================================================================================================
# # ===                                                      MATCH HISTORY                                                                                     ===
# # ================================================================================================================================================================

# class Game(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()

#     def __str__(self):
#         return self.name

# class Match(models.Model):
#     GAME_CHOICES = [
#         ('game1', 'Game 1'),
#         ('game2', 'Game 2'),
#     ]
#     game = models.CharField(max_length=5, choices=GAME_CHOICES)
#     player1 = models.ForeignKey(CustomUser, related_name='player1_matches', on_delete=models.CASCADE)
#     player2 = models.ForeignKey(CustomUser, related_name='player2_matches', on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now_add=True)
#     player1_score = models.IntegerField()
#     player2_score = models.IntegerField()
#     winner = models.ForeignKey(CustomUser, related_name='won_matches', on_delete=models.CASCADE)
#     details = models.TextField()

#     def __str__(self):
#         return f"{self.get_game_display()} match between {self.player1} and {self.player2} on {self.date}"
