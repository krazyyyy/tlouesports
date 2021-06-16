# from typing_extensions import ParamSpecKwargs
from json.decoder import JSONDecodeError
from django.core.exceptions import RequestAborted
from django.http import HttpResponseRedirect, JsonResponse, request
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string
# Create your views here.

from .models import BanUser, Contact, Matches, BanIp, AdminOptions, ReportTeamTwo, ReportTeamOne, Maps, Report, News, Games, Member, Ladders, userdtl,sliders,Social,image, Team
from .utils import EloRating  
from .countries import country_list, country_timezones
import random, string
from django.utils import timezone


from ipware import get_client_ip
import json
import datetime
import random
import pytz

jsonDec = json.decoder.JSONDecoder()
utc= pytz.timezone("Europe/London")

from django.contrib.auth.models import User




def report_match(request, pk, tid, wl):
    if wl == "True":
        wl = True
    else:
        wl = False
    if not request.user.is_authenticated:
        messages.error(request, "Please Login to report") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    match = Matches.objects.get(id=pk)
    
    if match.check_showtime() == False:
        messages.error(request, "Please Wait You cannot Report at the moment") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    team = Team.objects.get(id=tid)
    if match.team_1 == team:
        if ReportTeamOne.objects.filter(match=match).exists():
            messages.error(request, "You Have Already Reported") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        report = ReportTeamOne(match=match, claims=wl, reported=True)
    if match.team_2 == team:
        if ReportTeamTwo.objects.filter(match=match).exists():
            messages.error(request, "You Have Already Reported") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        report = ReportTeamTwo(match=match, claims=wl, reported=True)
    
    report.save()
    if wl == False:
        match.finalize()
    messages.success(request, "Reported") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def raise_dispute(request, pk, tid):
    if request.method == "POST":
        match = Matches.objects.get(id=pk)
        team = Team.objects.get(id=tid)
        if match.team_1 == team:
            rep = ReportTeamOne.objects.filter(match=match)
            if rep.exists():
                rep = rep[0]
                if rep.checkDispute():
                    messages.error(request, "You Have Already Raised Dispute") 
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
                rep.proof_1 = request.POST['proof-1']
                rep.proof_2 = request.POST['proof-2']
                rep.proof_3 = request.POST['proof-3']
                rep.msg = request.POST['msg']
            else:
                rep = ReportTeamOne(match=match,proof_1=request.POST['proof-1'], proof_2=request.POST['proof-2'], proof_3=request.POST['proof-3'], msg=request.POST['msg'])
        
        elif match.team_2 == team:
            rep = ReportTeamTwo.objects.filter(match=match)
            if rep.exists():
                rep = rep[0]
                if rep.checkDispute():
                    messages.error(request, "You Have Already Raised Dispute") 
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                rep.proof_1 = request.POST['proof-1']
                rep.proof_2 = request.POST['proof-2']
                rep.proof_3 = request.POST['proof-3']
                rep.msg = request.POST['msg']
            else:
                rep = ReportTeamTwo(match=match,proof_1=request.POST['proof-1'], proof_2=request.POST['proof-2'], proof_3=request.POST['proof-3'], msg=request.POST['msg'])
        else:
            messages.error(request, "You Have No Access") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        rep.save()
        messages.success(request, "Disputed") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        match = Matches.objects.get(id=pk)
        team = Team.objects.get(id=tid)
        return render(request, 'tlou/dispute.html', {
            'match' : match,
            'team' : team
        })
