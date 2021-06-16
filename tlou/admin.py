from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import fields
from django.forms import models
from django import forms

from .models import Contact, Maps, BanIp, BanUser, SocialList, Video, AdminOptions, ReportTeamOne, ReportTeamTwo, Matches, MapList, Report, Member,News,Games,Ladders,userdtl,Banner,sliders,Social,image, Team

from django.urls import reverse
from django.utils.safestring import mark_safe    

from django.urls import reverse
from django.utils.http import urlencode

from django.forms import TextInput, FileField, ModelForm
from django.utils.html import format_html



# Register your models here.

admin.site.register(userdtl)
admin.site.register(News)
admin.site.register(BanUser)
admin.site.register(Games)
admin.site.register(sliders)

class BanIPAdmin(admin.ModelAdmin):
    fields = ['ip', 'user', 'ban_until', 'temporary_ban', 'permanent_ban']
    def save_model(self, request, obj, form, change):
        if obj.user != None:
            ip_ = obj.user.userdtl.ip_address
            if ip_ != None:
                obj.ip = ip_
        print("yes")
        super(BanIPAdmin, self).save_model(request, obj, form, change)
    
admin.site.register(BanIp, BanIPAdmin)

class VideosInline(admin.StackedInline):
    model = Video

class SocialInline(admin.StackedInline):
    model = SocialList

class ManagementPanel(admin.ModelAdmin):
    inlines = [VideosInline, SocialInline]

admin.site.register(AdminOptions, ManagementPanel)


    


class MatchForm(ModelForm):
    
    model = Matches
    
admin_link = "/admin/tlou/"
        
class MapInline(admin.StackedInline):
    model = MapList

class ReportInline(admin.StackedInline):
    model = Report
    # inlines = [MatchInline]

class LadderAdmin(admin.ModelAdmin):
    model = Ladders
    inlines = [MapInline]

admin.site.register(Ladders, LadderAdmin)


class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'match_ladder', 'team_1', 'Report_1', 'team_2', 'Report_2', 'current_stats', 'all_actions')
    
    form = MatchForm

    def Report_1(self, obj):
        try:
            report = ReportTeamOne.objects.get(match=obj)
            url = f"{admin_link}reportteamone/{report.id}"
            res = "Lose"
            if report.claims == True:
                res = "Win"
            return format_html('<a href="{}"> {}</a>', url, res )
        except:
            return "Waiting"

    def Report_2(self, obj):
        try:
            report = ReportTeamTwo.objects.get(match=obj)
            url = f"{admin_link}reportteamtwo/{report.id}"
        
            res = "Lose"
            if report.claims == True:
                res = "Win"
            return format_html('<a href="{}"> {}</a>', url, res )
        except:
            return "Waiting"
    def show_disputes(self, obj):
        
        report = Report.objects.get(match=obj)
        url = f"{admin_link}report/{report.id}"
        return format_html('<a href="{}"> Dispute -{}</a>', url, report.id )

    def all_actions(self, obj):

        # url = f"/matches/teamonewin/{obj.id}"
        url = '/tlou/matches/teamonewin'
        url2 = '/tlou/matches/teamtwowin'
        url3 = '/tlou/matches/teamdel'
        return format_html(
            '<a class="button" href="{}/{}">Team 1</a>&nbsp;'
            '<a class="button" href="{}/{}">Team 2</a>&nbsp;'
            '<a class="button deletelink" href="{}/{}">Cancel</a>',url,obj.id,url2, obj.id, url3, obj.id )
    
class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'contacted_at')

admin.site.register(Contact, ContactAdmin)

class TemplateAdmin(admin.ModelAdmin):
 
    change_list_template = 'admin/admin_match.html'
    search_fields = ['id']
    def changelist_view(self, request, extra_context={}): 
        matches = Matches.objects.all()	
        extra_context['matches'] = matches
        return super(TemplateAdmin, self).changelist_view(request, extra_context)

admin.site.register(Matches, TemplateAdmin)



    # match.short_description = "Students"
class ReportAdmin(admin.ModelAdmin):
   
    
    fields = ("proof_1", "proof_2", "proof_3", "msg")
    



class MemberInline(admin.StackedInline):
    model = Member


class TeamDetail(models.ModelForm):
    model = Team
    class Meta:
        fields = ["team", "member", "rank"]

    


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'ladder')
    model = TeamDetail
    inlines = [MemberInline]

admin.site.register(Team, TeamAdmin)