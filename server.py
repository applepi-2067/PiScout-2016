import cherrypy
import sqlite3 as sql
import os
from ast import literal_eval
import requests
import math

# Update this value before every event
CURRENT_EVENT = '2016cars'

class ScoutServer(object):
	@cherrypy.expose
	def index(self, e=''):
		#First part is to handle event selection. When the event is changed, a POST request is sent here.
		illegal = ''
		if e != '':
			if os.path.isfile('data_' + e + '.db'):
				cherrypy.session['event'] = e
			else:
				illegal = e
		if 'event' not in cherrypy.session:
			cherrypy.session['event'] = CURRENT_EVENT

		#This secction generates the table of averages
		table = ''
		conn = sql.connect(self.datapath())
		averages = conn.cursor().execute('SELECT * FROM averages ORDER BY apr DESC').fetchall()
		conn.close()
		for team in averages:
			table += '''
			<tr>
				<td><a href="team?n={0}">{0}</a></td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
				<td>{5}</td>
				<td>{6}</td>
			</tr>
			'''.format(team[0], team[6], team[1], team[2], team[3], team[5], team[7])

		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
				<link href="./static/css/style.css" rel="stylesheet">
				<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
				<script>
				if (typeof jQuery === 'undefined')
				  document.write(unescape('%3Cscript%20src%3D%22/static/js/jquery.js%22%3E%3C/script%3E'));
				</script>
				<script type="text/javascript" src="./static/js/jquery.tablesorter.js"></script>
				<script>
				$(document).ready(function() {{
					$("table").tablesorter();
					$("#{1}").attr("selected", "selected");
					console.log($("#{1}").selected);
					{2}
				}});
				</script>
			</head>
			<body>
			<div style="max-width: 1000px; margin: 0 auto;">
				<br>
				<div style="vertical-align:top; float:left; width: 300px;">
					<h1>PiScout</h1>
					<h2>FRC Team 2067</h2>
					<br><br>
					<p class="main">Search Team</p>
					<form method="get" action="team">
						<input class="field" type="text" maxlength="4" name="n" autocomplete="off"/>
						<button class="submit" type="submit">Submit</button>
					</form>
					<br><br>
					 <p class="main">Change Event</p>
					<form method="post" action="">
						<select class="fieldsm" name="e">
						  <option id="2016ctss" value="2016ctss">Suffield Shakedown</option>
						  <option id="2016ctwat" value="2016ctwat">Waterbury District Event</option>
						  <option id="2016mawor" value="2016mawor">WPI District Event</option>
						  <option id="2016ripro" value="2016ripro">Rhode Island District Event</option>
						  <option id="2016cthar" value="2016cthar">Hartford District Event</option>
						  <option id="2016necmp" value="2016necmp">NE District Championship</option>
						  <option id="2016cars" value="2016cars">Carson Division</option>
						</select>
						<button class="submit" type="submit">Submit</button>
					</form>
					<br><br>
					<p class="main">Compare</p>
					<form method="get" action="compare">
						<select class="fieldsm" name="t">
						  <option value="team">Teams</option>
						  <option value="alliance">Alliances</option>
						</select>
						<button class="submit" type="submit">Submit</button>
					</form>
					<br><br>
					<p class="main">View Matches</p>
					<form method="get" action="matches">
						<select class="fieldsm" name="n">
						  <option value="2067">Our matches</option>
						  <option value="0">All matches</option>
						</select>
						<button class="submit" type="submit">Submit</button>
					</form>
				</div>

				<div style="vertical-align:top; border 1px solid black; overflow: hidden">
				 <table style="font-size: 140%;" class="tablesorter">
					<thead><tr>
						<th>Team</th>
						<th>APR</th>
						<th>Auto</th>
						<th>Defenses</th>
						<th>Shooting</th>
						<th>Endgame</th>
						<th>Goals</th>
					</tr></thead>
					<tbody>{0}</tbody>
				</table>
				</div>
			</div>
			</body>
		</html>'''.format(table, cherrypy.session['event'],
						  '''alert('There is no data for the event "{}"')'''.format(illegal) if illegal else '')

	# Show a detailed summary for a given team
	@cherrypy.expose()
	def team(self, n="2067"):
		if not n.isdigit():
			raise cherrypy.HTTPRedirect('/')
		if int(n)==666:
			raise cherrypy.HTTPError(403, 'Satan has commanded me to not disclose his evil strategy secrets.')
		#self.calcavg(n)
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		entries = cursor.execute('SELECT * FROM scout WHERE d0=? ORDER BY d1 DESC', (n,)).fetchall()
		#'''CREATE TABLE averages (team integer,auto real,def real, shoot real, accur integer, end real,apr integer)'''
		averages = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
		assert len(averages) < 2 #ensure there aren't two entries for one team
		if len(averages):
			s = averages[0]
		else:
			s = [0]*7 #generate zeros if no data exists for the team yet

		comments = cursor.execute('SELECT * FROM comments WHERE team=?', (n,)).fetchall()
		conn.close()

		# Generate html for comments section
		commentstr = ''
		for comment in comments:
			commentstr += '<div class="commentbox"><p>{}</p></div>'.format(comment[1])

		#Iterate through all the data entries and generate some text to go in the main table
		output = ''
		dataset = []
		labels = ['portcullis', 'cheval', 'moat', 'ramparts', 'drawbridge', 'sally', 'rock wall', 'terrain', 'low bar']
		for e in entries:
			dp = {"match": e[1], "shoot":0, "def":0, "auto":0, "accur":0}
			a = ''
			a += '' if e[6] else 'not preloaded, '
			a += 'spy box, ' if e[4] else ''
			if any(e[10:19]): #if any of the defenses were crossed
				dp['auto'] += 10
				for num,lab in enumerate(labels):
					a += str(e[10+num]) + 'x ' + lab + ', ' if e[10+num] else ''	
			elif e[5]:
				dp['auto'] += 2 #otherwsie add points if reach
				a += 'reach, '
			dp['auto'] += e[7]*10 #high goal
			a += str(e[7]) + 'x high goal, ' if e[7] else ''
			dp['auto'] += e[8]*5 #low goal
			a += str(e[8]) + 'x low goal, ' if e[8] else ''
			a += str(e[9]) + 'x miss, ' if e[9] else ''
			
			d = ''
			dp['def'] += 5*sum([min(2,a) for a in e[19:28]]) #points for crossing defenses
			for num,lab in enumerate(labels):
				d += str(e[19+num]) + 'x ' + lab + ', ' if e[19+num] else ''	

			sh = ''
			dp['shoot'] += e[30]*2 + e[28]*5 #add low/high goal points
			sh += str(e[28]) + 'x high goal, ' if e[28] else ''
			sh += str(e[29]) + 'x high miss, ' if e[29] else ''
			sh += str(e[30]) + 'x low goal, ' if e[30] else ''
			dp['accur'] = int(100*e[28]/(e[28]+e[29])) if e[28] else 0

			o = 'scaling, ' if e[32] else 'challenging, ' if e[31] else ''
			o += 'failed scale, ' if e[33] else ''
			o += str(e[2]) + 'x foul, ' if e[2] else ''
			o += str(e[3]) + 'x tech foul, ' if e[3] else ''
			o += 'defense, ' if e[34] else ''
			o += 'feeder, ' if e[35] else ''

			#dp['end'] += e[32]*15 if e[32] else e[31]*5 #scale/challenge points

			output += '''
			<tr {5}>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td>{4}</td>
				<td><a class="flag" href="javascript:flag({6}, {7});">X</a></td>
			</tr>'''.format(e[1], a[:-2], d[:-2], sh[:-2], o[:-2], 'style="color: #B20000"' if e[36] else '', e[1], e[36])
			for key,val in dp.items():
				dp[key] = round(val, 2)
			if not e[36]:
				dataset.append(dp)
		dataset.reverse() #reverse so that graph is in the correct order

		#Grab the image from the blue alliance
		imcode = ''
		headers = {"X-TBA-App-Id": "frc2067:scouting-system:v01"}
		m = []
		try:
			#get the picture for a given team
			m = self.get("http://www.thebluealliance.com/api/v2/team/frc{0}/media".format(n), params=headers).json()
			if m.status_code == 400:
				m = []
		except:
			pass #swallow the error lol
		for media in m:
			if media['type'] == 'imgur':
				imcode = '''<br>
				<div style="text-align: center">
				<p style="font-size: 32px; line-height: 0em;">Image</p>
				<img src=http://i.imgur.com/{}.jpg></img>
				</div>'''.format(media['foreign_key'])
				break
			if media['type'] == 'cdphotothread':
				imcode = '''<br>
				<div style="text-align: center">
				<p style="font-size: 32px; line-height: 0em;">Image</p>
				<img src=http://chiefdelphi.com/media/img/{}></img>
				</div>'''.format(media['details']['image_partial'].replace('_l', '_m'))
				break
		
		return '''
		<html>
			<head>
				<title>{0} | PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
         		<script type="text/javascript" src="/static/js/amcharts.js"></script>
				<script type="text/javascript" src="/static/js/serial.js"></script>
				<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
				<script>
				if (typeof jQuery === 'undefined')
				  document.write(unescape('%3Cscript%20src%3D%22/static/js/jquery.js%22%3E%3C/script%3E'));
				</script>
				<script>
					var chart;
					var graph;

					var chartData = {8};

					AmCharts.ready(function () {{
						// SERIAL CHART
						chart = new AmCharts.AmSerialChart();

						chart.dataProvider = chartData;
						chart.marginLeft = 10;
						chart.categoryField = "match";

						// AXES
						// category
						var categoryAxis = chart.categoryAxis;
						categoryAxis.dashLength = 3;
						categoryAxis.minorGridEnabled = true;
						categoryAxis.minorGridAlpha = 0.1;

						// value
						var valueAxis = new AmCharts.ValueAxis();
						valueAxis.position = "left";
						valueAxis.axisColor = "#111111";
						valueAxis.gridAlpha = 0;
						valueAxis.axisThickness = 2;
						chart.addValueAxis(valueAxis)

						var valueAxis2 = new AmCharts.ValueAxis();
						valueAxis2.position = "right";
						valueAxis2.axisColor = "#FCD202";
						valueAxis2.gridAlpha = 0;
						valueAxis2.axisThickness = 2;
						chart.addValueAxis(valueAxis2);

						// GRAPH
						graph = new AmCharts.AmGraph();
						graph.title = "Shoot Points";
						graph.valueAxis = valueAxis;
						graph.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph.lineColor = "#637bb6";
						graph.bullet = "round";
						graph.bulletSize = 8;
						graph.bulletBorderColor = "#FFFFFF";
						graph.bulletBorderAlpha = 1;
						graph.bulletBorderThickness = 2;
						graph.lineThickness = 2;
						graph.valueField = "shoot";
						graph.balloonText = "Shoot Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph);

						graph2 = new AmCharts.AmGraph();
						graph2.title = "Defense Points";
						graph2.valueAxis = valueAxis;
						graph2.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph2.lineColor = "#187a2e";
						graph2.bullet = "round";
						graph2.bulletSize = 8;
						graph2.bulletBorderColor = "#FFFFFF";
						graph2.bulletBorderAlpha = 1;
						graph2.bulletBorderThickness = 2;
						graph2.lineThickness = 2;
						graph2.valueField = "def";
						graph2.balloonText = "Defense Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph2);

						graph3 = new AmCharts.AmGraph();
						graph3.title = "Auto Points";
						graph3.valueAxis = valueAxis;
						graph3.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph3.lineColor = "#FF6600";
						graph3.bullet = "round";
						graph3.bulletSize = 8;
						graph3.bulletBorderColor = "#FFFFFF";
						graph3.bulletBorderAlpha = 1;
						graph3.bulletBorderThickness = 2;
						graph3.lineThickness = 2;
						graph3.valueField = "auto";
						graph3.balloonText = "Auto Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph3);

						graph4 = new AmCharts.AmGraph();
						graph4.valueAxis = valueAxis2;
						graph4.title = "High Goal Accuracy";
						graph4.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph4.lineColor = "#FCD202";
						graph4.bullet = "round";
						graph4.bulletSize = 8;
						graph4.bulletBorderColor = "#FFFFFF";
						graph4.bulletBorderAlpha = 1;
						graph4.bulletBorderThickness = 2;
						graph4.lineThickness = 2;
						graph4.valueField = "accur";
						graph4.balloonText = "High Goal Accuracy:<br><b><span style='font-size:14px;'>[[value]]%</span></b>";
						chart.addGraph(graph4);

						// CURSOR
						var chartCursor = new AmCharts.ChartCursor();
						chartCursor.cursorAlpha = 0;
						chartCursor.cursorPosition = "mouse";
						chart.addChartCursor(chartCursor);

						var legend = new AmCharts.AmLegend();
						legend.marginLeft = 110;
						legend.useGraphSettings = true;
						chart.addLegend(legend);
						chart.creditsPosition = "bottom-right";

						// WRITE
						chart.write("chartdiv");
					}});

					function flag(m, f)
					{{
						$.post(
							"flag",
							{{num: {0}, match: m, flagval: f}}
						);
						window.location.reload(true);
					}}
				</script>
			</head>
			<body>
				<h1 class="big">Team {0}</h1>
				<h2><a style="color: #B20000" href='/'>PiScout Database</a></h2>
				<br><br>
				<div style="text-align:center;">
					<div id="apr">
						<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
						<p style="font-size: 400%; line-height: 0em">{7}</p>
					</div>
					<div id="stats">
						<p class="statbox" style="font-weight:bold">Average match:</p>
						<p class="statbox">Auto points: {2}</p>
						<p class="statbox">Defense points: {3}</p>
						<p class="statbox">Shooting points: {4}</p>
						<p class="statbox">High goal accuracy: {5}%</p>
						<p class="statbox">Endgame points: {6}</p>
					</div>
				</div>
				<br>
				<div id="chartdiv" style="width:1000px; height:400px; margin: 0 auto;"></div>
				<br>
				<table>
					<thead><tr>
						<th>Match</th>
						<th>Auto</th>
						<th>Defenses</th>
						<th>Shooting</th>
						<th>Other</th>
						<th>Flag</th>
					</tr></thead>{1}
				</table>
				{9}
				<br>
				<div style="text-align: center; max-width: 700px; margin: 0 auto;">
					<p style="font-size: 32px; line-height: 0em;">Comments</p>
					{10}
					<form style="width: 100%; max-width: 700px;" method="post" action="submit">
						<input name="team" value="{0}" hidden/>
						<textarea name="comment" rows="3"></textarea>
						<button class="submit" type="submit">Submit</button>
					</form>
				</div>
				<br>
				<p style="text-align: center; font-size: 24px"><a href="/matches?n={0}">View this team's match schedule</a></p>
			</body>
		</html>'''.format(n, output, s[1], s[2], s[3], s[4], s[5], s[6], str(dataset).replace("'",'"'), imcode, commentstr)

	# Called to flag a data entry
	@cherrypy.expose()
	def flag(self, num='', match='', flagval=0):
		if not (num.isdigit() and match.isdigit()):
			return '<img src="http://goo.gl/eAs7JZ" style="width: 1200px"></img>'
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		cursor.execute('UPDATE scout SET flag=? WHERE d0=? AND d1=?', (int(not int(flagval)),num,match))
		conn.commit()
		conn.close()
		self.calcavg(num)
		return ''

	# Input interface to compare teams or alliances
	@cherrypy.expose()
	def compare(self, t='team'):
		return 		'''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
			</head>
			<body>
				<h1 class="big">Compare {0}s</h1>
				<h2><a style="color: #B20000" href='/'>PiScout Database</a></h2>
				<br><br>
				{1}
		</html>'''.format(t.capitalize(), '''
				<p class="main">Enter up to 4 teams</p>
				<form method="get" action="teams">
					<input class="field" type="text" maxlength="4" name="n1" autocomplete="off"/>
					<input class="field" type="text" maxlength="4" name="n2" autocomplete="off"/>
					<input class="field" type="text" maxlength="4" name="n3" autocomplete="off"/>
					<input class="field" type="text" maxlength="4" name="n4" autocomplete="off"/>
					<button class="submit" type="submit">Submit</button>
				</form>
		''' if t=='team' else '''
				<p class="main">Enter two alliances</p>
				<form method="get" action="alliances" style="text-align: center; width: 800px; margin: 0 auto;">
					<div style="display: table;">
						<div style="display:table-cell;">
							<input class="field" type="text" maxlength="4" name="b1" autocomplete="off"/>
							<input class="field" type="text" maxlength="4" name="b2" autocomplete="off"/>
							<input class="field" type="text" maxlength="4" name="b3" autocomplete="off"/>
						</div>
						<div style="display:table-cell;">
							<p style="font-size: 64px; line-height: 2.4em;">vs</p>
						</div>
						<div style="display:table-cell;">
							<input class="field" type="text" maxlength="4" name="r1" autocomplete="off"/>
							<input class="field" type="text" maxlength="4" name="r2" autocomplete="off"/>
							<input class="field" type="text" maxlength="4" name="r3" autocomplete="off"/>
						</div>
					</div>
					<button class="submit" type="submit">Submit</button>
				</form>''')

	# Output for team comparison
	@cherrypy.expose()
	def teams(self, n1='', n2='', n3='', n4=''):
		nums = [n1, n2, n3, n4]
		averages = []
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		output = ''
		for n in nums:
			if not n:
				continue
			if not n.isdigit():
				raise cherrypy.HTTPError(400, "You fool! Enter NUMBERS, not letters.")
			average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
			assert len(average) < 2
			if len(average):
				entry = average[0]
			else:
				entry = [0]*7
			# Add a data entry for each team
			output += '''<div style="text-align:center; display: inline-block; margin: 16px;">
							<p><a href="/team?n={0}" style="font-size: 32px; line-height: 0em;">Team {0}</a></p>
							<div id="apr">
								<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
								<p style="font-size: 400%; line-height: 0em">{6}</p>
							</div>
							<div id="stats">
								<p class="statbox" style="font-weight:bold">Match Averages:</p>
								<p class="statbox">Auto points: {1}</p>
								<p class="statbox">Defense points: {2}</p>
								<p class="statbox">Shooting points: {3}</p>
								<p class="statbox">High goal accuracy: {4}%</p>
								<p class="statbox">Endgame points: {5}</p>
							</div>
						</div>'''.format(n, *entry[1:]) #unpack the elements
		conn.close()

		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
			</head>
			<body>
				<h1 class="big">Compare Teams</h1>
				<h2><a style="color: #B20000" href='/'>PiScout Database</a></h2>
				<br><br>
				<div style="margin: 0 auto; text-align: center; max-width: 900px;">
				{0}
				<br><br><br>
				</div>
			</body>
		</html>'''.format(output)

	# Output for alliance comparison
	@cherrypy.expose()
	def alliances(self, b1='', b2='', b3='', r1='', r2='', r3=''):
		nums = [b1, b2, b3, r1, r2, r3]
		averages = []
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		#start a div table for the comparison
		#to later be formatted with sum APR
		output = '''<div style="display: table">
				        <div style="display: table-cell;">
				        <p style="font-size: 36px; color: #0000B8; line-height: 0;">Blue Alliance</p>
					<p style="font-size: 24px; color: #0000B8; line-height: 0.2;">{2}% chance of win</p>
				        <div id="apr">
							<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
							<p style="font-size: 400%; line-height: 0em">{0}</p>
							<br>
						</div>'''
		apr = []
		#iterate through all six teams
		for i,n in enumerate(nums):
			#at halfway pointm switch to the second row
			if i == 3:
				output+='''</div>
						<div style="display: table-cell;">
						<p style="font-size: 36px; color: #B20000; line-height: 0;">Red Alliance</p>
						<p style="font-size: 24px; color: #B20000; line-height: 0.2;">{3}% chance of win</p>
						<div id="apr">
							<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
							<p style="font-size: 400%; line-height: 0em">{1}</p>
							<br>
						</div>'''
			if not n.isdigit():
				raise cherrypy.HTTPError(400, "You fool! Enter six valid team numbers!")
			average = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
			assert len(average) < 2
			if len(average):
				entry = average[0]
			else:
				entry = [0]*7
			apr.append(entry[6])
			output += '''<div style="text-align:center; display: inline-block; margin: 16px;">
							<p><a href="/team?n={0}" style="font-size: 32px; line-height: 0em;">Team {0}</a></p>
							<div id="apr">
								<p style="font-size: 200%; margin: 0.65em; line-height: 0.1em">APR</p>
								<p style="font-size: 400%; line-height: 0em">{6}</p>
							</div>
							<div id="stats">
								<p class="statbox" style="font-weight:bold">Match Averages:</p>
								<p class="statbox">Auto points: {1}</p>
								<p class="statbox">Defense points: {2}</p>
								<p class="statbox">Shooting points: {3}</p>
								<p class="statbox">High goal accuracy: {4}%</p>
								<p class="statbox">Endgame points: {5}</p>
							</div>
						</div>'''.format(n, *entry[1:]) #unpack the elements
		output += "</div></div>"
		prob_red = 1/(1+math.e**(-0.08099*(sum(apr[3:6]) - sum(apr[0:3]))))
		output = output.format(sum(apr[0:3]), sum(apr[3:6]), round((1-prob_red)*100,1), round(prob_red*100,1))
		conn.close()


		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
			</head>
			<body>
				<h1 class="big">Compare Alliances</h1>
				<h2><a style="color: #B20000" href='/'>PiScout Database</a></h2>
				<br><br>
				<div style="margin: 0 auto; text-align: center; max-width: 1000px;">
				{0}
				<br><br><br>
				</div>
			</body>
		</html>'''.format(output)

	# Lists schedule data from TBA
	@cherrypy.expose()
	def matches(self, n=0):
		n = int(n)
		event = self.getevent()
		headers = {"X-TBA-App-Id": "frc2067:scouting-system:v01"}
		try:
			if n:
				#request a specific team
				m = self.get("http://www.thebluealliance.com/api/v2/team/frc{0}/event/{1}/matches".format(n, event), params=headers)
			else:
				#get all the matches from this event
				m = self.get("http://www.thebluealliance.com/api/v2/event/{0}/matches".format(event), params=headers)
			if m.status_code == 400:
				raise cherrypy.HTTPError(400, "Request rejected by The Blue Alliance.")
		except:
			raise cherrypy.HTTPError(503, "Unable to retrieve data about this event.")
		output = ''
		m = m.json()
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
			<tr>
				<td><a href="alliances?b1={1}&b2={2}&b3={3}&r1={4}&r2={5}&r3={6}">{0}</a></td>
				<td><a href="team?n={1}">{1}</a></td>
				<td><a href="team?n={2}">{2}</a></td>
				<td><a href="team?n={3}">{3}</a></td>
				<td><a href="team?n={4}">{4}</a></td>
				<td><a href="team?n={5}">{5}</a></td>
				<td><a href="team?n={6}">{6}</a></td>
				<td>{7}</td>
				<td>{8}</td>
			</tr>
			'''.format(match['num'], match['alliances']['blue']['teams'][0][3:],
						match['alliances']['blue']['teams'][1][3:], match['alliances']['blue']['teams'][2][3:],
						match['alliances']['red']['teams'][0][3:], match['alliances']['red']['teams'][1][3:],
						match['alliances']['red']['teams'][2][3:], match['alliances']['blue']['score'],
						match['alliances']['red']['score'])

		return '''
			<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
			</head>
			<body>
				<h1>Matches{0}</h1>
				<h2><a style="color: #B20000" href='/'>PiScout Database</a></h2>
				<br><br>
				<table>
				<thead><tr>
					<th>Match</th>
					<th>Blue 1</th>
					<th>Blue 2</th>
					<th>Blue 3</th>
					<th>Red 1</th>
					<th>Red 2</th>
					<th>Red 3</th>
					<th>Blue Score</th>
					<th>Red Score</th>
				</tr></thead>
				<tbody>
				{1}
				</tbody>
				</table>
			</body>
			</html>
		'''.format(": {}".format(n) if n else "", output)

	# Used by the scanning program to submit data, and used by comment system to submit data
	@cherrypy.expose()
	def submit(self, data='', team='', comment=''):
		if not (data or team):
			return '''
				<h1>FATAL ERROR</h1>
				<h3>DATA CORRUPTION</h3>
				<p>Erasing database to prevent further damage to the system.</p>'''

		if data == 'json':
			return '[]' #bogus json for local version

		conn = sql.connect(self.datapath())
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
		cursor.execute('INSERT INTO scout VALUES (' + ','.join([str(a) for a in d])  + ',0' + ')')
		conn.commit()
		conn.close()

		self.calcavg(d[0])
		return ''

	# Calculates average scores for a team
	def calcavg(self, n):
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		#d0 is the identifier for team, d1 is the identifier for match
		entries = cursor.execute('SELECT * FROM scout WHERE d0=? AND flag=0 ORDER BY d1 DESC', (n,)).fetchall()
		s = {'auto': 0, 'def': 0, 'shoot': 0, 'end': 0, 'goals':0}
		accur = [0,0]
		apr = 0
		# Iterate through all entries (if any exist) and sum all categories
		if entries:
			for e in entries:
				if any(e[10:19]): #if any of the defenses were crossed
					s['auto'] += 10
				else:
					s['auto'] += 2*e[5] #otherwsie add points if reach
				s['auto'] += e[7]*10 #high goal
				s['auto'] += e[8]*5 #low goal
				s['goals'] += e[30] + e[28]
				s['def'] += 5*sum([min(2,a) for a in e[19:28]]) #points for crossing defenses
				s['shoot'] += e[30]*2 + e[28]*5 #add low/high goal points
	
				accur[0] += e[28] #high shots made
				accur[1] += e[28] + e[29] #high shots attempted
				s['end'] += e[32]*15 if e[32] else e[31]*5 #scale/challenge points

			# take the average (divide by number of entries)
			for key,val in s.items():
				s[key] = round(val/len(entries), 2)
			s['goals'] = round(s['goals'], 1)

			# calculate the percent of shots made (assign 0 if no shots attemped)
			accuracy = int(100*accur[0]/accur[1] if accur[1] else 0)

			# formula for calculating APR (point contribution)
			apr = int(s['auto'] + s['def'] + s['shoot'] + s['end'])

		#replace the data entry with a new one
		cursor.execute('DELETE FROM averages WHERE team=?',(n,))
		cursor.execute('INSERT INTO averages VALUES (?,?,?,?,?,?,?,?)',(n, s['auto'], s['def'], s['shoot'], accuracy, s['end'], apr, s['goals']))
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
	#END OF CLASS