def create_dispute(request, pk, tpk):
    if not request.user.is_authenticated:
        messages.error(request, "Please Login to report") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    dispute_description = request.POST.get('description')
    proof = request.POST.get('proof')
    match = Matches.objects.get(id=pk)
    team = Team.objects.get(id=tpk)

    if match.team_1 == team:
        report_ = f"{match.team_1} Won against {match.team_2}"
        report = Report(match=match, team_1_report=report_, dispute_text_1=dispute_description, dispute_proof_1=proof)
    if match.team_2 == team:
        report_ = f"{match.team_2} Won against {match.team_1}"
        report = Report(match=match, team_2_report=report_, dispute_text_2=dispute_description, dispute_proof_2=proof)
    match.result = True

    report.save()
    match.save()
    report.is_dispute()    

    messages.success(request, f"Dispute started for {report.id} / {report.match}, Soon Our Team Will Look in it") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def dispute(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please Login to report") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    report = Report.objects.get(id=pk)
    try:
        member = Member.objects.get(team=report.match.team_1, member=request.user)
    except:
        member = Member.objects.get(team=report.match.team_2, member=request.user)
        

    team = Team.objects.get(ladder=report.match.match_ladder, member=member)
    dispute_description = request.POST.get('description')
    proof = request.POST.get('proof')
    if report.match.team_1 == team:
        # if report.dispute_text_1 != "":
        #     messages.error(request, f"You dispute {report.id} / {report.match} already underway, please be paitent") 
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        report.dispute_text_1 = dispute_description
        report.dispute_proof_1 = proof

    if report.match.team_2 == team:
        # if report.dispute_text_2 != "":
        #     messages.error(request, f"You dispute {report.id} / {report.match} already underway, please be paitent") 
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        report.dispute_text_2 = dispute_description
        report.dispute_proof_2 = proof
    report.save()
    messages.success(request, f"Dispute started for {report.id} / {report.match}, Soon Our Team Will Look in it") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def result(request, pk, tm):
    if not request.user.is_authenticated:
        messages.error(request, "Please Login to report") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    match = Matches.objects.get(id=pk)    
    if match.team_1 == None or match.team_2 == None:
        messages.error(request, "There is No Team Two, Whom You are Going to Report") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    if f"{match.team_1}" == tm:
  
        winner_id = match.team_1.id
        report = f"{match.team_1} Won against {match.team_2}"
    if f"{match.team_2}" == tm:
      
        winner_id = match.team_2.id
        report = f"{match.team_2} Won against {match.team_1}"

    try:
        member = Member.objects.get(team=match.team_1.id, member=request.user) 
        team_1 = Team.objects.get(member=member)
        try:
            result = Report.objects.get(match=match)
            result.team_1_report = report
            result.winner_id_1 = winner_id
        except:
            result = Report(team_1_report=report, winner_id_1=winner_id, match=match)

    except:
        member = Member.objects.get(team=match.team_2.id, member=request.user) 
        team_2 = Team.objects.get(member=member)
        try:
            result = Report.objects.get(match=match)
            result.team_2_report = report
            result.winner_id_2 = winner_id
        except:
            result = Report(team_2_report=report, winner_id_2=winner_id, match=match)
    
    result.save()
    match.save()
    match.team_1.save()
    match.team_2.save()
    result.final_result()
    result.save()
    messages.success(request, "Finish") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
def cancelMatch(request, pk):

    match = Matches.objects.get(id=pk)
    if match.team_2 is not None: 
        messages.success(request, f"{match.team_2}, already accept match requeste") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    match.delete()
    messages.success(request, f"Match Canceled") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def acceptPage(request, pk, tpk):
    match = Matches.objects.get(id=pk)
    team = Team.objects.get(id=tpk)
    members = Member.objects.filter(team=team)

    return render(request, 'tlou/accept.html', {
        "match" : match,
        "team" : team,
        "members" : members
    })
def editTeam(request,pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please Login You have no access to this page") 
        return redirect(index)
    team = Team.objects.get(id=pk)
    try:
        leader = Member.objects.get(team=team, member=request.user, rank="Leader")
    
    except:
        messages.error(request, "Only Team Leader have access to this page") 
        return redirect(index)

    members = Member.objects.filter(team=team)
    allusr = User.objects.all()

    return render(request, 'tlou/edit.html',{
        "team" : team,
        "members" : members,
        "alluser" : allusr,
        "leader" : leader
    })

def renderTeam(request, pk):
    
    team = Team.objects.get(id=pk)
    members = Member.objects.filter(team=team)
    allusr = User.objects.filter(is_staff=False)
    matches = Matches.objects.all()
   
    team_mem = False
    founder = False
    team_2 = None
    challenger_members = None

    for member in members:
        if request.user.is_authenticated and f"{member}" == f"{request.user}":
            team_mem = True
        if member.is_leader() and f"{member.member}" == f"{request.user}":
            founder = True      
    if request.user.is_authenticated:
        member_ = Member.objects.filter(member=request.user)
        if member_.exists(): 
            mem = member_[0]
        else:
            mem = None
        if Team.objects.filter(ladder=team.ladder, member=mem):
            team_2 = Team.objects.filter(ladder=team.ladder, member=Member.objects.filter(member=request.user)[0])
            # timez = team_2.convert_time(mem.userdtl.timezone)
            challenger_members = Member.objects.filter(team=team_2[0])
           
    return render(request, 'tlou/team.html',{
        'team' : team,
        'members' : members,
        'team_member' : team_mem,
        'founder' : founder,
        'alluser' : allusr,
        'team_2' : team_2,
        'matches' : matches,
        'challenger' : challenger_members,
        
    })

def abortRequest(request, pk, tpk):
    match = Matches.objects.get(id=pk)
    team = Team.objects.get(id=tpk)
    if match.cancel_request_1 and team == match.team_1:
        match.cancel_request_2 = False
        match.save()
        messages.success(request, f"Request Aborted") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    elif match.cancel_request_2 and team == match.team_2:
        match.cancel_request_2 = False
        match.save()
        messages.success(request, f"Request Aborted") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, f"No one Request for Match Cancel") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def changeImg(request):
    img = request.FILES.get('img-profile')
    banner = request.FILES.get('img-banner')
    team_id = request.POST.get('team-id')
    team = Team.objects.get(id=team_id)

   
    if banner != None:
     
        team.banner = banner
    if img != None:
        team.image = img
    team.save()
    messages.success(request, f"Team Profile Updated") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def acceptChallenge(request, pk):

    match = Matches.objects.get(id=pk)
    if match.team_2 is None:
        member = Member.objects.get(member=request.user)
        limit = request.POST.get('player-limit')
        count = request.POST.get('player-count')
        if int(count) < int(limit[0]):
            messages.error(request, f"You Do not have enough players to play this match") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
         
        li = []
        for i in range(int(count)):
            
            try:
                li.append(int(request.POST.get(f"member-{i + 1}")))
            except:
                pass
        for j in li:
            m = Member.objects.get(id=j)
            if m.member.userdtl.psn == '':
                messages.error(request, f"{m.member} Haven't set PSN yet, you cannot add him to team") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if match.members_list is None:
            match.members_list = json.dumps(li)
        else:
            lis = jsonDec.decode(match.members_list) 
            lis.extend(li)
            match.members_list = json.dumps(lis)
        
        

        if len(li) > int(limit[0]):
            messages.error(request, f"Please Select Only {limit[0]} player, It is {limit} match") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if len(li) < int(limit[0]):
            messages.error(request, "You Do not Have enough players") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        team = Team.objects.get(ladder=match.match_ladder, member=member)
        if match.challenged_team != None and match.challenged_team != team.name:
            messages.error(request, "This Challenge is for other team!") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        if match.team_1 == team:
            messages.error(request, "You Cannot Respond To Your Own Match") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        date_from = datetime.datetime.now(pytz.timezone("Europe/London")) - datetime.timedelta(minutes=60)
        mat = Matches.objects.filter(time__gte=date_from, match_ladder=match.match_ladder)
       
        for m in mat:

            if m.team_1 == match.team_1 and m.team_2 == team:
                messages.error(request, "You Cannot Play With This Team Before One Hour ") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if m.team_1 == team and m.team_2 == match.team_1:
                messages.error(request, "You Cannot Play With This Team Before One Hour ") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        

        team.ladder.matches_played = team.ladder.matches_played + 1
        

        team.ladder.save()
        match.team_2 = team
        match.public = 'False'
    
        match.save()
        
        maps = team.ladder.map_ladders.all()
        li_ = random.sample(set(maps),int(limit[0]))
        
        for i in range(int(limit[0])):
            if (i % 2) == 0:
                    
                if match.team_1.rating >= team.rating:
                    host = match.team_1 
                if match.team_1.rating <= team.rating:
                    host = team 
                if match.team_1.rating == team.rating:
                    host = match.team_1
            else:
                if match.team_1.rating <= team.rating:
                    host = match.team_1 
                if match.team_1.rating >= team.rating:
                    host = team 
                if match.team_1.rating == team.rating:
                    host = team
            
            map = Maps(host=host, match=match, map_name=li_[i].name, img_url=li_[i].img.url, rules="")
            map.save()

        messages.success(request, "Match Accepted") 
        return redirect('challenge', pk=match.id)
        # return render(request, "tlou/challenge", {
        #     "match" : match
        # })
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "Match Request Already Responded By someone") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def challengePage(request, pk):
    match = Matches.objects.get(id=pk)
    try:
        report = Report.objects.get(match=match)
    except:
        report = None
    try:
        try:
            member = Member.objects.get(member=request.user, team=match.team_1 )
        except:
            member = Member.objects.get(member=request.user, team=match.team_2 )
    except:
        member = None
    return render(request, 'tlou/challengePage.html', {
        "match" : match,
        'report' : report,
        'member' : member,
    })

