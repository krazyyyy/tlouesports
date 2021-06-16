from django.contrib import admin
from django.urls import path,include
from .import views

urlpatterns = [
    path('', views.index, name="index"),
    path('news', views.newsView, name="news"),
    path('aboutus', views.aboutus, name="about"),
    path('news/<str:pk>', views.defsnews, name="single-news"),
    path('games', views.gameView, name="games"),
    path('ladders/<str:pk>', views.ladderListView, name="ladders"),
    path('ladder/<str:pk>', views.ladderView, name="ladder"),
    path('signup', views.handleSignup, name="signup"),
    path('login', views.handleLogin, name="login"),
    path('logout', views.handleLogout, name="logout"),
    path("validate/<str:user>", views.validate, name="validate"),
    path("profile/<str:user>", views.defprofile, name="profile"),
    path('contact', views.defcontact, name="contact"),
    path('sendmessage', views.sendMessage, name="sendmessage"),
    path('create', views.createTeam, name="create"),
    path('teams/<int:pk>', views.teamsPage, name="teams"),
    path('team/<int:pk>', views.renderTeam, name="team"),
    path('join/<int:pk>', views.joinTeam, name="join"),
    path('leave/<int:pk>', views.leaveTeam, name="leave"),
    path('kick/<int:pk>', views.kickMember, name="kick"),
    path('promote', views.promotePlayer, name="promote"),
    path('transferLeader', views.transferLeader, name="transferleader"),
    path('invite', views.sendInvite, name="invite"),
    path('accept/<str:pk>', views.acceptInvite, name="accept"),
    path('deny/<str:pk>', views.rejectInvite, name="deny"),
    path('update', views.updateProfile, name="update"),
    path('postmatch', views.postMatch, name="postmatch"),
    path('edit/<str:pk>', views.editTeam, name="edit"),
    path('accept/<str:pk>/<str:tpk>', views.acceptPage, name="accept"),
    path('challenge/<str:pk>', views.challengePage, name="challenge"),
    path('acceptChallenge/<str:pk>', views.acceptChallenge, name="acceptChallenge"),
    path('result/<str:pk>/<str:tm>', views.result, name="result"),
    path('cancel/<str:pk>', views.cancelMatch, name="cancel"),
    path("dispute/<str:pk>", views.dispute, name="dispute"),
    path("changeImge", views.changeImg, name="changeImg"),
    path("cancelreq/<str:pk>", views.cancelMatchReq, name="cancelreq"),
    path("acceptcancel/<str:pk>", views.acceptCancel, name="acceptcancel"),
    path("abort/<str:pk>/<str:tpk>", views.abortRequest, name="abort"),
    path("create/<str:pk>/<str:tpk>", views.create_dispute, name="create_dispute"),
    path("report_match/<str:pk>/<str:tid>/<str:wl>", views.report_match, name="report_match"),
    path("report_match/<str:pk>/<str:tid>/", views.raise_dispute, name="raise_dispute"),
    path("tlou/matches/teamonewin/<str:pk>", views.admin_action_win_one, name="adminwin1"),
    path("tlou/matches/teamtwowin/<str:pk>", views.admin_action_win_two, name="adminwin2"),
    path("tlou/matches/teamdel/<str:pk>", views.admincancel, name="admindel"),
    path("tlou/matches/proof/<str:pk>", views.adminForm, name="proofs"),
    path("tlou/matches/reverse/<str:pk>", views.reverse_match, name="revmat"),
    path("raise/<str:pk>", views.raiseDispute, name="raise"),
    path("changepassword", views.changePassword, name="changepassword"),
    path("forgot", views.forgot, name="forgot"),
    path("reset/<str:pk>/<str:code>", views.resetPassword, name="reset"),
    path("footer", views.base_extension, name="footer"),
    path("privacy", views.privacy, name="privacy"),
    path("terms", views.terms, name="terms"),
]
