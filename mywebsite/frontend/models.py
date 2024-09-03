from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings

# ================================================================================================================================================================
# ===                                                                 CUSTOM USER                                                                             ====
# ================================================================================================================================================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # Create the user's FriendList
        FriendList.objects.create(user=user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, unique=True)
    avatar = models.FileField(upload_to='img/avatars/', default='img/avatars/defaultPusheen.png')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    victories = models.PositiveIntegerField(default=0)
    defeats = models.PositiveIntegerField(default=0)

    sent_requests_count = models.PositiveIntegerField(default=0)
    received_requests_count = models.PositiveIntegerField(default=0)
    accepted_requests_count = models.PositiveIntegerField(default=0)
    declined_requests_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    objects = CustomUserManager()

    def get_pending_friend_requests(self):
        return FriendRequest.objects.filter(receiver=self, is_active=True)

    def get_sent_friend_requests(self):
        return FriendRequest.objects.filter(sender=self, is_active=True)

    def __str__(self):
        return self.email

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
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account != self.user and account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def unfriend(self, removee):
        self.remove_friend(removee)
        try:
            friends_list = FriendList.objects.get(user=removee)
            friends_list.remove_friend(self.user)
        except FriendList.DoesNotExist:
            pass

    def is_mutual_friend(self, friend):
        return friend in self.friends.all()

    def friend_count(self):
        return self.friends.count()

# # ================================================================================================================================================================
# # ===                                                      FRIEND REQUEST                                                                                      ===
# # ================================================================================================================================================================

class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} (Active: {self.is_active})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only update counters when the request is first created
            self.sender.sent_requests_count += 1
            self.receiver.received_requests_count += 1
            self.sender.save()
            self.receiver.save()
        super(FriendRequest, self).save(*args, **kwargs)

    def accept(self):
        if self.is_active:
            try:
                receiver_friend_list = FriendList.objects.get(user=self.receiver)
                sender_friend_list = FriendList.objects.get(user=self.sender)

                receiver_friend_list.add_friend(self.sender)
                sender_friend_list.add_friend(self.receiver)

                self.is_active = False  # Deactivate the friend request
                self.sender.friends_count += 1
                self.receiver.friends_count += 1

                self.save()
                self.sender.save()
                self.receiver.save()

            except FriendList.DoesNotExist:
                print(f"Friend list does not exist for sender or receiver.")
            except Exception as e:
                print(f"An error occurred while accepting the friend request: {str(e)}")

    def decline(self):
        if self.is_active:
            self.is_active = False
            self.receiver.declined_requests_count += 1

            self.save()
            self.receiver.save()

    def cancel(self):
        if self.is_active:
            self.is_active = False
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1

            self.save()
            self.sender.save()
            self.receiver.save()

    def delete(self, *args, **kwargs):
        if self.is_active:
            self.sender.sent_requests_count -= 1
            self.receiver.received_requests_count -= 1
            self.sender.save()
            self.receiver.save()
        super(FriendRequest, self).delete(*args, **kwargs)

    @staticmethod
    def count_declined_requests(user):
        return (
            FriendRequest.objects.filter(sender=user, is_active=False).count() +
            FriendRequest.objects.filter(receiver=user, is_active=False).count()
        )