def postMatch(request):
    if request.user.is_authenticated:
        lad_id = request.POST['ladder_id']
        ld_ = Ladders.objects.get(id=lad_id)
        if ld_.end_ladder:
            messages.error(request, f"Ladder Ended No Access") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        best = request.POST.get('best')
        players = request.POST.get('players')
        time_ = request.POST.get('datetime')
        play = (int(players[0]))
        try:
            total = int(request.POST.get('member-count'))
        except:
            messages.error(request, f"You are Not in any Team") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        today = datetime.date.today()
        d1 = today.strftime("%d/%m/%Y")
        t = (datetime.datetime.strptime(time_, "%H:%M").time())
        datetime_ = datetime.datetime.combine(datetime.date.today(), t)
        user = User.objects.get(username=request.user)
        
        tz_ = pytz.timezone(user.userdtl.timezone_user)
        datetime_ = tz_.localize(datetime_)
        print(datetime_)
        # print(datetime_.astimezone(pytz.timezone('Asia/Kolkata')))
        # raise EOFError
        if play > total:
            messages.error(request, f"You cannot play {players} Match, {play} player required") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        li = []
        for i in range(total):
            try:
                li.append(int(request.POST.get(f"member-{i + 1}")))
            except:
                pass
        for j in li:
            m = Member.objects.get(id=j)
            if m.member.userdtl.psn == '':
                messages.error(request, f"{m.member} Has not set PSN yet, you cannot add him to team") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        if len(li) > int(play):
            messages.error(request, f"Please Select Only {play} player, It is {players} match") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if len(li) < int(play):
            messages.error(request, "You Do not Have enough players") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        li = json.dumps(li)
        
        try:
            print(request.POST['team-1'])
            team_1 = request.POST['team-1']
            team = Team.objects.get(name=team_1)
            ladder = Ladders.objects.get(id=lad_id)
            match = Matches(team_1=team, players=players, match_type=best, match_ladder=ladder, time=datetime_.astimezone(pytz.timezone('Europe/London')), members_list=li)
            match.save()
            
        except:
            # send request if some one challenge
            team_1 = request.POST['team-2']
            req = request.POST['team-1-id']
            
            send_request = Team.objects.get(id=req)
            team = Team.objects.get(name=team_1)
            ladder = Ladders.objects.get(id=lad_id)
            match = Matches(team_1=team, challenged_team=send_request.name, players=players, match_type=best, match_ladder=ladder, time=datetime_.astimezone(pytz.timezone('Europe/London')), public=False, members_list=li)
            match.save()
            send_request.match_request.add(match.id)
            send_request.save()
           
        
        messages.success(request, "Match Posted Successfully") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "Log in to Create Match or Challenge!!") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    if request.user.is_authenticated:
        data = json.loads(request.body)
        print(data)
        lad_id = data['ladder_id']
        print(lad_id)
        ld_ = Ladders.objects.get(id=lad_id)
        if ld_.end_ladder:
            return JsonResponse({"message" : f"Ladder Ended No Access"})
            # messages.error(request, f"Ladder Ended No Access") 
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        best = data['best']
        players = data['players']
        time_ = data['datetime']
        play = (int(players[0]))
        try:
            total = int(data['member-count'])
        except:
            return JsonResponse({"message" :f"You are Not in any Team"}) 
            # messages.error(request, f"You are Not in any Team") 
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        today = datetime.date.today()
        d1 = today.strftime("%d/%m/%Y")
        t = (datetime.datetime.strptime(time_, "%H:%M").time())
        datetime_ = datetime.datetime.combine(datetime.date.today(), t)
        user = User.objects.get(username=request.user)
        
        tz_ = pytz.timezone(user.userdtl.timezone_user)
        datetime_ = tz_.localize(datetime_)
        
        if play > total:
            return JsonResponse({"message" :f"You cannot play {players} Match, {play} player required"}) 
            # messages.error(request, f"You cannot play {players} Match, {play} player required") 
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        li = []
        for i in range(total):
            try:
                li.append(int(request.POST.get(f"member-{i + 1}")))
            except:
                pass
        for j in li:
            m = Member.objects.get(id=j)
            if m.member.userdtl.psn == '':
                return JsonResponse({"message" : f"{m.member} Has not set PSN yet, you cannot add him to team"}) 
                # messages.error(request, f"{m.member} Has not set PSN yet, you cannot add him to team") 
                # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        if len(li) > int(play):
            return JsonResponse({"message": f"Please Select Only {play} player, It is {players} match"}) 
            # messages.error(request, f"Please Select Only {play} player, It is {players} match") 
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        print(len(li) , int(play))
        if len(li) < int(play):
            return JsonResponse({"message" : "You Do not Have enough players"}) 
            # messages.error(request, "You Do not Have enough players") 
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        li = json.dumps(li)
        
        try:
            team_1 = data['team-1']
            team = Team.objects.get(name=team_1)
            ladder = Ladders.objects.get(id=lad_id)
            match = Matches(team_1=team, players=players, match_type=best, match_ladder=ladder, time=datetime_.astimezone(pytz.timezone('Europe/London')), members_list=li)
            match.save()
            
        except:
            # send request if some one challenge
            team_1 = data['team-2']
            req = data['team-1-id']
            
            send_request = Team.objects.get(id=req)
            team = Team.objects.get(name=team_1)
            ladder = Ladders.objects.get(id=lad_id)
            match = Matches(team_1=team, challenged_team=send_request.name, players=players, match_type=best, match_ladder=ladder, time=datetime_.astimezone(pytz.timezone('Europe/London')), public=False, members_list=li)
            match.save()
            send_request.match_request.add(match.id)
            send_request.save()
           
        return JsonResponse({"status" : "success"})
        # messages.success(request, "Match Posted Successfully") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "Log in to Create Match or Challenge!!") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cancelMatchReq(request, pk):
    match = Matches.objects.get(id=pk)

    if match.cancel_request_1 or match.cancel_request_2:
        messages.error(request, "Any One Team Have Already Request For Cancel Match!!!") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    list_ = jsonDec.decode(match.members_list)
    for lis in list_:
        member = Member.objects.filter(id=lis, member=request.user)
        
        if member.exists():
            break
    if not member.exists():
        messages.error(request, "You Have No Access!!") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    team = Team.objects.get(ladder=match.match_ladder, member=member[0])
    if team == match.team_1:
            match.cancel_request_1 = True
            match.save()
            messages.success(request, "Team One Requested For Match Cancel") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
    elif team == match.team_2:
            match.cancel_request_2 = True
            match.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
             
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def acceptCancel(request, pk):
    match = Matches.objects.get(id=pk)

    list_ = jsonDec.decode(match.members_list)
    for lis in list_:
        member = Member.objects.filter(id=lis, member=request.user)
        
        if member.exists():
            break
    if not member.exists():
        messages.error(request, "You Have No Access!!") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    team = Team.objects.get(ladder=match.match_ladder, member=member[0])
    if match.cancel_request_1 and team == match.team_1:
        messages.error(request, "Your Team Have Requested For Cancel Match Please Wait For Other Team") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if match.cancel_request_2 and team == match.team_2:
        messages.error(request, "Your Team Have Requested For Cancel Match Please Wait For Other Team") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if match.team_2 is not None:
        match.match_ladder.matches_played = match.match_ladder.matches_played - 1

    match.delete()
    messages.success(request, "Match Canceled") 
    return redirect('index')

