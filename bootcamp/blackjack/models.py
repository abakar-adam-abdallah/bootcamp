# from django.db import models

# # Create your models here.

# # class Person(models.Model):
# #     first_name = models.CharField(max_length=30)
# #     last_name = models.CharField(max_length=30)


# class Game(models.Model):
#     name = models.CharField(max_length=250)
#     turn = models.IntegerField(default=0)
#     ended = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name

# class Player(models.Model):
#     name = models.CharField(max_length=50)
#     score = models.IntegerField(default=0)
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
#     stand = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.name} ({self.score})"

# ------------------

# from django.db import models


# class Student(models.Model):
#     name = models.CharField(max_length=150)
#     email = models.EmailField(unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-id"]

#     def __str__(self):
#         return f"{self.name} <{self.email}>"


# class Game(models.Model):
#     name = models.CharField(max_length=250)
#     turn = models.IntegerField(default=0)
#     ended = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-id"]

#     def __str__(self):
#         return f"Game({self.name})"


# class Player(models.Model):
#     name = models.CharField(max_length=100)
#     score = models.IntegerField(default=0)
#     stand = models.BooleanField(default=False)
#     game = models.ForeignKey(Game, related_name="players", on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-id"]

#     def __str__(self):
#         return f"{self.name} (g#{self.game_id})"


# ----------------







from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=250)
    turn = models.IntegerField(default=0)
    ended = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Player(models.Model):
    game = models.ForeignKey(Game, related_name="players", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    stand = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.name} ({self.game_id})"
