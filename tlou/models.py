from typing import Match, Tuple
from django.db import models
# from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.expressions import F
from django.db.models.fields import BLANK_CHOICE_DASH, DateField
from django.db.models.fields.related import ForeignKey
from django.http import request
from django.utils.text import slugify
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField


from django.utils import timezone, tree
import datetime
import json
import pytz


from .countries import country_timezones, country_names, country_flags
from django.db.models.signals import post_save
from .utils import EloRating


utc= pytz.timezone("Europe/London")
# Create your models here.
jsonDec = json.decoder.JSONDecoder()



class News(models.Model):
    title=models.CharField(max_length=400)
    image=models.ImageField(upload_to="media/News")
    Description= RichTextField()
    time = models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=True)
    rank=models.IntegerField(default=0)

    class Meta:
        verbose_name = 'New'

    def __str__(self):
        return self.title




class userdtl(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    invitation = models.ManyToManyField('Team', null=True, blank=True)
    twitter = models.CharField(max_length=300, default=None, null=True, blank=True)
    youtube = models.CharField(max_length=300, default=None, null=True, blank=True)
    twitch = models.CharField(max_length=300, default=None, null=True, blank=True)
    bpass = models.CharField(max_length=50, default="")
    add1 = models.CharField(max_length=500, null=True, blank=True)
    add2 = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    gold_trophy = models.IntegerField(default=0)
    silver_trophy = models.IntegerField(default=0)
    bronze_trophy = models.IntegerField(default=0)
    user_win = models.IntegerField(default=0)
    user_lose = models.IntegerField(default=0)
    tpass = models.CharField(max_length=500, default="")
    psn = models.CharField(max_length=500, default="")
    img_user =  models.ImageField(default="media/profile/LOGO_BLACK_PNG.png", upload_to="media/profile", null=True, blank=True)
    team_left = models.DateTimeField(null=True, blank=True)
    country = models.CharField(max_length=64, choices=country_names, default="United Kingdom")
    flag = models.CharField(max_length=200, choices=country_flags, default="https://restcountries.eu/data/gbr.svg")
    # timezone_user = models.CharField(max_length=200, choices=country_timezones, default="Europe/London")
    timezone_user = models.CharField(max_length=200, default="Europe/London")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    forgot_access = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "User Detail"
    def __str__(self):
        return self.user.username

   

    def total_matches(self):
        total = self.user_win + self.user_lose
        return total

    def win_ratio(self):
        if self.user_win != 0:
            return  int(self.user_win /( self.user_win + self.user_lose ) * 100)
        return 0

    def country_select(self):
        for c in country_flags:
            if c[1] == self.country:
                try:
                    self.flag = c[0]
                except:
                    pass


class BanIp(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    temporary_ban = models.BooleanField(null=True, blank=True)
    permanent_ban = models.BooleanField(null=True, blank=True)
    ban_until = models.DateTimeField(null=True, blank=True)

    def is_still_ban(self):
        ban = True
        if datetime.datetime.now().astimezone(pytz.timezone("Europe/London")) > self.ban_until.astimezone(pytz.timezone("Europe/London")) and self.temporary_ban:
            ban = False
            self.delete()
        return ban

class Games(models.Model):
    Name=models.CharField(max_length=400)
    image=models.ImageField(upload_to="media/Games")
    time = models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=True)
    rank=models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Game'

    def __str__(self):
        return self.Name


class Ladders(models.Model):
    Name = models.CharField(max_length=400)
    game = models.ForeignKey(Games, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to="media/Ladders")
    console = models.CharField(max_length=100)
    minmembers = models.IntegerField(default="3")
    maxmembers = models.IntegerField(default="11")
    region = models.CharField(max_length=100)
    season = models.IntegerField(default=0)
    teams = models.ManyToManyField('Team', blank=True, null=True)
    matches_played = models.IntegerField(default=0)
    lock_ladder = models.BooleanField(default=False)
    rules = RichTextField()
    playoff_info = RichTextField()
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    rank = models.IntegerField(default=0)
    end_ladder = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'View Ladder'

    def __str__(self):
        return self.Name

    def is_finished(self):
    
        public = False
        
        if datetime.datetime.now().astimezone(pytz.timezone("Europe/London")) > self.end_date.astimezone(pytz.timezone("Europe/London")):
            public = True
            self.end_ladder = public
            self.lock_ladder = public
            self.save()

        return public
    
    def count_down(self):
        import math
        t = self.end_date.astimezone(pytz.timezone("Europe/London")).replace(microsecond = 0) - datetime.datetime.now().astimezone(pytz.timezone("Europe/London")).replace(microsecond = 0)
       
        return t

class Contact(models.Model):
    name = models.CharField(max_length=128)
    message = RichTextField()
    email = models.EmailField()
    contacted_at = models.DateTimeField(auto_now_add=True)


class Banner(models.Model):
    Heading = models.CharField(max_length=400)
    content = RichTextField()
    time = models.DateTimeField(null=False)
    image = models.ImageField(upload_to="media/Banner", null=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.Heading

class sliders(models.Model):
    Heading=models.CharField(max_length=400)
    SubHeading=models.CharField(max_length=400, null=True)
    link=models.CharField(max_length=400, default="#")
    image=models.ImageField(upload_to="media/Sliders", null=True)
    active=models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Slider'
    
    def __str__(self):
        return self.Heading

class Social(models.Model):
    name=models.CharField(max_length=100)
    link=models.CharField(max_length=400, default="#")
    faicon=models.CharField(max_length=100, default="fa-facebook")
    def __str__(self):
        return self.name

class MapList(models.Model):
    name = models.CharField(max_length=120)
    img = models.ImageField(upload_to="media/maps", null=True, blank=True)
    ladder = models.ForeignKey(Ladders, on_delete=models.CASCADE, related_name="map_ladders")

class image(models.Model):
    title=models.CharField(max_length=400)
    image=models.ImageField(upload_to="media/Sliders", null=True)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.title


class Team(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="media/Teams", null=True,blank=True, default="media/profile/LOGO_BLACK_PNG.png")
    ladder = models.ForeignKey(Ladders, on_delete=models.DO_NOTHING, null=True,blank=True)
    Win = models.IntegerField(default=0)
    Lose = models.IntegerField(default=0)
    gold_trophy = models.IntegerField(default=0)
    silver_trophy = models.IntegerField(default=0)
    bronze_trophy = models.IntegerField(default=0)
    about = RichTextField(max_length=500, null=True, blank=True)
    founded_at = models.DateField(auto_now_add=True)
    match_request = models.ManyToManyField('Matches', null=True, blank=True)
    streak = models.TextField(null=True, blank=True, default="[]")
    rating = models.IntegerField(default=1000)
    crown = models.BooleanField(default=False)
    banner = models.ImageField(upload_to="media/Teams", null=True, blank=True)
    crown_held = models.IntegerField(default=0)
    rating_per_match = models.TextField(default="[]")

    def check_limit(self):
        member = Member.objects.filter(team=self)

        if self.ladder.maxmembers < len(member):
            return True
        return False

        


    def match_rate(self):
        lis = jsonDec.decode(self.rating_per_match)
        for i in lis:
            t = i.split("|")
            mat = Match.object.filter(id=self.id) 
        
            
            return t[0]
                

    def total_trophies(self):
        return self.gold_trophy + self.silver_trophy + self.bronze_trophy

    def longest_streak(self):
        lis = jsonDec.decode(self.streak)
        count = 0
        max_repeat = 0
        for i in range( len(lis) - 1, -1, -1):
            if lis[i] == 0:
                if count > max_repeat:
                    max_repeat = count 
            else:
                count += 1
        return max_repeat

    def win_streak(self):
        lis = jsonDec.decode(self.streak)
        count = 0
        for i in range( len(lis) - 1, -1, -1):
            if lis[i] == 0:
                break
            else:
                count += 1
        return count
    def total_matches(self):
        total = self.total = self.Win + self.Lose
        return total

    def win_ratio(self):
        if self.Win != 0:
            return  int(self.Win /( self.Win + self.Lose ) * 100)
        return 0

    def __str__(self):
        return f"{self.name}"

class Member(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    RANK_CHOICES = (
        ("Leader", "Leader"),
        ("Captain", "Captain"),
        ("Member", "Member")
    )
    rank = models.CharField(max_length=34, choices=RANK_CHOICES, default="Member")
    team_joined = models.DateTimeField(auto_now_add=True)
    
    def is_leader(self):
        leader = False
        if self.rank == "Leader":
            leader = True
        return leader
    
    def has_access(self):
        leader = False
        if self.rank == "Leader" or self.rank == "Captain":
            leader = True
        return leader

    def __str__(self):
        return f"{self.member}"

class Maps(models.Model):
    host = models.ForeignKey(Team, null=True, blank=True, on_delete=models.CASCADE, related_name="map_host")
    rules = RichTextField()
    img_url = models.CharField(max_length=300, null=True, blank=True)
    map_name = models.CharField(max_length=50)        
    match = models.ForeignKey('Matches', null=True, blank=True, on_delete=models.CASCADE, related_name="map_matches")

    class Meta:
        verbose_name = 'Map'

class Matches(models.Model):
    MATCHES = (
        ("Best of 1", "Best of 1"),
        ("Best of 3", "Best of 3"),
        ("Best of 5", "Best of 5"),
    )
    PLAYERS = (
        ("3v3", "3v3"),
        ("4v4", "4v4"),
        ("5v5", "5v5"),
    )
    match_type = models.CharField(max_length=34, default="Best of 1")
    players = models.CharField(max_length=34, default="3v3")
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="Team_A", null=True, blank=True)
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="Team_B", null=True, blank=True)
    match_ladder = models.ForeignKey(Ladders, on_delete=models.CASCADE, related_name="ladders_match")
    time = models.DateTimeField()
    public = models.BooleanField(default=True)
    members_list = models.TextField(null=True)
    result = models.BooleanField(default=False)
    STATUS = [
        ('In-Progress', 'In-Progress'),
        ('Disputed', 'Disputed'),
        ('Completed', 'Completed')
    ]
    status = models.CharField(max_length=128, default="In-Progress")
    winner = models.CharField(max_length=64 ,null=True,blank=True)
    cancel_request_1 = models.BooleanField(default=False)
    cancel_request_2 = models.BooleanField(default=False)
    team_one_rating = models.CharField(max_length=64, default="")
    team_two_rating = models.CharField(max_length=64, default="")
    disputed = models.BooleanField(default=False)
    challenged_team = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = "Manage Matche"

    def __str__(self):
        return f"{self.team_1} vs {self.team_2}- ID {self.id}"

    def no_show_time(self):
        timeadd = self.time + datetime.timedelta(minutes=10)
        try:
            tz = pytz.timezone(exposed_request.user.userdtl.timezone_user)
        
            time = self.time + datetime.timedelta(minutes=10)
            t = time.astimezone(tz)
        
            # d = datetime.datetime.strptime(str(time), '%Y-%m-%d %M:%H')
            d = datetime.datetime.strptime(str(t)[:-6], '%Y-%m-%d %H:%M:%S')
            
            return d
        except:
            return timeadd

    def check_showtime(self):
        
        if self.convert_time() > self.no_show_time():
            return False
        return True

    def check_dispute(self):
        dispute = False
        try:
            rep_1 = ReportTeamOne.objects.get(match=self)
        except:
            rep_1 = None
        try:
            rep_2 = ReportTeamTwo.objects.get(match=self)
        except:
            rep_2 = None
        if rep_1 != None and rep_1.claims == True and rep_2 != None and rep_2.claims == True:
            dispute = True

        return dispute


    def finalize(self):
        result = False
        try:
            rep_1 = ReportTeamOne.objects.get(match=self)
            
        except:
            rep_1 = None
        try:
            rep_2 = ReportTeamTwo.objects.get(match=self)
           
        except:
            rep_2 = None
        
        if self.check_dispute() == False:
            if rep_1 != None and rep_1.claims == False:
                self.team_1.Win = self.team_1.Win + 1 
                if self.team_1.crown == False:
                    self.team_1.crown_held = self.team_1.crown + 1
                lis = jsonDec.decode(self.team_1.streak)
                lis.append(1)
                self.team_1.streak = json.dumps(lis)
                self.team_1.save(update_fields=['Win', 'streak', 'crown_held'])
                
                for m in self.sort_team_A():
                    m.member.userdtl.user_win = m.member.userdtl.user_win + 1
                    m.member.userdtl.save()
                for m in self.sort_team_B():
                    m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
                    m.member.userdtl.save()
                
                self.team_2.Lose = self.team_2.Lose + 1
                lis_ = jsonDec.decode(self.team_2.streak)
                lis_.append(0)
                self.team_2.streak = json.dumps(lis_)
                self.team_2.save(update_fields=['Lose', 'streak'])
                
                self.winner = self.team_1.name  
                d = 1 

            if rep_2 != None and rep_2.claims == False:
                self.team_2.Win = self.team_2.Win + 1 
                if self.team_2.crown == False:
                    self.team_2.crown_held = self.team_2.crown + 1
                lis_ = jsonDec.decode(self.team_2.streak)
                lis_.append(1)
                self.team_2.streak = json.dumps(lis_)
                self.team_2.save(update_fields=['Win', 'streak', 'crown_held'])

                for m in self.sort_team_B():
                    m.member.userdtl.user_win = m.member.userdtl.user_win + 1
                    m.member.userdtl.save()
                for m in self.sort_team_A():
                    m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
                    m.member.userdtl.save()

                self.team_1.Lose = self.team_1.Lose + 1 
                lis = jsonDec.decode(self.team_1.streak)
                lis.append(0)
                self.team_1.streak = json.dumps(lis)
                self.team_1.save(update_fields=['Lose', 'streak'])

                self.winner = self.team_2.name  
                d = 2
            
            elo = EloRating(self.team_1.rating, self.team_2.rating, 30, d, self.team_1.crown, self.team_2.crown  )
            
            per_rate = elo[0] - self.team_1.rating
            self.team_one_rating = per_rate

            self.team_1.rating = elo[0]
            self.team_1.crown = elo[2]
            
       
            per_rate = elo[1] - self.team_2.rating
            
            self.team_two_rating = per_rate
            self.team_2.rating = elo[1]
            self.team_2.crown = elo[3]

            self.team_1.save(update_fields=["rating", "crown", "rating_per_match"])
            self.team_2.save(update_fields=["rating", "crown", "rating_per_match"])
            self.result = True
            self.disputed = False
            self.save(update_fields=['result', 'disputed', 'winner', 'team_one_rating', 'team_two_rating'])
            # self.match.save()
        return result

    def current_stats(self):
        
        if self.in_progress() and self.disputed == False:
            self.status = "In-Progress"
            
            self.save()
            return self.status
            
        if self.winner != "" and self.winner is not None:
            
            self.status = "Completed"
            self.save()
            return self.status
        
        if self.check_dispute() or self.disputed == True:
            self.status = "Disputed"
            self.save()
            return self.status
        


    def convert_time(self):
        try:
            tz = pytz.timezone(exposed_request.user.userdtl.timezone_user)
        
            time = self.time
            t = time.astimezone(tz)
        
            # d = datetime.datetime.strptime(str(time), '%Y-%m-%d %M:%H')
            d = datetime.datetime.strptime(str(t)[:-6], '%Y-%m-%d %H:%M:%S')
            
            return d
        except:
            return self.time

    def in_progress(self):
        prog = False
        if self.active_match():
            
            if self.winner == None or self.winner == '':
                if self.check_dispute() == False:
                    
                    prog = True
            
        return prog

    def is_expired(self):
        
        public = True
        
        if datetime.datetime.now().astimezone(pytz.timezone("Europe/London")) > self.time.astimezone(pytz.timezone("Europe/London")):
            public = False
            self.public = public
            
            if self.team_1 == None or self.team_2 == None:
                self.delete()

        return public
    
    

    def active_match(self):
        is_active = False
        if self.team_1 is not None and self.team_2 is not None:
            is_active = True
        
        return is_active

    def sort_team_A(self):
        try:
            li = []
            if self.team_1 is not None:
                member_team_1 = Member.objects.filter(team=self.team_1)
                lis = jsonDec.decode(self.members_list)
                for idx, m in enumerate(member_team_1):
                    if m.id in lis:
                        # print(Member.objects.get(m.id))
                        li.append(Member.objects.get(id=m.id))    
            return li
        except:
            pass

    def sort_team_B(self):
        try:
            li = []
            if self.team_2 is not None:
                member_team_2 = Member.objects.filter(team=self.team_2)
                lis = jsonDec.decode(self.members_list)
                for idx, m in enumerate(member_team_2):
                    if m.id in lis:
                        # print(Member.objects.get(m.id))
                        li.append(Member.objects.get(id=m.id))    
            
            return li
            
        except:
            pass

class ReportTeamOne(models.Model):
    match = models.ForeignKey('Matches', on_delete=models.CASCADE, related_name="report_one_team")
    proof_1 = models.CharField(max_length=196, null=True, blank=True)
    proof_2 = models.CharField(max_length=196, null=True, blank=True)
    proof_3 = models.CharField(max_length=196, null=True, blank=True)
    msg = models.TextField(null=True, blank=True)
    claims = models.BooleanField(null=True, blank=True)
    reported = models.BooleanField(default=False, null=True, blank=True)

    def win_or_lose(self):
        if self.claims == False:
            return "Lose"
        if self.claims == True:
            return "Win"
        if self.claims == None:
            return "Waiting"

    def checkDispute(self):
        if self.msg != "" and self.msg != None:
            return True
        return False

class ReportTeamTwo(models.Model):
    match = models.ForeignKey('Matches', on_delete=models.CASCADE, related_name="report_two_team")
    proof_1 = models.CharField(max_length=196, null=True, blank=True)
    proof_2 = models.CharField(max_length=196, null=True, blank=True)
    proof_3 = models.CharField(max_length=196, null=True, blank=True)
    msg = models.TextField(null=True, blank=True)
    claims = models.BooleanField(null=True, blank=True)
    reported = models.BooleanField(default=False, null=True, blank=True)

    def win_or_lose(self):
        if self.claims == False:
            return "Lose"
        if self.claims == True:
            return "Win"
        if self.claims == None:
            return "Waiting"

    def checkDispute(self):
        if self.msg != "" and self.msg != None:
            return True
        return False

class Report(models.Model):
    team_1_report = RichTextField(null=True, blank=True)         
    team_2_report = RichTextField(null=True, blank=True)         
    match = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name="MatchReport")
    winner_id_1 = models.IntegerField(null=True, blank=True) 
    winner_id_2 = models.IntegerField(null=True, blank=True) 
    dispute_text_1 = RichTextField(null=True, blank=True)
    dispute_text_2 = RichTextField(null=True, blank=True)
    dispute_proof_1 = models.CharField(max_length=300, null=True, blank=True)
    dispute_proof_2 = models.CharField(max_length=300, null=True, blank=True)

    def final_result(self):
        result = False
        if self.team_1_report == self.team_2_report and self.winner_id_1 == self.winner_id_2:
            self.match.result = True
            

            if self.match.team_1.id == self.winner_id_1:
                
                self.match.team_1.Win = self.match.team_1.Win + 1 
                if self.match.team_1.crown == False:
                    self.match.team_1.crown_held = self.match.team_1.crown + 1
                lis = jsonDec.decode(self.match.team_1.streak)
                lis.append(1)
                self.match.team_1.streak = json.dumps(lis)
                self.match.team_1.save(update_fields=['Win', 'streak', 'crown_held'])
                
                
                self.match.team_2.Lose = self.match.team_2.Lose + 1
                lis_ = jsonDec.decode(self.match.team_2.streak)
                lis_.append(0)
                self.match.team_2.streak = json.dumps(lis_)
                self.match.team_2.save(update_fields=['Lose', 'streak'])
                
                self.match.winner = self.match.team_1.name  
                d = 1
                
            elif self.match.team_2.id == self.winner_id_1:
                
                self.match.team_2.Win = self.match.team_2.Win + 1 
                if self.match.team_2.crown == False:
                    self.match.team_2.crown_held = self.match.team_2.crown + 1
                lis_ = jsonDec.decode(self.match.team_2.streak)
                lis_.append(1)
                self.match.team_2.streak = json.dumps(lis_)
                self.match.team_2.save(update_fields=['Win', 'streak', 'crown_held'])

                self.match.team_1.Lose = self.match.team_1.Lose + 1 
                lis = jsonDec.decode(self.match.team_1.streak)
                lis.append(0)
                self.match.team_1.streak = json.dumps(lis)
                self.match.team_1.save(update_fields=['Lose', 'streak'])

                self.match.winner = self.match.team_2.name  
                d = 2
            
            
            elo = EloRating(self.match.team_1.rating, self.match.team_2.rating, 30, d, self.match.team_1.crown, self.match.team_2.crown  )
            li1 = jsonDec.decode(self.match.team_1.rating_per_match)
            per_rate = elo[0] - self.match.team_1.rating
            li1.append(f"{per_rate} | {self.match.id}")
            self.match.team_1rating_per_match = json.dumps(li1)

            self.match.team_1.rating = elo[0]
            self.match.team_1.crown = elo[2]
            
            li2 = jsonDec.decode(self.match.team_2.rating_per_match)
            per_rate = elo[1] - self.match.team_2.rating
            li2.append(f"{per_rate} | {self.match.id}")
            self.match.team_2.rating_per_match = json.dumps(li2)
            self.match.team_2.rating = elo[1]
            self.match.team_2.crown = elo[3]

            self.match.team_1.save(update_fields=["rating", "crown", "rating_per_match"])
            self.match.team_2.save(update_fields=["rating", "crown", "rating_per_match"])
            self.match.save(update_fields=['result', 'winner'])
            # self.match.save()
            result = True
            return result

    def is_dispute(self):
        
        if self.team_2_report != self.team_1_report:
            
            return True
        return False


