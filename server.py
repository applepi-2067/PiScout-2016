import cherrypy
import sqlite3 as sql
import os
import json
from ast import literal_eval
import requests
import math
from statistics import mode
from ipaddress import IPV6LENGTH
from event import CURRENT_EVENT
from piscout import SCOUT_FIELDS
from piscout import AVERAGE_FIELDS

# Update this value before every event
# Use the event codes given by thebluealliance
DEFAULT_MODE = 'averages'

class ScoutServer(object):
    @cherrypy.expose
    def index(self, m='', e=''):
        
        #First part is to handle event selection. When the event is changed, a POST request is sent here.
        illegal = '' #i competely forget what this variable does, just leave it
        if e != '':
            if os.path.isfile('data_' + e + '.db'):
                cherrypy.session['event'] = e
            else:
                illegal = e
        if 'event' not in cherrypy.session:
            cherrypy.session['event'] = CURRENT_EVENT
            
        if m != '':
            cherrypy.session['mode'] = m
        if 'mode' not in cherrypy.session:
            cherrypy.session['mode'] = DEFAULT_MODE

        #This section generates the table of averages
        table = ''
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        if(cherrypy.session['mode'] == "averages"):
            data = conn.cursor().execute('SELECT * FROM averages ORDER BY apr DESC').fetchall()
        elif (cherrypy.session['mode'] == "maxes"):
            data = conn.cursor().execute('SELECT * FROM maxes ORDER BY apr DESC').fetchall()
        elif (cherrypy.session['mode'] == "noD"):
            data = conn.cursor().execute('SELECT * FROM noDefense ORDER BY apr DESC').fetchall()
        else:
            data = conn.cursor().execute('SELECT * from lastThree ORDER BY apr DESC').fetchall()
        conn.close()
        for team in data: #this table will need to change based on the number of columns on the main page
            table += '''
                <tr role="row">
                    <td><a href="team?n={0}">{0}</a></td>
                    <td class="hidden-xs">{1}</td>
                    <td class="hidden-xs">{2}</td>
                    <td class="hidden-xs">{3}</td>
                    <td class="hidden-xs">{4}</td>
                    <td class="hidden-xs">{5}</td>
                    <td class="hidden-xs">{6}</td>
                    <td class="hidden-xs">{7}</td>
                    <td class="hidden-xs">{8}</td>

                    <td class="rankingColumn rankColumn1 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{1}</td>
                    <td class="rankingColumn rankColumn2 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{2}</td>
                    <td class="rankingColumn rankColumn3 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{3}</td>
                    <td class="rankingColumn rankColumn4 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{4}</td>
                    <td class="rankingColumn rankColumn5 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{5}</td>
                    <td class="rankingColumn rankColumn6 hidden-sm hidden-md hidden-lg" style="">{6}</td>
                    <td class="rankingColumn rankColumn7 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{7}</td>
                    <td class="rankingColumn rankColumn8 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{8}</td>
                </tr>
            '''.format(team['team'], team['apr'], team['autogear'], team['teleopgear'], round(team['autogear'] + team['teleopgear'], 2), team['autoballs'], team['teleopballs'], team['end'], team['defense'])
        #in this next block, update the event list and the column titles
        
        with open('web/index.html', 'r') as file:
            page = file.read()
        return page.format(table, cherrypy.session['event'], cherrypy.session['mode'])

    # Show a detailed summary for a given team
    @cherrypy.expose()
    def team(self, n="238"):
        if not n.isdigit():
            raise cherrypy.HTTPRedirect('/')
        if int(n)==666:
            raise cherrypy.HTTPError(403, 'Satan has commanded me to not disclose his evil strategy secrets.')
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        entries = cursor.execute('SELECT * FROM scout WHERE Team=? ORDER BY Match DESC', (n,)).fetchall()
        averages = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
        assert len(averages) < 2 #ensure there aren't two entries for one team
        if len(averages):
            s = averages[0]
        else:
            s = [0]*8 #generate zeros if no data exists for the team yet

        comments = cursor.execute('SELECT * FROM comments WHERE team=?', (n,)).fetchall()
        conn.close()

        # Generate html for comments section
        commentstr = ''
        for comment in comments:
            commentstr += '<div class="commentbox"><p>{0}</p></div>'.format(comment[1])

        #Iterate through all the data entries and generate some text to go in the main table
        #this entire section will need to change from year to year
        output = ''
        dataset = []
        print(len(entries))
        for e in entries:
            # Important: the index of e refers to the number of the field set in main.py
            # For example e[1] gets value #1 from main.py
            dp = {"match": e['match'], "autoshoot":0, "shoot":0, "autogears":0, "gears":0, "geardrop":0}
            a = ''
            a += 'baseline, ' if e['AutoBaseline'] else ''
            a += 'side try, ' if e['AutoSideAttempt'] else ''
            a += 'center try, ' if e['AutoCenterAttempt'] else ''
            a += 'side peg, ' if e['AutoSideSuccess'] else ''
            a += 'center peg, ' if e['AutoCenterSuccess'] else ''
            dp['autogears'] += e['AutoGears']
            a += str(e['AutoLowBalls']) + 'x low goal, ' if e['AutoLowBalls'] else ''
            a += str(e['AutoHighBalls']) + 'x high goal, ' if e['AutoHighBalls'] else ''
            dp['autoshoot'] += e['AutoLowBalls']/3 + e['AutoHighBalls']

            d = ''
            d += str(e['TeleopGears']) + 'x gears, ' if e['TeleopGears'] else ''
            d += str(e['TeleopGearDrops']) + 'x gears dropped, ' if e['TeleopGearDrops'] else ''
            dp['gears'] += e['TeleopGears']
            dp['geardrop'] += e['TeleopGearDrops']

            sh = ''
            sh += str(e['TeleopLowBalls']) + 'x low goal, ' if e['TeleopHighBalls'] else ''
            sh += str(e['TeleopHighBalls']) + 'x high goal, ' if e['TeleopHighBalls'] else ''
            dp['shoot'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3

            o = 'hang, ' if e['Hang'] else 'failed hang, ' if e['FailedHang'] else ''
            o += str(e['Fouls']) + 'x foul, ' if e['Fouls'] else ''
            o += str(e['TechFouls']) + 'x tech foul, ' if e['TechFouls'] else ''
            o += 'defense, ' if e['Defense'] else ''
            o += 'feeder, ' if e['Feeder'] else ''
            o += 'defended, ' if e['Defended'] else ''

            #Generate a row in the table for each match
            output += '''
            <tr role="row" {5}>
                <td>{0}</td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{3}</td>
                <td>{4}</td>
                <td><a class="flag" href="javascript:flag({6},{7});">X</a></td>
                <td class="hidden-xs"><a class="edit" href="/edit?key={8}">E</a></td>
            </tr>'''.format(e['Match'], a[:-2], d[:-2], sh[:-2], o[:-2], 'style="color: #B20000"' if e['Flag'] else '', e['Match'], e['Flag'], e['Key'])
            for key,val in dp.items():
                dp[key] = round(val, 2)
            if not e['Flag']: #if flagged
                dataset.append(dp) #add it to dataset, which is an array of data that is fed into the graphs
            dataset.reverse() #reverse so that graph is in the correct order

        #Grab the image from the blue alliance
        imcode = ''
        headers = {"X-TBA-App-Id": "frc2067:scouting-system:v02"}
        m = []
        try:
            #get the picture for a given team
            m = self.get("http://www.thebluealliance.com/api/v2/team/frc{0}/media".format(n), params=headers).json()
            if m.status_code == 400:
                m = []
        except:
            pass #swallow the error lol
        for media in m:
            if media['type'] == 'imgur': #check if there's an imgur image on TBA
                imcode = '''<br>
                <div style="text-align: center">
                <p style="font-size: 32px;">Image</p>
                <img src=http://i.imgur.com/{}.jpg></img>
                </div>'''.format(media['foreign_key'])
                break
            if media['type'] == 'cdphotothread':
                imcode = '''<br>
                <div style="text-align: center">
                <p style="font-size: 32px;">Image</p>
                <img src=http://chiefdelphi.com/media/img/{}></img>
                </div>'''.format(media['details']['image_partial'].replace('_l', '_m'))
                break

        #Every year, update the labels for the graphs. The data will come from the variable dataset
        #Then update all the column headers and stuff
        with open('web/team.html', 'r') as file:
            page = file.read()
        return page.format(n, output, s[1], s[2], s[3], s[4], s[5], s[6], s[7], str(dataset).replace("'",'"'), imcode, commentstr)

    # Called to flag a data entry
    @cherrypy.expose()
    def flag(self, num='', match='', flagval=0):
        if not (num.isdigit() and match.isdigit()):
            return '<img src="http://goo.gl/eAs7JZ" style="width: 1200px"></img>'
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        cursor.execute('UPDATE scout SET Flag=? WHERE Team=? AND Match=?', (int(not int(flagval)),num,match))
        conn.commit()
        conn.close()
        self.calcavg(num, self.getevent())
        self.calcmaxes(num, self.getevent())
        self.calcavgNoD(num, self.getevent())
        self.calcavgLastThree(num, self.getevent())
        return ''
    
    #Called to recalculate all averages/maxes
    @cherrypy.expose()
    def recalculate(self):
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        data = conn.cursor().execute('SELECT * FROM averages ORDER BY apr DESC').fetchall()
        for team in data:
            self.calcavg(team[0], self.getevent())
            self.calcmaxes(team[0], self.getevent())
            self.calcavgNoD(team[0], self.getevent())
            self.calcavgLastThree(team[0], self.getevent())
        with open('web/recalculate.html', 'r') as file:
            page = file.read()
        return page
        

    # Input interface to choose teams to compare
    @cherrypy.expose()
    def compareTeams(self):
        with open('web/compareTeams.html', 'r') as file:
            page = file.read()
        return page
    
    #Input interface to choose alliances to compare
    @cherrypy.expose
    def compareAlliances(self):
        with open('web/compareAlliances.html', 'r') as file:
            page = file.read()
        return page

    # Output for team comparison
    @cherrypy.expose()
    def teams(self, n1='', n2='', n3='', n4='', stat1='', stat2=''):
        nums = [n1, n2, n3, n4]
        if stat2 == 'none':
            stat2 = ''      
        if not stat1:
            stat1 = 'autogears'
            
        averages = []
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        output = '<div>'
        for index, n in enumerate(nums):
            if not n:
                continue
            if not n.isdigit():
                raise cherrypy.HTTPError(400, "You fool! Enter NUMBERS, not letters.")
            average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
                entry = average[0]
            else:
                entry = [0]*8
            # Add a data entry for each team
            output += '''<div class="comparebox_container">
                    <p><a href="/team?n=254" style="font-size: 32px;">Team {0}</a></p>
                    <div class="statbox_container">
                        <div id="apr">
                            <p style="font-size: 20pt;">APR</p>
                            <p style="font-size: 40pt;">{1}</p>
                        </div>
                        <div id="stats">
                            <p class="statbox" style="font-weight:bold">Average match:</p>
                            <p class="statbox">Auto Gears: {2}</p>
                            <p class="statbox">Teleop Gears: {3}</p>
                            <p class="statbox">Dropped Gears: {4}</p>
                            <p class="statbox">Auto Shoot Points: {5}</p>
                            <p class="statbox">Teleop Shoot Points: {6}</p>
                            <p class="statbox">Endgame Points: {7}</p>
                        </div>
                    </div>
                </div>'''.format(n, *list(entry[1:])) #unpack the elements
            if ((len(nums) == 2 and index==0) or (len(nums) != 2 and index==1)):
                output += '</div><div>'
        output += '</div>'
        
        teamCharts = ''
        dataset = []
        colors = ["#FF0000", "#000FFF", "#1DD300", "#C100E3", "#AF0000", "#000666", "#0D5B000", "#610172"]
        for idx, n in enumerate(nums):
            if not n:
                continue
            entries = cursor.execute('SELECT * FROM scout WHERE Team=? ORDER BY Match ASC', (n,)).fetchall()

            for index, e in enumerate(entries):
            # Important: the index of e refers to the number of the field set in main.py
                # For example e[1] gets value #1 from main.py
                if(not isinstance(e, tuple)):
                    dp = {"autoshoot":0, "shoot":0, "autogears":0, "gears":0, "geardrop":0} 
                    a = ''
                    a += 'baseline, ' if e['AutoBaseline'] else ''
                    a += str(e[5]) + 'x gears, ' if e['AutoGears'] else ''
                    dp['autogears'] += e['AutoGears']
                    a += str(e[7]) + 'x low goal, ' if e['AutoLowBalls'] else ''
                    a += str(e[8]) + 'x high goal, ' if e['AutoHighBalls'] else ''
                    dp['autoshoot'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
        
                    d = ''
                    d += str(e['TeleopGears']) + 'x gears, ' if e['TeleopGears'] else ''
                    d += str(e['TeleopGearDrops']) + 'x gears dropped, ' if e['TeleopGearDrops'] else ''
                    dp['gears'] += e['TeleopGears']
                    dp['geardrop'] += e['TeleopGearDrops']
        
                    sh = ''
                    sh += str(e['TeleopLowBalls']) + 'x low goal, ' if e['TeleopLowBalls'] else ''
                    sh += str(e['TeleopHighBalls']) + 'x high goal, ' if e['TeleopHighBalls'] else ''
                    dp['shoot'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
        
                    o = 'hang, ' if e['Hang'] else 'failed hang, ' if e['FailedHang'] else ''
                    o += str(e['Fouls']) + 'x foul, ' if e['Fouls'] else ''
                    o += str(e['TechFouls']) + 'x tech foul, ' if e['TechFouls'] else ''
                    o += 'defense, ' if e['Defense'] else ''
                    o += 'feeder, ' if e['Feeder'] else ''
                    o += 'defended, ' if e['Defended'] else ''
                    for key,val in dp.items():
                        dp[key] = round(val, 2)
                    if not e['Flag']:
                        if len(dataset) < (index + 1):
                            if stat2:
                                dataPoint = {"match":(index+1), "team" + n + "stat1":dp[stat1], "team" + n + "stat2":dp[stat2]}
                            else:
                                dataPoint = {"match":(index+1), "team" + n + "stat1":dp[stat1]}
                            dataset.append(dataPoint)
                        else:
                            dataset[index]["team" + n + "stat1"] = dp[stat1]
                            if stat2:
                                dataset[index]["team" + n + "stat2"] = dp[stat2]

            teamCharts += '''// GRAPH
                            graph{0} = new AmCharts.AmGraph();
                            graph{0}.title = "{1}";
                            graph{0}.valueAxis = valueAxis;
                            graph{0}.type = "smoothedLine"; // this line makes the graph smoothed line.
                            graph{0}.lineColor = "{3}";
                            graph{0}.bullet = "round";
                            graph{0}.bulletSize = 8;
                            graph{0}.bulletBorderColor = "#FFFFFF";
                            graph{0}.bulletBorderAlpha = 1;
                            graph{0}.bulletBorderThickness = 2;
                            graph{0}.lineThickness = 2;
                            graph{0}.valueField = "{2}";
                            graph{0}.balloonText = "{1}<br><b><span style='font-size:14px;'>[[value]]</span></b>";
                            chart.addGraph(graph{0});
                            '''.format(n + "_1", "Team " + n + stat1, "team" + n + "stat1", colors[idx])
            if stat2:
                teamCharts += '''// GRAPH
                graph{0} = new AmCharts.AmGraph();
                graph{0}.title = "{1}";
                graph{0}.valueAxis = valueAxis2;
                graph{0}.type = "smoothedLine"; // this line makes the graph smoothed line.
                graph{0}.lineColor = "{3}";
                graph{0}.bullet = "round";
                graph{0}.bulletSize = 8;
                graph{0}.bulletBorderColor = "#FFFFFF";
                graph{0}.bulletBorderAlpha = 1;
                graph{0}.bulletBorderThickness = 2;
                graph{0}.lineThickness = 2;
                graph{0}.valueField = "{2}";
                graph{0}.balloonText = "{1}<br><b><span style='font-size:14px;'>[[value]]</span></b>";
                chart.addGraph(graph{0});
                '''.format(n + "_2", "Team " + n + stat2, "team" + n + "stat2", colors[4+idx])
        with open('web/teams.html', 'r') as file:
            page = file.read()
        return page.format(str(dataset).replace("'",'"'), teamCharts, stat1, stat2 + "2", output)

    # Output for alliance comparison
    @cherrypy.expose()
    def alliances(self, b1='', b2='', b3='', r1='', r2='', r3='', mode='', level=''):
        if mode == '':
            mode = 'averages'
        if level == '':
            level = 'quals'
        numsBlue = [b1, b2, b3]
        numsRed = [r1, r2, r3]
        averages = []
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        #start a div table for the comparison
        #to later be formatted with sum APR
        teamsBlue = []
        teamsRed = []
        ballScore = []
        endGame = []
        autoGears = []
        teleopGears = []
        #iterate through all six teams
        for i,n in enumerate(numsBlue):
            if not n.isdigit():
                raise cherrypy.HTTPError(400, "You fool! Enter six valid team numbers!")
            if mode == 'averages':
                average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            else:
                average = cursor.execute('SELECT * FROM maxes WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
                entry = average[0]
            else:
                entry = [0]*8
            teamsBlue.append(n)
            teamsBlue.extend(entry[1:-1])
        for i,n in enumerate(numsRed):
            if not n.isdigit():
                raise cherrypy.HTTPError(400, "You fool! Enter six valid team numbers!")
            if mode == 'averages':
                average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            else:
                average = cursor.execute('SELECT * FROM maxes WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
                entry = average[0]
            else:
                entry = [0]*8
            teamsRed.append(n)
            teamsRed.extend(entry[1:-1])
        
        blue_score = self.predictScore(numsBlue, level)['score']
        red_score = self.predictScore(numsRed, level)['score']
        blue_score = int(blue_score)
        red_score = int(red_score)
        
        prob_red = 1/(1+math.e**(-0.08099*(red_score - blue_score))) #calculates win probability from 2016 data
        conn.close()
        with open('web/alliances.html', 'r') as file:
            page = file.read()
        return page.format(round((1-prob_red)*100,1), blue_score, *teamsBlue, round(prob_red*100,1), red_score, *teamsRed)

    # Lists schedule data from TBA
    @cherrypy.expose()
    def matches(self, n=0):
        n = int(n)
        event = self.getevent()
        datapath = 'data_' + event + '.db'
        self.database_exists(event)
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        
        m = self.getMatches(event, n)

        output = ''

        if 'feed' in m:
            raise cherrypy.HTTPError(503, "Unable to retrieve data about this event.")
        
        #assign weights, so we can sort the matches
        for match in m:
            match['value'] = match['match_number']
            type = match['comp_level']
            if type == 'qf':
                match['value'] += 1000
            elif type == 'sf':
                match['value'] += 2000
            elif type == 'f':
                match['value'] += 3000

        m = sorted(m, key=lambda k: k['value'])
        for match in m:
            if match['comp_level'] != 'qm':
                match['num'] = match['comp_level'].upper() + ' ' + str(match['match_number'])
            else:
                match['num'] = match['match_number']
            output += '''
                <tr role="row">
                    <td>{0}</td>
                    <td class="hidden-xs">{1}</td>
                    <td class="hidden-xs">{2}</td>
                    <td class="hidden-xs">{3}</td>
                    <td class="hidden-xs">{4}</td>
                    <td class="hidden-xs">{5}</td>
                    <td class="hidden-xs">{6}</td>
                    <td class="hidden-xs">{7}</td>
                    <td class="hidden-xs">{8}</td>
                    
                    <td class="rankingColumn rankColumn1 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{1}</td>
                    <td class="rankingColumn rankColumn2 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{2}</td>
                    <td class="rankingColumn rankColumn3 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{3}</td>
                    <td class="rankingColumn rankColumn4 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{4}</td>
                    <td class="rankingColumn rankColumn5 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{5}</td>
                    <td class="rankingColumn rankColumn6 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{6}</td>
                    <td class="rankingColumn rankColumn7 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{7}</td>
                    <td class="rankingColumn rankColumn8 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{8}</td>
                </tr>
            '''.format(match['num'], match['alliances']['blue']['teams'][0][3:],
                        match['alliances']['blue']['teams'][1][3:], match['alliances']['blue']['teams'][2][3:],
                        match['alliances']['red']['teams'][0][3:], match['alliances']['red']['teams'][1][3:],
                        match['alliances']['red']['teams'][2][3:], match['alliances']['blue']['score'],
                        match['alliances']['red']['score'])
        
        with open('web/matches.html', 'r') as file:
            page = file.read()
        return page.format(": {0}".format(n) if n else "", output)

    # Used by the scanning program to submit data, and used by comment system to submit data
    # this won't ever need to change
    @cherrypy.expose()
    def submit(self, data='', event='', team='', comment=''):
        if not (data or team):
            return '''
                <h1>FATAL ERROR</h1>
                <h3>DATA CORRUPTION</h3>
                <p>Erasing database to prevent further damage to the system.</p>'''

        if data == 'json':
            return '[]' #bogus json for local version

        datapath = 'data_' + event + '.db'
        self.database_exists(event)
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()

        if team:
            if not comment:
                conn.close()
                raise cherrypy.HTTPRedirect('/team?n=' + str(team))
            cursor.execute('INSERT INTO comments VALUES (?, ?)', (team, comment))
            conn.commit()
            conn.close()
            raise cherrypy.HTTPRedirect('/team?n=' + str(team))

        d = literal_eval(data)
        flag = 0
        if (d['AutoHighBalls'] or d['TeleopHighBalls']) and (d['AutoLowBalls'] or d['AutoHighBalls']): 
            flag = 1
        if d['Hang'] and d['FailedHang']:
            flag = 1
            
        m = self.getMatches(event)
                
        if m:
            match = next((item for item in m if (item['match_number'] == d['Match']) and (item['comp_level'] == 'qm')))
            teams = match['alliances']['blue']['teams'] + match['alliances']['red']['teams']
            if not 'frc' + str(d['Team']) in teams:
                flag = 1   
                
        if d['AutoGears']:    #if auto gear, set baseline
            d['AutoBaseline'] = 1
            
        if d['Replay']:   #replay
            cursor.execute('DELETE from scout WHERE Team=? AND Match=?', (str(d[0]),str(d[1])))
        cursor.execute('INSERT INTO scout VALUES (NULL,' + ','.join([str(a) for a in d]) + ')')
        conn.commit()
        conn.close()

        self.calcavg(d['Team'], event)
        self.calcmaxes(d['Team'], event)
        self.calcavgNoD(d['Team'], event)
        self.calcavgLastThree(d['Team'], event)
        return ''

    # Calculates average scores for a team
    def calcavg(self, n, event):
        datapath = 'data_' + event + '.db'
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        #delete the existing entry, if a team has no matches they will be removed
        cursor.execute('DELETE FROM averages WHERE team=?',(n,))
        #d0 is the identifier for team, Match is the identifier for match
        entries = cursor.execute('SELECT * FROM scout WHERE Team=? AND flag=0 ORDER BY Match DESC', (n,)).fetchall()
        s = {'autogears': 0, 'teleopgears': 0, 'geardrop': 0, 'autoballs': 0, 'teleopballs':0, 'end': 0, 'defense': 0}
        apr = 0
        # Iterate through all entries (if any exist) and sum all categories
        if entries:
            for e in entries:
                s['autogears'] += e['AutoGears']
                s['teleopgears'] += e['TeleopGears']
                s['autoballs'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
                s['teleopballs'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
                s['geardrop'] += e['TeleopGearDrops']
                s['end'] += e['Hang']*50
                s['defense'] += e['Defense']

            # take the average (divide by number of entries)
            for key,val in s.items():
                s[key] = round(val/len(entries), 2)

            # formula for calculating APR (point contribution)
            apr = s['autoballs'] + s['teleopballs'] + s['end']
            if s['autogears']:
                apr += 20 * min(s['autogears'], 1)
            if s['autogears'] > 1:
                apr += (s['autogears'] - 1) * 10   
                
            apr += max(min(s['teleopgears'], 2 - s['autogears']) * 20, 0)
            if s['autogears'] + s['teleopgears'] > 2:
                apr += min(s['teleopgears'] + s['autogears'] - 2, 4) * 10
            if s['autogears'] + s['teleopgears'] > 6:
                apr += min(s['teleopgears'] + s['autogears'] - 6, 6) * 7
            apr = int(apr)

            #replace the data entry with a new one
            cursor.execute('INSERT INTO averages VALUES (?,?,?,?,?,?,?,?,?)',(n, apr, s['autogears'], s['teleopgears'], s['geardrop'], s['autoballs'], s['teleopballs'], s['end'], s['defense']))
        conn.commit()
        conn.close()
        
        # Calculates average scores for a team
    def calcavgNoD(self, n, event):
        datapath = 'data_' + event + '.db'
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        #delete the existing entry, if a team has no matches they will be removed
        cursor.execute('DELETE FROM noDefense WHERE team=?',(n,))
        #d0 is the identifier for team, Match is the identifier for match
        entries = cursor.execute('SELECT * FROM scout WHERE Team=? AND Flag=0 AND Defense=0 ORDER BY Match DESC', (n,)).fetchall()
        s = {'autogears': 0, 'teleopgears': 0, 'geardrop': 0, 'autoballs': 0, 'teleopballs':0, 'end': 0, 'defense': 0}
        apr = 0
        # Iterate through all entries (if any exist) and sum all categories
        if entries:
            for e in entries:
                s['autogears'] += e['AutoGears']
                s['teleopgears'] += e['TeleopGears']
                s['autoballs'] += e['AutoLowBalls']/3 + e['AutoHighBalls']
                s['teleopballs'] += e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3
                s['geardrop'] += e['TeleopGearDrops']
                s['end'] += e['Hang']*50
                s['defense'] += e['Defense']

            # take the average (divide by number of entries)
            for key,val in s.items():
                s[key] = round(val/len(entries), 2)

            # formula for calculating APR (point contribution)
            apr = s['autoballs'] + s['teleopballs'] + s['end']
            if s['autogears']:
                apr += 20 * min(s['autogears'], 1)
            if s['autogears'] > 1:
                apr += (s['autogears'] - 1) * 10   
                
            apr += max(min(s['teleopgears'], 2 - s['autogears']) * 20, 0)
            if s['autogears'] + s['teleopgears'] > 2:
                apr += min(s['teleopgears'] + s['autogears'] - 2, 4) * 10
            if s['autogears'] + s['teleopgears'] > 6:
                apr += min(s['teleopgears'] + s['autogears'] - 6, 6) * 7
            apr = int(apr)

            #replace the data entry with a new one
            cursor.execute('INSERT INTO noDefense VALUES (?,?,?,?,?,?,?,?,?)',(n, apr, s['autogears'], s['teleopgears'], s['geardrop'], s['autoballs'], s['teleopballs'], s['end'], s['defense']))
        conn.commit()
        conn.close()
        
    # Calculates average scores for a team
    def calcavgLastThree(self, n, event):
        datapath = 'data_' + event + '.db'
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        #delete the existing entry, if a team has no matches they will be removed
        cursor.execute('DELETE FROM lastThree WHERE team=?',(n,))
        #d0 is the identifier for team, Match is the identifier for match
        entries = cursor.execute('SELECT * FROM scout WHERE Team=? AND Flag=0 ORDER BY Match DESC', (n,)).fetchall()
        s = {'autogears': 0, 'teleopgears': 0, 'geardrop': 0, 'autoballs': 0, 'teleopballs':0, 'end': 0, 'defense': 0}
        apr = 0
        # Iterate through all entries (if any exist) and sum all categories
        if entries:
            entries = entries[0:3]
            for e in entries:
                s['autogears'] += e['AutoGears']
                s['teleopgears'] += e['TeleopGears']
                s['autoballs'] += e['AutoLowBalls']/3 + e['AutoLowBalls']
                s['teleopballs'] += e['TeleopLowBalls']/9 + e['TeleopLowBalls']/3
                s['geardrop'] += e['TeleopGearDrops']
                s['end'] += e['Hang']*50
                s['defense'] += e['Defense']

            # take the average (divide by number of entries)
            for key,val in s.items():
                s[key] = round(val/len(entries), 2)

            # formula for calculating APR (point contribution)
            apr = s['autoballs'] + s['teleopballs'] + s['end']
            if s['autogears']:
                apr += 20 * min(s['autogears'], 1)
            if s['autogears'] > 1:
                apr += (s['autogears'] - 1) * 10   
                
            apr += max(min(s['teleopgears'], 2 - s['autogears']) * 20, 0)
            if s['autogears'] + s['teleopgears'] > 2:
                apr += min(s['teleopgears'] + s['autogears'] - 2, 4) * 10
            if s['autogears'] + s['teleopgears'] > 6:
                apr += min(s['teleopgears'] + s['autogears'] - 6, 6) * 7
            apr = int(apr)

            #replace the data entry with a new one
            cursor.execute('INSERT INTO lastThree VALUES (?,?,?,?,?,?,?,?,?)',(n, apr, s['autogears'], s['teleopgears'], s['geardrop'], s['autoballs'], s['teleopballs'], s['end'], s['defense']))
        conn.commit()
        conn.close()
        
    def calcmaxes(self, n, event):
        datapath = 'data_' + event + '.db'
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        
        #delete entry, if the team has match records left it will be replaced later
        cursor.execute('DELETE FROM maxes WHERE team=?',(n,))
        entries = cursor.execute('SELECT * FROM scout WHERE Team = ? AND Flag=0 ORDER BY Match DESC',(n,)).fetchall()
        s = {'autogears': 0, 'teleopgears': 0, 'geardrop': 0, 'autoballs': 0, 'teleopballs':0, 'end': 0, 'apr':0, 'defense': 0 }
        apr = 0
        # Iterate through all entries (if any exist) and sum all categories
        if entries:
            for e in entries:
                s['autogears'] = max(s['autogears'], e['AutoGears'])
                s['teleopgears'] = max(s['teleopgears'], e['TeleopGears'])
                s['autoballs'] = max(s['autoballs'], (e['AutoLowBalls']/3 + e['AutoHighBalls']))
                s['teleopballs'] = max(s['teleopballs'], (e['TeleopLowBalls']/9 + e['TeleopHighBalls']/3))
                s['geardrop'] = max(s['geardrop'], e['TeleopGearDrops'])
                s['end'] = max(s['end'], e['Hang']*50)
                s['defense'] = max(s['defense'], e['Defense'])
                apr = (e['AutoLowBalls']/3 + e['AutoHighBalls']) + (e['TeleopLowBalls']/9 + e['AutoHighBalls']/3) + e['Hang']*50
                if e['AutoGears']:
                    apr += 60
                if e['AutoGears'] > 1:
                    apr += (e['AutoGears'] - 1) * 30   
                    
                apr += min(min(e['TeleopGears'], 2 - e['AutoGears']) * 20, 0)
                if e['AutoGears'] + e['TeleopGears'] > 2:
                    apr += min(e['TeleopGears'] + e['AutoGears'] - 2, 4) * 10
                if e['AutoGears'] + e['TeleopGears'] > 6:
                    apr += min(e['TeleopGears'] + e['AutoGears'] - 6, 6) * 7
                s['apr'] = max(s['apr'], (int(apr)))

        for key,val in s.items():
            s[key] = round(val, 2)
        #replace the data entry with a new one

        cursor.execute('INSERT INTO maxes VALUES (?,?,?,?,?,?,?,?,?)',(n, s['apr'], s['autogears'], s['teleopgears'], s['geardrop'], s['autoballs'], s['teleopballs'], s['end'], s['defense']))
        conn.commit()
        conn.close()

    # Return the path to the database for this event
    def datapath(self):
        return 'data_' + self.getevent() + '.db'

    # Return the selected event
    def getevent(self):
        if 'event' not in cherrypy.session:
            cherrypy.session['event'] = CURRENT_EVENT
        return cherrypy.session['event']
    
    def getMatches(self, event, team=''):
        headers = {"X-TBA-App-Id": "frc2067:scouting-system:v02"}
        try:
            if team:
                #request a specific team
                m = requests.get("http://www.thebluealliance.com/api/v2/team/frc{0}/event/{1}/matches".format(team, event), params=headers)
            else:
                #get all the matches from this event
                m = requests.get("http://www.thebluealliance.com/api/v2/event/{0}/matches".format(event), params=headers)
            if m.status_code == 400 or m.status_code == 404:
                raise Exception
            if m.text != '[]':
                with open(event + "_matches.json", "w+") as file:
                    file.write(str(m.text))
                m = m.json()
            else:
                m = []
        except:
            try:
                with open(event + '_matches.json') as matches_data:
                    m = json.load(matches_data)
            except:
                m = []
        return m

    # Wrapper for requests, ensuring nothing goes terribly wrong
    # This code is trash; it just works to avoid errors when running without internet
    def get(self, req, params=""):
        a = None
        try:
            a = requests.get(req, params=params)
            if a.status_code == 404:
                raise Exception #freaking stupid laziness
        except:
            #stupid lazy solution for local mode
            a = requests.get('http://127.0.0.1:8000/submit?data=json')
        return a
    
    def database_exists(self, event):
        datapath = 'data_' + event + '.db'
        if not os.path.isfile(datapath):
            # Generate a new database with the three tables
            conn = sql.connect(datapath)
            conn.row_factory = sql.Row
            cursor = conn.cursor()
            # Replace 36 with the number of entries in main.py
            tableCreate = "CREATE TABLE scout (key INTEGER PRIMARY KEY, "
            for key in SCOUT_FIELDS:
                tableCreate += key + " integer , "
            tableCreate += ")"
            print(tableCreate)
            cursor.execute(tableCreate)
            cursor.execute('''CREATE TABLE averages (team integer,apr integer,autogear real,teleopgear real, geardrop real, autoballs real, teleopballs real, end real)''')
            cursor.execute('''CREATE TABLE maxes (team integer, apr integer, autogear real, teleopgear real, geardrop real, autoballs real, teleopballs real, end real)''')
            cursor.execute('''CREATE TABLE comments (team integer, comment text)''')
            conn.close()
            
    @cherrypy.expose()
    def edit(self, key='', **params):
        datapath = 'data_' + self.getevent() + '.db'
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        if len(params) > 1:
            sqlCommand = 'UPDATE scout SET '
            for name, value in params.items():
                sqlCommand += name + '=' + (value if value else 'NULL') + " , "
            sqlCommand = sqlCommand[:-2]
            sqlCommand+='WHERE key=' + str(key)
            print(sqlCommand)
            cursor.execute(sqlCommand)
            conn.commit()
            conn.close()
            self.calcavg(params['Team'], self.getevent())
            self.calcmaxes(params['Team'], self.getevent())
            self.calcavgNoD(params['Team'], self.getevent())
            self.calcavgLastThree(params['Team'], self.getevent())
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor= conn.cursor()
        entries = cursor.execute('SELECT * from scout ORDER BY flag DESC, Team ASC, Match ASC').fetchall()
                
        if key == '':
            key = entries[0][0]
        combobox = ''

        for e in entries:
            combobox += '''<option id="{0}" value="{0}">{1} Team {2}: Match {3}</option>\n'''.format(e['Key'], "*" if e['Flag'] else "", e['Team'], e['Match'])
                         
        
        entry = cursor.execute('SELECT * from scout WHERE key=?', (key,)).fetchone()
        conn.close()
        
        i = 0
        leftEdit = ''
        rightEdit = ''
        for key in SCOUT_FIELDS:
            print(key)
            if(key == 'Replay'):
                continue
            if(i < len(SCOUT_FIELDS)/2):
                leftEdit += '''<div><label for="team" class="editLabel">{0}</label>
                            <input class="editNum" type="number" name="{0}" value="{1}"></div>'''.format(key, entry[key])
            else:
                rightEdit += '''<div><label for="team" class="editLabel">{0}</label>
                            <input class="editNum" type="number" name="{0}" value="{1}"></div>'''.format( key, entry[key])
            i = i+1
        with open('web/edit.html', 'r') as file:
            page = file.read()
        return page.format(combobox, entry['Team'], entry['Match'], entry['Key'], leftEdit, rightEdit)
        
            
    @cherrypy.expose()
    def rankings(self):
        event = self.getevent()
        datapath = 'data_' + event + '.db'
        self.database_exists(event)
        conn = sql.connect(datapath)
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        
        rankings = {}
        
        headers = {"X-TBA-App-Id": "frc2067:scouting-system:v02"}
        m = requests.get("http://www.thebluealliance.com/api/v2/event/{0}/matches".format(event), params=headers)
        r = requests.get("http://www.thebluealliance.com/api/v2/event/{0}/rankings".format(event), params=headers)
        if 'feed' in m:
            raise cherrypy.HTTPError(503, "Unable to retrieve data about this event.")
        if r.text != '[]':
            r = r.json()
        else:
            raise cherrypy.HTTPError(503, "Unable to retrieve rankings data for this event.")
        if m.text != '[]':
            m = m.json()
        else:
            raise cherrypy.HTTPError(503, "Unable to retrieve match data for this event.")
 
        del r[0]
        for item in r:
            rankings[str(item[1])] = {'rp': round(item[2]*item[9],0), 'matchScore': item[3], 'currentRP': round(item[2]*item[9],0), 'currentMatchScore': item[3]}
            
        for match in m:
            if match['comp_level'] == 'qm':
                if match['alliances']['blue']['score'] == -1:
                    blueTeams = [match['alliances']['blue']['teams'][0][3:], match['alliances']['blue']['teams'][1][3:], match['alliances']['blue']['teams'][2][3:]]
                    blueResult = self.predictScore(blueTeams)
                    blueRP = blueResult['fuelRP'] + blueResult['gearRP']
                    redTeams = [match['alliances']['red']['teams'][0][3:], match['alliances']['red']['teams'][1][3:], match['alliances']['red']['teams'][2][3:]]
                    redResult = self.predictScore(redTeams)
                    redRP = redResult['fuelRP'] + redResult['gearRP']
                    if blueResult['score'] > redResult['score']:
                        blueRP += 2
                    elif redResult['score'] > blueResult['score']:
                        redRP += 2
                    else:
                        redRP += 1
                        blueRP += 1
                    for team in blueTeams:
                        rankings[team]['rp'] += blueRP
                        rankings[team]['matchScore'] += blueResult['score']
                    for team in redTeams:
                        rankings[team]['rp'] += redRP
                        rankings[team]['matchScore'] += redResult['score']

        output = ''
        for index,out in enumerate(sorted(rankings.items(), key=keyFromItem(lambda k,v: (v['rp'], v['matchScore'])), reverse=True)):
            output += '''
            <tr role="row">
                <td>{0}</td>
                <td><a href="/team?n={1}">{1}</a></td>
                <td class="hidden-xs">{2}</td>
                <td class="hidden-xs">{3}</td>
                <td class="hidden-xs">{4}</td>
                <td class="hidden-xs">{5}</td>
               

                
                <td class="rankingColumn rankColumn1 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{2}</td>
                <td class="rankingColumn rankColumn2 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{3}</td>
                <td class="rankingColumn rankColumn3 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{4}</td>
                <td class="rankingColumn rankColumn4 hidden-sm hidden-md hidden-lg hidden-xs" style="display: none;">{5}</td>
               
            </tr>
            '''.format(index + 1, out[0], (int)(out[1]['rp']), (int)(out[1]['matchScore']), (int)(out[1]['currentRP']), (int)(out[1]['currentMatchScore']))
        with open('web/rankings.html', 'r') as file:
            page = file.read()
        return page.format(output)

        
    
    def predictScore(self, teams, level='quals'):
        conn = sql.connect(self.datapath())
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        ballScore = []
        endGame = []
        autoGears = []
        teleopGears = []
        for n in teams:
            average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
            assert len(average) < 2
            if len(average):
                entry = average[0]
            else:
                entry = [0]*8
            autoGears.append(entry[2])
            teleopGears.append(entry[3])
            ballScore.append((entry[5]+entry[6]))
            endGame.append((entry[7]))
        retVal = {'score': 0, 'gearRP': 0, 'fuelRP': 0}
        score = sum(ballScore[0:3]) + sum(endGame[0:3])
        if sum(autoGears[0:3]) >= 1:
            score += 60
        else:
            score += 40
        if sum(autoGears[0:3]) >= 3:
            score += 60
        elif sum(autoGears[0:3] + teleopGears[0:3]) >= 2:
            score += 40
        if sum(autoGears[0:3] + teleopGears[0:3]) >= 6:
            score += 40
        if sum(autoGears[0:3] + teleopGears[0:3]) >= 12:
            score += 40
            if level == 'playoffs':
                score += 100
            else:
                retVal['gearRP'] == 1
        if sum(ballScore[0:3]) >= 40:
            if level == 'playoffs':
                score += 20
            else:
                retVal['fuelRP'] == 1
        retVal['score'] = score
        return retVal
            
    #END OF CLASS

# Execution starts here
datapath = 'data_' + CURRENT_EVENT + '.db'

def keyFromItem(func):
    return lambda item: func(*item)
    
if not os.path.isfile(datapath):
    # Generate a new database with the three tables
    conn = sql.connect(datapath)
    cursor = conn.cursor()
    # Replace 36 with the number of entries in main.py
    tableCreate = "CREATE TABLE scout (key INTEGER PRIMARY KEY, "
    for key in SCOUT_FIELDS:
        tableCreate += key + " integer, "
    tableCreate = tableCreate[:-2]
    tableCreate += ")"
    print(tableCreate)
    cursor.execute(tableCreate)
    cursor.execute('''CREATE TABLE averages (team integer,apr integer,autogear real,teleopgear real, geardrop real, autoballs real, teleopballs real, end real, defense real)''')
    cursor.execute('''CREATE TABLE maxes (team integer, apr integer, autogear real, teleopgear real, geardrop real, autoballs real, teleopballs real, end real, defense real)''')
    cursor.execute('''CREATE TABLE lastThree (team integer, apr integer, autogear real, teleopgear real, geardrop real, autoballs real, teleopballs real, end real, defense real)''')
    cursor.execute('''CREATE TABLE noDefense (team integer, apr integer, autogear real, teleopgear real, geardrop real, autoballs real, teleopballs real, end real, defense real)''')
    cursor.execute('''CREATE TABLE comments (team integer, comment text)''')
    conn.close()

conf = {
     '/': {
         'tools.sessions.on': True,
         'tools.staticdir.root': os.path.abspath(os.getcwd())
     },
     '/static': {
         'tools.staticdir.on': True,
         'tools.staticdir.dir': './web/static'
     },
     '/favicon.ico': {
        'tools.staticfile.on': True,
        'tools.staticfile.filename': './web/static/img/favicon.ico'
    },
    'global': {
        'server.socket_port': 8000
    }
}

#start method only to be used on the local version
#def start():
#    cherrypy.quickstart(ScoutServer(), '/', conf)

#the following is run on the real server
'''

conf = {
         '/': {
                 'tools.sessions.on': True,
                 'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': './web/static'
         },
        'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 80
        }
}
'''
cherrypy.quickstart(ScoutServer(), '/', conf)