def changePassword(request):
    user = User.objects.get(id=request.user.id)
    old_password = request.POST.get('old_password')
   
    new1 = request.POST.get('new_password1')
    new2 = request.POST.get('new_password2')
    auth = authenticate(username=user.username, password=old_password)
    
    if auth is None:
        messages.error(request, "Incorrect Old Password!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if new1 != new2:
        messages.error(request, "New Password Doesnot Match!")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    user.set_password(new1)
    user.save()
    messages.success(request, "Password Changed")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def updateProfile(request):
    user = User.objects.get(id=request.user.id)
    if request.user == user:
        user_dt = userdtl.objects.get(user=user)
        user.first_name = request.POST.get('fname')
        user.last_name = request.POST.get('lname')
        user.email = request.POST.get('email')
        


        user_dt.timezone_user = request.POST.get('timezone')
        user_dt.twitch = request.POST.get('twitch')
        user_dt.twitter = request.POST.get('twitter')
        user_dt.youtube = request.POST.get('youtube')
        cont = request.POST.get('country')
        if cont != user_dt.country:
            user_dt.country = cont
        img = request.FILES.get('image_change')
        if img is not None:
            user_dt.img_user = img
        # user_dt.save(update_fields=['country', 'twitter', 'youtube', 'twitch', 'timezone_user'])
        user.save()
        user_dt.save()
        user_dt.country_select()
        user_dt.save()
        if request.POST.get('psn'):
            messages.error(request, "Please contact Support for updating PSN") 
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            

        messages.success(request, "Profile Updated") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You Have No Access") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def rejectInvite(request, pk):
    user = User.objects.get(id=request.user.id)
    user_dt = userdtl.objects.get(user=user)
    user_dt.invitation.remove(pk)
    
    user_dt.save()
    messages.success(request, "Request Denied!!") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def acceptInvite(request, pk):
    user = User.objects.get(id=request.user.id)
    team = Team.objects.get(name=pk)
    if team.check_limit():
        messages.error(request, f"Team Reached Members Max Limit") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # print(Member.objects.filter(team=team, member=user.id).exists())
    ladder = Ladders.objects.get(id=team.ladder.id)
    try:
        for teams in ladder.teams.all():
            if Member.objects.filter(team=teams, member=user.id).exists():
                messages.error(request, f"You Already in a {teams}") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # mem = Member.objects.get(member=user.id)
        # team = Team.objects.filter(member=mem.member, ladder=team.ladder)
        # for t in team:
        #     if Member.objects.filter(team=t, member=user).exists():
        #         messages.error(request, "You Already in a Team") 
        #         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        pass
    vuser = userdtl.objects.get(user=user)
    NUMBER_OF_SECONDS = 42300
    
    if (vuser.team_left - utc.localize(datetime.datetime.now())).total_seconds() < NUMBER_OF_SECONDS:
        messages.error(request, f"You Cannot Join Any Team Before 12 Hours") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    vuser.invitation.remove(team.id)
    member = Member(team=team,member=user)
    member.save()

    messages.success(request, f"{team.name}, Joined Successfully") 
    return redirect('team', pk=team.id)
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def sendInvite(request):
    pk = request.POST['member1']
    team_name = request.POST.get('teamname')
    team = Team.objects.get(name=team_name)
    try:
        user_ = User.objects.get(username=pk)
    except:
        messages.error(request, f"No User Found With {pk} Username") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user = userdtl.objects.get(user=user_.id)
    user.invitation.add(team.id)
    user.save()
    messages.success(request, f"{user}, has been Invite") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def transferLeader(request):
    pk = request.POST.get('member1')
    member_ = Member.objects.get(id=pk)
    member_.rank = "Leader"
    member_.save()
    print(pk)
    curr = request.POST.get('leader')
    print(curr)
    member = Member.objects.get(id=curr)
    member.rank = "Captain"
    member.save()
    messages.success(request, f"Leadership has been Transfered to {member_.member}") 
    return redirect(index)

def promotePlayer(request):
    
    pk = request.POST.get('member1')
    member = Member.objects.get(id=pk)
    rank = request.POST.get('rank')
    member.rank = rank
    member.save()
    messages.success(request, f"{member.member}, has been Prometed to Leader") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

def kickMember(request, pk): 
    
    member = Member.objects.get(id=pk)
    NUMBER_OF_SECONDS = 43200
    team = Team.objects.get(id=member.team.id)
    A = team.Team_A.all()
    B = team.Team_B.all()

    if A or B:
        for i in A:

            if i.in_progress():
                messages.error(request, "There are Active Matches, You cannot Kick Member") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        for j in B:
         
            if j.in_progress():
                
                messages.error(request, "There are Active Matches, You cannot Kick Member") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # if (member.team_joined - utc.localize(datetime.datetime.now())).total_seconds() < NUMBER_OF_SECONDS:
    #     messages.error(request, "Player cannot be kicked from team before 12 Hours") 
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    member.member.userdtl.team_left = datetime.datetime.now()
    member.member.userdtl.save()
    member.delete()
    messages.success(request, "Member Removed") 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    # else:
    #     messages.error(request, "You Have no access") 
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
def leaveTeam(request, pk): 
    

    member = Member.objects.get(id=pk)
    team = Team.objects.get(id=member.team.id)
    A = team.Team_A.all()
    B = team.Team_B.all()
    if A or B:
        for i in A:

            if i.in_progress():
                messages.error(request, "There are Active Matches, You cannot Leave Team") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        for j in B:
            
            if j.in_progress():
                messages.error(request, "There are Active Matches, You cannot Leave Team") 
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.user == member.member:
        member.member.userdtl.team_left = datetime.datetime.now()
        member.member.userdtl.save()
        member.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, "You Have no access") 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def createTeam(request):
    if request.method == 'POST':
        name = request.POST['name']
        leader = request.user
        if Team.objects.filter(name=name).exists():
            return render(request, 'tlou/create.html',
            {"message" : f"{name} Already Taken, Try other"})
        else:
            team = Team(name=name)
            team.save()
            member = Member(team=team, member=leader, rank="Leader")
            member.save()
            return redirect(index)
        
    else:
        return render(request, "tlou/create.html")