class AdminOptions(models.Model):
    about_image = models.ImageField(upload_to="media/support", null=True, blank=True)
    about_info = RichTextField(null=True, blank=True)
    about_info_2 = RichTextField(null=True, blank=True)
    
    contact_email = models.CharField(max_length=128, null=True, blank=True)
    contact_info = RichTextField(null=True, blank=True)

    winner_bool = models.BooleanField(default=False)
    winner_list = models.CharField(max_length=500, null=True, blank=True)
    
    
    notice_text = RichTextField(null=True, blank=True)
    term_and_condition = RichTextField(null=True, blank=True)
    privacy_and_policy = RichTextField(null=True, blank=True)

    news_banner = models.ImageField(upload_to="media/News", null=True, blank=True)
    about_background_banner = models.ImageField(upload_to="media/News", null=True, blank=True)
    contact_banner = models.ImageField(upload_to="media/Banner", null=True, blank=True)
    game_banner = models.ImageField(upload_to="media/Banner", null=True, blank=True)
    
    ladder_banner = models.ImageField(upload_to="media/Banner", null=True, blank=True)
    second_ladder_banner = models.ImageField(upload_to="media/Banner", null=True, blank=True)
    team_background_banner = models.ImageField(upload_to="media/Banner", null=True, blank=True)

    access_name = models.CharField(max_length=128, null=True, blank=True)
    

    class Meta:
        verbose_name = "Web Management"

    def winners(self):
        return self.winner_list  
      

class SocialList(models.Model):
    options = models.ForeignKey(AdminOptions, on_delete=models.CASCADE, null=True, blank=True, related_name="social_media")
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=400, null=True, blank=True)
    faicon = models.CharField(max_length=100, default="fa-facebook", null=True, blank=True)
    



class BanUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    temporary_ban = models.BooleanField(null=True, blank=True)
    permanent_ban = models.BooleanField(null=True, blank=True)
    ban_until = models.DateTimeField()

    def is_still_ban(self):
        ban = True
        if datetime.datetime.now().astimezone(pytz.timezone("Europe/London")) > self.ban_until.astimezone(pytz.timezone("Europe/London")) and self.temporary_ban:
            ban = False
            self.delete()
        return ban


class Video(models.Model):
    admin_option = models.ForeignKey(AdminOptions, on_delete=models.CASCADE , null=True, blank=True, related_name="video_list")
    video_link = models.CharField(max_length=500, null=True, blank=True)
    video_title = models.CharField(max_length=500, null=True, blank=True)