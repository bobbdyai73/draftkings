"""This is a Pyhton class object designed to update a data frame consisting of NFL player statistics. The database is used in a prodective model, whos function is to predict every players weekly staicstics"""

import pandas as pd 
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

class DkWeeklyUpdate():

    # Dictionaries to be used for mapping
    position_dict = {'qb':'DraftKingsQuarterbackFantasyPointsAllowedAverage',
                    'wr':'DraftKingsWideReceiverFantasyPointsAllowedAverage',
                    'rb':'DraftKingsRunningbackFantasyPointsAllowedAverage',
                    'te':'DraftKingsTightEndFantasyPointsAllowedAverage'}

    team_dict = {'New England Patriots':'NE',
                'Green Bay Packers':'GB',
                'Tampa Bay Buccaneers':'TB',
                'Kansas City Chiefs':'KC',
                'San Diego Chargers':'SD',
                'St. Louis Rams':'STL',
                'New Orleans Saints':'NO',
                'New York Jets':'NYJ',
                'New York Giants':'NYG',
                'San Francisco 49ers':'SF',
                'Los Angeles Rams':'LAR',
                'Jacksonville Jaguars':'JAX',
                'Los Angeles Chargers':'LAC'}

    rename_cols = {'qb':{'Opponent':'opp',
                          'PassingAttempts':'att',
                          'PassingCompletionPercentage':'comp%',
                          'PassingYards':'yds',
                          'PassingYardsPerAttempt':'yds/att',
                          'PassingTouchdowns':'td',
                          'PassingInterceptions':'int',
                          'FantasyPointsDraftKings':'points'},
                   'rb':{'Opponent':'Opp',
                          'RushingAttempts':'att',
                          'RushingYards':'yds',
                          'RushingYardsPerAttempt':'yds/att',
                          'RushingTouchdowns':'td',
                          'FumblesLost':'fum',
                          'FantasyPointsDraftKings':'points'},
                   'te':{'ReceivingTargets':'tar',
                          'Receptions':'rec',
                          'ReceivingYards':'yds',
                          'ReceivingTouchdowns':'td',
                          'ReceivingYardsPerTarget':'yds/tar',
                          'ReceivingYardsPerReception':'yds/rec',
                          'FantasyPointsDraftKings':'points'},
                   'wr':{'ReceivingTargets':'tar',
                          'Receptions':'rec',
                          'ReceivingYards':'yds',
                          'ReceivingTouchdowns':'td',
                          'ReceivingYardsPerTarget':'yds/tar',
                          'ReceivingYardsPerReception':'yds/rec',
                          'FantasyPointsDraftKings':'points'}
                  }





    def __init__ (self,csv):
        self.df = pd.read_csv(csv)
        
        # Rename columns to match historical stats df
    def rename_cols(self, position):
        self.rename(columns=rename_cols[position])
               
        return self
        
        
        # Prepare the defensive ranking dataframe by sorting by position
    def add_defensive_rankings (self, df1, position):
       
        df1.sort_values(position_dict[position], inplace=True)
        df1.reset_index(inplace=True, drop=True)
        df1['Rank'] = df.index + 1
        df1.index = df1['Team']
        
        # Map defensive ranking to each player in stats df
        self['def_rk'] = list(map(lambda x: df1.loc[x]['Rank']))
        return self

        # Get location of every game for week and append it to the location dataframe
    def pfr_scraper(url, current_week):

        # Set url for requests function
        page = requests.get(url)

        # Use BeautifulSoup to scarpe data the data from Pro Footbal Reference.com 
        soup = BeautifulSoup(page.text,'html.parser')
        weeks = []  
        for tr in soup.find_all('tr'):
            weeks.append(tr.text)

         # Remove any lines that dont describe weekly nfl game
        for row in weeks:
            if row.split()[0].isalpha():
                weeks.remove(row)
            else:
                pass    

          # Split string a first non digit and use result for week varianble of each individual matchup
        day = []
        week = []
        date = []
        time =[]
        for row in weeks:
            if int(re.split(r'(\d+)', row)[1]) <= current_week:
                week.append(re.split(r'(\d+)', row)[1])
                day.append(re.split(r'(\d+)',row)[2][:3])
                if re.split(r'(\d+)', row)[2][3:11] == 'November' and int(re.split(r'(\d+)', row)[3][:2]) > 30:
                    date.append(re.split(r'(\d+)',row)[2][3:] + re.split(r'(\d+)', row)[3][0]\
                                + ',' + ' ' + urlparse(url).path.split('/')[2])
                elif  re.split(r'(\d+)', row)[2][3:11] == 'November' and int(re.split(r'(\d+)', row)[3][:2]) <= 30:
                    date.append(re.split(r'(\d+)',row)[2][3:] + re.split(r'(\d+)', row)[3][:2]\
                                + ',' + ' ' + urlparse(url).path.split('/')[2])
                if re.split(r'(\d+)', row)[2][3:11] != 'November' and int(re.split(r'(\d+)', row)[3][:2]) > 31:
                    date.append(re.split(r'(\d+)',row)[2][3:] + re.split(r'(\d+)', row)[3][0]\
                                + ',' + ' ' + urlparse(url).path.split('/')[2])
                elif re.split(r'(\d+)', row)[2][3:11] != 'November' and int(re.split(r'(\d+)', row)[3][:2]) <= 31:
                    date.append(re.split(r'(\d+)',row)[2][3:] + re.split(r'(\d+)', row)[3][:2]\
                                + ',' + ' ' + urlparse(url).path.split('/')[2])
          
               # Use beautiful to retrieve detail on each game in an NFL season
        game =[]
        for td in soup.find_all('td'):
            game.append(td.text)

        # Create lists to establish the home and away teams in every game of an NFL season
        home = []
        away =[]

        try:
            for idx,val in enumerate(game):
                if val == '':
                    home.append(game[idx-1])
                    away.append(game[idx+1])
                elif val =='@':
                    home.append(game[idx+1])
                    away.append(game[idx-1])
        except:
            None

        # Create a dataframe to hold the location date and time of every NFL game by week
        loc = pd.DataFrame()
        loc['date'] = date
        loc['week'] = current_week
        loc['home']=home[0:len(week)]
        loc['away']=away[0:len(week)]
        loc['year']=int(urlparse(url).path.split('/')[2])


        loc= loc.replace({"away": team_dict})
        loc= loc.replace({"home": team_dict})

        # Convert the NFL team names that are not in Team Dictiionary by capitalizing the first three character of the team name 
        try:
            loc['home'] = loc['home'].apply(lambda x: x[0:3].upper())
            loc['away'] = loc['away'].apply(lambda x: x[0:3].upper())
        except:
            None
            
        return loc

    # Add the home or away atribute to the stats df
    def home_away(self, loc):
        for team in self['Team']:
            if team in list([loc['week']==week]['home']):
                home_lst.append('home')
                date_lst.append(loc[loc['home']==team]['date'])
            else:
                home_lst.append('away')
                date_lst.append(loc[loc['away']==team]['date'])
        self['h/a'] = home_lst
        self['date'] = date_lst
               
        return self
               
    # Add surface type for each game played
       
    def onehot_encode(self):
        self.reset_index(inplace=True, drop=True)
        encoder = LabelEncoder()
        self['h/a_encoded'] = encoder.fit_trandsform(self['h/a'])
        self['surface_encode'] = encoder.fit_transform(self['surface'])
        home = OneHotEncoder()
        surface = OneHotencoder()
        
        X = home.fit_transform(self['h/a_encoded'].values.reshape(-1,1)).toarray()
        Xs = surface.fit_transform(self['surface_encoded'].values.reshape(-1,1)).toarray()
        
        dfONeHot = pd.DataFrame(X, columns =["h/a_"+str(int(i)) for i in range(X.shape[1])])
        self = pd.concat([self,dfOneHot], axis=1)
        
        dfOneHot = pd.DataFrame(Xs, columns = ['surface_'+str(int(i)) for i in range(Xs.shape[1])])
        self = pd.concat([self,dfOneHot])
        
        return self
                                
                                
                                
                                
        
                                                     
        
               
               
               
               
     


