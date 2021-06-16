import math
  
# Function to calculate the Probability
def Probability(rating1, rating2):
  
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))
  
  
# Function to calculate Elo rating
# K is a constant.
# d determines whether
# Player A wins or Player B. 
def EloRating(Ra, Rb, K, d, team1=False, team2=False):
   
  
    # To calculate the Winning
    # Probability of Player B
    Pb = Probability(Ra, Rb)
  
    # To calculate the Winning
    # Probability of Player A
    Pa = Probability(Rb, Ra)
  
    # Case -1 When Player A wins
    # Updating the Elo Ratings
    if (d == 1) :
        new_pts1 = Ra + K * (1 - Pa)
        new_pts2 = Rb + K * (0 - Pb)
      
  
    # Case -2 When Player B wins
    # Updating the Elo Ratings
    else :
        new_pts1 = Ra + K * (0 - Pa)
        new_pts2 = Rb + K * (1 - Pb)
      
    if team1:
      if d == 1:
        pts = new_pts1 - Ra
        new_pts1 += pts
      else:
        team1 = False
        team2 = True   
    if team2:
      if d != 1:
        pts = new_pts2 - Rb
        new_pts2 += pts
      else:
        team2 = False
        team1 = True

    return round(new_pts1), round(new_pts2), team1, team2