def teamsPage(request, pk):
    member = Member.objects.get(member=request.user)
    lad = Ladders.objects.filter(id=pk)
    team = Team.objects.get(ladder=lad[0], member=member)
    match = Matches.objects.filter(match_ladder=lad[0])
    teams = dict(teams=match)
    # return JsonResponse(teams)
    return render(request, 'tlou/teams.html', {
        "teams" : match,
        "team_1" : team
    })

def joinTeam(request, pk):
    team = Team.objects.get(id=pk)
    member = Member(team=team, member=request.user)    
    member.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class datathread(threading.Thread):
    def __init__(self, data):
        self.data = data
        threading.Thread.__init__(self)

    def run(self):
        self.data.send()

def aboutus(request):
    return render(request, 'tlou/about.html')


def index(request):
    indexnews = News.objects.filter(active=True).order_by('?')[:4]
    fsliders = sliders.objects.filter(active=True)
    fladder = Ladders.objects.filter(active=True).order_by('?')[:4]
    fsocial = Social.objects.all()
    matches = Matches.objects.all().order_by('-id')[:5]
    
    return render(request,'index.html', {
        'news':indexnews,
        'slider':fsliders,
        'social':fsocial,
        'ladder':fladder,
        'matches' : matches,
        
        })

def newsView(request):
    indexnews = News.objects.filter(active=True)[:20]
    
    return render(request,'news.html', {
        'news':indexnews,
        })

def defsnews(request, pk):
    indexnews = News.objects.get(id=pk)
    fsocial = Social.objects.all()
    fimage = image.objects.filter(active=True).order_by('?'[:5])
    return render(request,'single-blog.html', {'news':indexnews,'social':fsocial,'image':fimage})