# Execution starts here
datapath = 'data_' + CURRENT_EVENT + '.db'

if not os.path.isfile(datapath):
	# Generate a new database with the three tables
	conn = sql.connect(datapath)
	cursor = conn.cursor()
	cursor.execute('CREATE TABLE scout (' + ','.join([('d' + str(a) + ' integer') for a in range (36)]) + ',flag integer' + ')')
	cursor.execute('''CREATE TABLE averages (team integer,auto real,def real, shoot real, accur integer, end real,apr integer,goals integer)''')
	cursor.execute('''CREATE TABLE comments (team integer, comment text)''')
	conn.close()

conf = {
	 '/': {
		 'tools.sessions.on': True,
		 'tools.staticdir.root': os.path.abspath(os.getcwd())
	 },
	 '/static': {
		 'tools.staticdir.on': True,
		 'tools.staticdir.dir': './public'
	 },
	'global': {
		'server.socket_port': 8000
	}
}

#start method only to be used on the local version
def start():
	cherrypy.quickstart(ScoutServer(), '/', conf)

#the following is run on the real server
'''

conf = {
         '/': {
                 'tools.sessions.on': True,
                 'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/static': {
                 'tools.staticdir.on': True,
                 'tools.staticdir.dir': './public'
         },
        'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 80
        }
}

cherrypy.quickstart(ScoutServer(), '/', conf)
'''