def gameView(request):
    games = Games.objects.filter(active=True)[:12]
    return render(request,'games.html', {
        'games':games,
        })

def ladderListView(request,pk):
    sgame = Games.objects.get(id=pk)
    ladders = Ladders.objects.filter(game=sgame,active=True)[:12]
    return render(request,'ladders.html', {
        'gname' : sgame,
        'ladders':ladders
        })

def ladderView(request,pk):
    allusr = User.objects.filter(is_staff=False)
    ladders = Ladders.objects.get(id=pk,active=True)
    matches = Matches.objects.filter(match_ladder=ladders)
    
    if request.method == 'POST':
        teamname = request.POST.get('teamname', '')
        if ladders.lock_ladder:
            messages.error(request, "Ladder Has been locked or Finished")
            return redirect("/ladder/"+str(ladders.id))

        pteam = Team(name=teamname,ladder=ladders)
        pteam.save()
        leader = Member(rank="Leader", member=request.user, team=pteam)
        leader.save()
        
        ladders.teams.add(pteam.id)
        ladders.save()  
        messages.success(request, "Your team has been successfully created")
        return redirect("/ladder/"+str(ladders.id))
    teams = Team.objects.filter(ladder=ladders).order_by('-rating')
    participant = False
    founder = False
    player = None
    fteam = None
    if request.user.is_authenticated :
        member = Member.objects.filter(member=request.user)
        
        if member.exists():
            
            for m in member:
                if request.user.username == m.member.username:
                    if m.rank == "Leader":
                        founder = True
                  
                if m.team.ladder == ladders:
                    user = User.objects.get(username=request.user)
                    
                    member_ = Member.objects.get(member=user.id) 
                    
                    fteam = Team.objects.get(ladder=ladders, member=member_.id)
                   
                    player = Member.objects.filter(team=fteam)
                    participant = True
           
    #     else:
    #         fteam = None
    #         player = None
    # else:
    #     player = None
    #     fteam = None
    
    return render(request,'tlou/ladder.html', {
        'ladder':ladders,
        'alluser':allusr,
        'players' : player,
        'pteam' : fteam,
        'teams':teams,
        "participant" : participant,
        "founder" : founder,
        "matches" : matches,
        })

@csrf_exempt
def handleSignup(request):
    if request.method == 'POST':
        # Get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']

        ip, is_routable = get_client_ip(request)
        banip = BanIp.objects.filter(ip=ip)
        if banip.exists():
            if banip[0].temporary_ban:
                messages.error(request, "Your IP Address is Temporarily Banned")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if banip[0].permanent_ban:
                messages.error(request, "Your IP Address Permanantly Banned")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Used")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        psn = request.POST['psn']
       
        if psn != '' and userdtl.objects.filter(psn=psn).exists():
            messages.error(request, "PSN Already Used")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        timezone = request.POST['timezone']
        country = request.POST['country']
        # Check for errorneous inputs
        if User.objects.filter(username=username):
            messages.error(request, "Username you choose is already used")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # username should be under 10 characters
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # username should be alphanumeric
        if not username.isalnum():
            messages.error(request, "Username should only contain letters and numbers")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # passwords should match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect('/')

        # Create the user 
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        dtluser = userdtl(user_id = myuser.id, timezone_user=timezone, tpass = random.randint(1000,9999), bpass = pass1, psn=psn, country=country)
        dtluser.save()
        dtluser.country_select()
        dtluser.save()

        messages.success(request, "Your Tlouesports account has been successfully created")
        return redirect("/validate/"+ myuser.username +"")
    else:
        return HttpResponse('404 - Not Found')

def handleLogin(request):
    if request.method == 'POST':
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        ip, is_routable = get_client_ip(request)
        banip = BanIp.objects.filter(ip=ip)
        if banip.exists():
            if banip[0].temporary_ban:
                messages.error(request, "Your IP Address is Temporarily Banned")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            if banip[0].permanent_ban:
                messages.error(request, "Your IP Address Permanantly Banned")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                


        if loginpassword == "":
            return redirect("/validate/"+ loginusername +"")

        vuser = User.objects.get(username=loginusername)
        try:
            ban = BanUser.objects.get(user=vuser)
            if ban.is_still_ban():
                if ban.temporary_ban:
                    messages.error(request, "Your Account is Temporarily Banned")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                if ban.permanent_ban:
                    messages.error(request, "Your Account Permanantly Banned")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
        except:
            pass
        
        # if is_routable:
        vuser.userdtl.ip_address = ip
        vuser.userdtl.save()
        if loginpassword != "" and not vuser.is_active:
        
            if vuser.is_active == False:

                messages.error(request, "Your Account is in-active Please Check your Email For Confirmation")
                return redirect('validate', user = loginusername)
        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
             
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
        else:
            messages.error(request, "Invalid Credentials, Please try again")
             
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            
    return HttpResponse('404 - Not Found')


def handleLogout(request): 
    logout(request)
    messages.success(request, "Successfully Logged Out")
     
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
 


def validate(request, user):
    fsocial = Social.objects.all()
    fimage = image.objects.filter(active=True).order_by('?'[:5])
    try:
     
        vuser = User.objects.get(username = user)
        if request.user.is_active:
            messages.error(request, "You Have No Access")
            return redirect('index')
      
        email_from = settings.EMAIL_HOST_USER
   
        # msg = f"Hi \n Your Verification Code is {vuser.userdtl.tpass}"
        msg = render_to_string('tlou/mail.html', {'user' : user, 'code': vuser.userdtl.tpass})
    

        recipient_list = [vuser.email, ]

        subject = "Verify Account"

        send_mail( subject, msg, email_from, recipient_list )

        if request.method == "POST":
            passw = request.POST['onepass']
            if passw == vuser.userdtl.tpass:
                musr = User.objects.get(username = user)
                if musr.is_active == False:
                    musr.is_active = True
                    messages.success(request, "Account Validation Successful !")
                else:
                    passn = request.POST['npass']
                    musr.set_password(passn)
                    usr = userdtl.objects.get(user = musr)
                    usr.bpass = passn
                    usr.save()
                    messages.success(request, "Password changed successfully !!")
                musr.save()
                login(request, musr)
            
                return redirect("/")
            else:
                messages.success(request, "Invalid OTP")
    except:
        messages.error(request, "Account not Exists")
        return redirect('/')
    return render(request, 'validate.html', {'vuser': vuser,'social':fsocial,'image':fimage})


def defprofile(request, user):
  
    try:
        vuser = User.objects.get(username = user)
        member = Member.objects.filter(member=vuser)
        for m in member:
            match_1 = Matches.objects.filter(team_1=m.team)
            match_2 = Matches.objects.filter(team_2=m.team)
            matches = match_1 | match_2
            game = Games.objects.filter(ladders=m.team.ladder)
            games = game | game


    except:
        messages.error(request,"You are trying to access profile of Invalid user")
        return redirect("/")
    return render(request,'tlou/profilePage.html',{
        'user' : vuser,
        'games' : games,
        'matches' : matches,
        'countries' : country_list,
        'timezone' : pytz.all_timezones,
        'teams' : member
        })

def sendMessage(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        contact = Contact(name=name, email=email, message=message)
        contact.save()
        messages.success(request, "We have Recieved Your Message We Will Contaact You in a while")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def defcontact(request):

    fsocial = Social.objects.all()
    fimage = image.objects.filter(active=True).order_by('?'[:5])
    options = AdminOptions.objects.get(access_name="admin")
    return render(request,'contact.html',{'social':fsocial,'image':fimage, 
            "options" : options})

def raiseDispute(request, pk):
    match = Matches.objects.get(id=pk)
    match.disputed = True
    match.save()
    messages.success(request, "Dispute Raised Please Submit your Proofs in 12 Hours")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def admin_action_win_one(request, pk):
    if request.user.is_superuser:
        match = Matches.objects.get(id=pk)
        match.team_1.Win = match.team_1.Win + 1 
        if match.team_1.crown == False:
            match.team_1.crown_held = match.team_1.crown + 1
        lis = jsonDec.decode(match.team_1.streak)
        lis.append(1)
        match.team_1.streak = json.dumps(lis)
        match.team_1.save(update_fields=['Win', 'streak', 'crown_held'])
        

        for m in match.sort_team_A():
            m.member.userdtl.user_win = m.member.userdtl.user_win + 1
            m.member.userdtl.save()
            
        for m in match.sort_team_B():
            m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
            m.member.userdtl.save()
        
        match.team_2.Lose = match.team_2.Lose + 1
        lis_ = jsonDec.decode(match.team_2.streak)
        lis_.append(0)
        match.team_2.streak = json.dumps(lis_)
        match.team_2.save(update_fields=['Lose', 'streak'])
        
        match.winner = match.team_1.name  
        d = 1


        elo = EloRating(match.team_1.rating, match.team_2.rating, 30, d, match.team_1.crown, match.team_2.crown  )
       
        per_rate = elo[0] - match.team_1.rating
        match.team_one_rating = per_rate
        
        match.team_1.rating = elo[0]
        match.team_1.crown = elo[2]
        
       
        per_rate = elo[1] - match.team_2.rating
        match.team_two_rating = per_rate
        match.team_2.rating = elo[1]
        match.team_2.crown = elo[3]

        match.team_1.save(update_fields=["rating", "crown"])
        match.team_2.save(update_fields=["rating", "crown"])
        match.result = True
        match.disputed = False
        match.save(update_fields=['result', 'disputed','winner', 'team_one_rating', 'team_two_rating'])
        messages.success(request, "Team Setted as Winner")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def admin_action_win_two(request, pk):
    if request.user.is_superuser:
        match = Matches.objects.get(id=pk)
        match.team_2.Win = match.team_2.Win + 1 
        if match.team_2.crown == False:
            match.team_2.crown_held = match.team_2.crown + 1
        lis = jsonDec.decode(match.team_2.streak)
        lis.append(1)
        match.team_2.streak = json.dumps(lis)
        match.team_2.save(update_fields=['Win', 'streak', 'crown_held'])
        
        for m in match.sort_team_B():
            m.member.userdtl.user_win = m.member.userdtl.user_win + 1
            m.member.userdtl.save()
        for m in match.sort_team_A():
            m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
            m.member.userdtl.save()

        
        match.team_1.Lose = match.team_1.Lose + 1
        lis_ = jsonDec.decode(match.team_1.streak)
        lis_.append(0)
        match.team_1.streak = json.dumps(lis_)
        match.team_1.save(update_fields=['Lose', 'streak'])
        
        match.winner = match.team_2.name  
        d = 2


        elo = EloRating(match.team_1.rating, match.team_2.rating, 30, d, match.team_1.crown, match.team_2.crown  )
      
        per_rate = elo[0] - match.team_1.rating
        match.team_one_rating = per_rate
        

        match.team_1.rating = elo[0]
        match.team_1.crown = elo[2]
        
        
        per_rate = elo[1] - match.team_2.rating
        match.team_two_rating = per_rate
        
        match.team_2.rating = elo[1]
        match.team_2.crown = elo[3]

        match.team_1.save(update_fields=["rating", "crown"])
        match.team_2.save(update_fields=["rating", "crown"])
        match.result = True
        match.disputed = False
        match.save(update_fields=['result','disputed', 'winner', 'team_one_rating', 'team_two_rating'])
        messages.success(request, "Team Setted as Winner")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def reverse_match(request, pk):
    if request.user.is_superuser:
        match = Matches.objects.get(id=pk)
        team = Team.objects.get(name=match.winner)
        if match.team_1 == team:
           
            team.Win = team.Win - 1 
            
            team.Lose = team.Lose + 1
            team.rating = team.rating - int(match.team_one_rating)
            
            lis_ = jsonDec.decode(team.streak)
            lis_.remove(1)
            lis_.append(0)
            team.streak = json.dumps(lis_)
            
            for m in match.sort_team_A():
                m.member.userdtl.user_win = m.member.userdtl.user_win - 1
                m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
                
                m.member.userdtl.save()
            for m in match.sort_team_B():
                m.member.userdtl.user_win = m.member.userdtl.user_win + 1
                m.member.userdtl.user_lose = m.member.userdtl.user_lose - 1
                m.member.userdtl.save()

            lis = jsonDec.decode(match.team_2.streak)
            lis.remove(0)
            lis.append(1)
            match.team_2.streak = json.dumps(lis_)

            match.team_2.Win = match.team_2.Win + 1
            match.team_2.Lose = match.team_2.Lose - 1
            match.team_2.rating = match.team_2.rating + int(match.team_one_rating)
            
            match.winner = match.team_2.name
            d = 2

            elo = EloRating(team.rating, match.team_2.rating, 30, d, team.crown, match.team_2.crown  )
            per_rate = elo[0] - team.rating 
            match.team_one_rating = per_rate
            per_rate = elo[1] - match.team_2.rating
            match.team_two_rating  = per_rate
            match.team_2.crown = elo[2]
            team.crown = elo[3]

            match.save()
            team.save()
            match.team_1.save()
            match.team_2.save()
            

        elif match.team_2 == team:
            team.Win = team.Win - 1 
            team.Lose = team.Lose + 1
            team.rating = team.rating - int(match.team_two_rating)
            
            lis_ = jsonDec.decode(team.streak)
            lis_.remove(1)
            lis_.append(0)
            team.streak = json.dumps(lis_)
            
            lis = jsonDec.decode(match.team_1.streak)
            lis.remove(0)
            lis.append(1)
            match.team_1.streak = json.dumps(lis_)

            match.team_1.Win = match.team_1.Win + 1
            match.team_1.Lose = match.team_1.Lose - 1
            match.team_1.rating = match.team_1.rating + int(match.team_one_rating) 
            
            d = 1
            match.winner = match.team_1.name
            elo = EloRating(match.team_1.rating, team.rating, 30, d, match.team_1.crown, team.crown  )
            per_rate = elo[0] - match.team_1.rating
            match.team_one_rating = per_rate
            per_rate = elo[1] - team.rating
            match.team_two_rating  = per_rate
            match.team_2.crown = elo[2]
            team.crown = elo[3]
            
            for m in match.sort_team_B():
                m.member.userdtl.user_win = m.member.userdtl.user_win - 1
                m.member.userdtl.user_lose = m.member.userdtl.user_lose + 1
                
                m.member.userdtl.save()
            for m in match.sort_team_A():
                m.member.userdtl.user_win = m.member.userdtl.user_win + 1
                m.member.userdtl.user_lose = m.member.userdtl.user_lose - 1
                m.member.userdtl.save()

            match.save()
            team.save()
            match.team_1.save()
            match.team_2.save()
            
        
        messages.success(request, "Match Reversed")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def admincancel(request , pk):
    if request.user.is_superuser:
        match = Matches.objects.get(id=pk)
        match.delete()
        messages.success(request, "Match Deleted")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def adminForm(request, pk):
    if request.user.is_superuser:
        match = Matches.objects.get(id=pk)
        
        return render(request, 'admin/proof.html', {
            "proof_1" : match.report_one_team.first,
            "proof_2" : match.report_two_team.first,
            "match" : match,
        })

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

@csrf_exempt
def forgot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = User.objects.filter(email=data['email'])
        if user.exists():
            st = randomword(18)

            user[0].userdtl.forgot_access = st

            recipient_list = [data['email'], ]
            email_from = settings.EMAIL_HOST_USER
            subject = "Forgot Password?"
            msg = render_to_string('tlou/forgot_mail.html', {
                'user' : user[0],
                'st' : st
            })
            
            send_mail( subject, msg, email_from, recipient_list )

            user[0].userdtl.save()
            return JsonResponse({"message" : "Email has been Sent To Reset Your Password"})
        else:
            return JsonResponse({"message" : "Email Address Not Found"})

    return render(request, 'tlou/forgot.html')

def resetPassword(request, pk, code):
    if request.user.is_authenticated:
        messages.error(request, "You Have No Access") 
        return redirect(index)


    user = User.objects.get(id=pk)
    if user.userdtl.forgot_access != code:
        messages.error(request, "Link Expired") 
        return redirect(index)

        

    recipient_list = [user.email, ]
    email_from = settings.EMAIL_HOST_USER
    subject = "New Password"
    password = randomword(11)
    user.set_password(password)
    user.save()
    msg = f"Hey {user},\n Your New Password is {password}, \n Make sure to change password after loging in"
    send_mail(subject, msg, email_from, recipient_list)
    user.userdtl.forgot_access = ''
    user.userdtl.save()
    return render(request, 'tlou/reset.html', {
        "message" : "Your Password Has Been Sent To Your Email"
    })

def base_extension(request):
    options = AdminOptions.objects.get(access_name="admin")
    return render(request, 'base_extension.html', {
        'options' : options
    })

def terms(request):
    return render(request, 'tlou/terms.html')

def privacy(request):
    return render(request, 'tlou/privacy.html')