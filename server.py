import cherrypy
import sqlite3 as sql
import os
from ast import literal_eval
import requests

# Update this value before every event
CURRENT_EVENT = '2015gal'

class ScoutServer(object):
	@cherrypy.expose
	def index(self, e=''):
		#First part is to handle event selection. When the event is changed, a POST request is sent here.
		illegal = ''
		if e != '':
			if os.path.isfile('data_' + e + '.db'):
				self.getalbum(refresh=True)
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
			'''.format(team[0], team[6], team[1], team[2], team[3], team[4], team[5])

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
						  <option id="2015gal" value="2015gal">Galileo Division</option>
						  <option id="2015necmp" value="2015necmp">District Championship</option>
						  <option id="2015cthar" value="2015cthar">Hartford</option>
						  <option id="2015rismi" value="2015rismi">Rhode Island</option>
						  <option id="2015ctwat" value="2015ctwat">Waterbury</option>
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
						<th>Step</th>
						<th>Tote</th>
						<th>RC/Noodle</th>
						<th>Coop</th>
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
	def team(self, n=2067):
		if not n.isdigit():
			raise cherrypy.HTTPRedirect('/')
		if int(n)==666:
			raise cherrypy.HTTPError(403, 'Satan has commanded me to not disclose his evil strategy secrets.')
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		entries = cursor.execute('SELECT * FROM scout WHERE team=? ORDER BY MATCH DESC', (n,)).fetchall()
		averages = cursor.execute('SELECT * FROM averages WHERE team=?', (n,)).fetchall()
		assert len(averages) < 2 #ensure there aren't two entries for one team
		if len(averages):
			sum = averages[0]
		else:
			sum = [0]*7 #generate zeros if no data exists for the team yet

		comments = cursor.execute('SELECT * FROM comments WHERE team=?', (n,)).fetchall()
		conn.close()

		# Generate html for comments section
		commentstr = ''
		for comment in comments:
			commentstr += '<div class="commentbox"><p>{}</p></div>'.format(comment[1])

		#Iterate through all the data entries and generate some text to go in the main table
		output = ''
		dataset = []
		for e in entries:
			dp = {"match": e[1], "rc":0, "tote":0, "auto":0, "step":0}
			a = ''
			if e[5]: #stacked?
				a += "3 tote; "
				dp['auto'] += 20;
			elif e[2] == 3: #number of totes
				a += "3 tote, not stacked; "
				dp['auto'] += 6
			elif e[2]:
				a += str(e[2]) + ' totes; '
				dp['auto'] += 2*e[2]
			if e[3]:
				dp['auto'] += 8/3 * e[3]
				a += str(e[3]) +  ' RC(s) in zone; '
			if e[4]:
				dp['step'] = e[4]
				a += str(e[4]) + ' RC(s) from step; '
			if e[6]:
				dp['auto'] += 4/3
				a += 'moved into auto zone; '
			s = ''
			for stack in range(7, 13):
				if e[stack] == 'None':
					continue
				st = literal_eval(e[stack])
				if st['capping']:
					s += 'capped '
					dp['rc'] += st['height']*4
				else:
					dp['tote'] += st['height']*2
				s += str(st['height']) + ' stack'
				if st['capped']:
					dp['rc'] += st['height']*4
					s += ', capped'
				if st['noodled']:
					dp['rc'] += 6
					s += '/noodled'
				s += '; '

			#tote location
			o = ''
			if e[13]:
				o += str(e[13]) + ' coop totes; '
			if e[14]:
				o += str(e[14]) + ' RCs from step; '
			if e[16] == 1:
				o += 'all totes from HP'
			elif e[16] == 18:
				o += 'all totes from landfill'
			elif 2 <= e[16] <= 7:
				o += 'most totes from HP'
			elif 17 >= e[16] >= 12:
				o += 'most totes from landfill'
			elif e[16] == 0:
				o += "doesn't pick up gray totes"
			else:
				o += "totes equally from landfill/HP"
			output += '''
			<tr {4}>
				<td>{0}</td>
				<td>{1}</td>
				<td>{2}</td>
				<td>{3}</td>
				<td><a class="flag" href="javascript:flag({5}, {6});">X</a></td>
			</tr>'''.format(e[1], a[:-2], s[:-2], o, 'style="color: #B20000"' if e[17] else '', e[1], e[17])
			for key,val in dp.items():
				dp[key] = round(val, 2)
			if not e[17]:
				dataset.append(dp)

		#Grab the image from picasa
		imcode = ''
		headers = {"GData-Version": "2"}
		images = self.get(self.getalbum(), params=headers).json()
		if 'entry' in images['feed']:
			for img in images['feed']['entry']:
				if img['title']['$t'].split('.')[0] == str(n):
					imcode = '''<br>
						<div style="text-align: center">
						<p style="font-size: 32px; line-height: 0em;">Image</p>
						<img src={}></img>
						</div>'''.format(img['content']['src'])
		return '''
		<html>
			<head>
				<title>PiScout</title>
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
						graph.title = "RC/Noodle Points";
						graph.valueAxis = valueAxis;
						graph.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph.lineColor = "#637bb6";
						graph.bullet = "round";
						graph.bulletSize = 8;
						graph.bulletBorderColor = "#FFFFFF";
						graph.bulletBorderAlpha = 1;
						graph.bulletBorderThickness = 2;
						graph.lineThickness = 2;
						graph.valueField = "tote";
						graph.balloonText = "Tote Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
						chart.addGraph(graph);

						graph2 = new AmCharts.AmGraph();
						graph2.title = "Tote Points";
						graph2.valueAxis = valueAxis;
						graph2.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph2.lineColor = "#187a2e";
						graph2.bullet = "round";
						graph2.bulletSize = 8;
						graph2.bulletBorderColor = "#FFFFFF";
						graph2.bulletBorderAlpha = 1;
						graph2.bulletBorderThickness = 2;
						graph2.lineThickness = 2;
						graph2.valueField = "rc";
						graph2.balloonText = "RC Points:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
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
						graph4.title = "Step RCs";
						graph4.type = "smoothedLine"; // this line makes the graph smoothed line.
						graph4.lineColor = "#FCD202";
						graph4.bullet = "round";
						graph4.bulletSize = 8;
						graph4.bulletBorderColor = "#FFFFFF";
						graph4.bulletBorderAlpha = 1;
						graph4.bulletBorderThickness = 2;
						graph4.lineThickness = 2;
						graph4.valueField = "step";
						graph4.balloonText = "RCs from Step:<br><b><span style='font-size:14px;'>[[value]]</span></b>";
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
						<p class="statbox">Step RCs: {3}</p>
						<p class="statbox">Tote points: {4}</p>
						<p class="statbox">RC/noodle points: {5}</p>
						<p class="statbox">Coop points: {6}</p>
					</div>
				</div>
				<br>
				<div id="chartdiv" style="width:1000px; height:400px; margin: 0 auto;"></div>
				<br>
				<table>
					<thead><tr>
						<th>Match</th>
						<th>Auto</th>
						<th>Stacks</th>
						<th>Other Teleop</th>
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
		</html>'''.format(n, output, sum[1], sum[2], sum[3], sum[4], sum[5], sum[6], str(dataset).replace("'",'"'),imcode, commentstr)

	# Called to flag a data entry
	@cherrypy.expose()
	def flag(self, num='', match='', flagval=0):
		if not (num.isdigit() and match.isdigit()):
			return '<img src="http://goo.gl/eAs7JZ" style="width: 1200px"></img>'
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		cursor.execute('UPDATE scout SET flag=? WHERE team=? AND match=?', (int(not int(flagval)),num,match))
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
								<p class="statbox">Step RCs: {2}</p>
								<p class="statbox">Tote points: {3}</p>
								<p class="statbox">RC/noodle points: {4}</p>
								<p class="statbox">Coop points: {5}</p>
							</div>
						</div>'''.format(n, *entry[1:]) #unpack the elements
		conn.close()

		# Get all the images
		imcode = ''
		headers = {"GData-Version": "2"}
		images = self.get(self.getalbum(), params=headers).json()
		if 'entry' in images['feed']:
			for img in images['feed']['entry']:
				team = img['title']['$t'].split('.')[0]
				if team in nums:
					imcode += '''
						<div style="text-align: center; display: inline-block;">
						<p style="font-size: 32px; line-height: 0em;">Team {0}</p>
						<img src={1}></img>
						</div>'''.format(team, img['content']['src'])

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
				{1}
				</div>
			</body>
		</html>'''.format(output, imcode)

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
								<p class="statbox">Step RCs: {2}</p>
								<p class="statbox">Tote points: {3}</p>
								<p class="statbox">RC/noodle points: {4}</p>
								<p class="statbox">Coop points: {5}</p>
							</div>
						</div>'''.format(n, *entry[1:]) #unpack the elements
		output += "</div></div>"
		output = output.format(sum(apr[0:3]), sum(apr[3:6]))
		conn.close()

		#get all six images
		imcode = ''
		headers = {"GData-Version": "2"}
		images = self.get(self.getalbum(), params=headers).json()
		if 'entry' in images['feed']:
			#outer loop to process the two alliances separately
			for a in [0, 3]:
				for img in images['feed']['entry']:
					team = img['title']['$t'].split('.')[0]
					if team in nums[a:a+3]:
						imcode += '''
							<div style="text-align: center; display: inline-block;">
							<p style="font-size: 32px; line-height: 0em; color: {2}">Team {0}</p>
							<img src={1}></img>
							</div>'''.format(team, img['content']['src'], "#0000B8" if a==0 else "#B20000")

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
				{1}
				</div>
			</body>
		</html>'''.format(output, imcode)

	# Lists schedule data from TBA
	@cherrypy.expose()
	def matches(self, n=0):
		n = int(n)
		event = self.getevent()
		headers = {"X-TBA-App-Id": "frc2067:scouting-system:v01"}
		if n:
			#request a specific team
			m = self.get("http://www.thebluealliance.com/api/v2/team/frc{0}/event/{1}/matches".format(n, event), params=headers)
		else:
			#get all the matches from this event
			m = self.get("http://www.thebluealliance.com/api/v2/event/{0}/matches".format(event), params=headers)
		if m.status_code == 400:
			return "You botched it."
		output = ''
		m = m.json()
		if 'feed' in m:
			raise cherrypy.HTTPError(400, "You can't view matches in offline mode.")

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
			return '{"feed": {"entry": []}}' #bogus json for local version

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
		cursor.execute('INSERT INTO scout VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',((d['team'],d['match']
			,d['auto_tote'],d['auto_RC_zone'],d['auto_RC_step'],int(d['auto_stack']),int(d['in_auto_zone']))
			+ tuple(map(str, d['stacks'])) + (d['coop'],d['tele_RC_step'],int(d['coop_stack']),d['tote_loc'], 0)))
		conn.commit()
		conn.close()

		self.calcavg(d['team'])
		return ''

	# Calculates average scores for a team
	def calcavg(self, n):
		conn = sql.connect(self.datapath())
		cursor = conn.cursor()
		entries = cursor.execute('SELECT * FROM scout WHERE team=? AND flag=0 ORDER BY MATCH DESC', (n,)).fetchall()
		sum = {'auto': 0, 'step': 0, 'tote': 0, 'rc': 0, 'coop': 0}
		apr = 0
		# Iterate through all entries (if any exist) and sum all categories
		if entries:
			for e in entries:
				if e[5]: #stacked?
					sum['auto'] += 20
				elif e[2] == 3: #number of totes
					sum['auto'] += 6
				elif e[2]:
					sum['auto'] += 2*e[2]
				if e[3]:
					sum['auto'] += 8/3 * e[3]
				if e[4]:
					sum['step'] += e[4]
				if e[6]:
					sum['auto'] += 4/3
				for stack in range(7, 13):
					if e[stack] == 'None':
						continue
					st = literal_eval(e[stack])
					if not st['capping']:
						sum['tote'] += st['height'] * 2
					if st['capped'] or st['capping']:
						sum['rc'] += st['height'] * 4
					if st['noodled']:
						sum['rc'] += 6
				if e[13]:
					sum['coop'] += 10*e[13]

			# take the average (divide by number of entries)
			for key,val in sum.items():
				sum[key] = round(val/len(entries), 2)

			# formula for calculating APR
			apr = int(sum['auto']*1.2 + sum['step']*5 + sum['tote'] + sum['rc'] + sum['coop']*0.2)

		#replace the data entry with a new one
		cursor.execute('DELETE FROM averages WHERE team=?',(n,))
		cursor.execute('INSERT INTO averages VALUES (?,?,?,?,?,?,?)',(n, sum['auto'], sum['step'],
																sum['tote'], sum['rc'], sum['coop'], apr))
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

	# Return the URL for a picasa web album
	# Refreshing this will request a new album (if event is changed, for example)
	def getalbum(self, refresh=False):
		if refresh or ('album' not in cherrypy.session):
			headers = {"GData-Version": "2"}
			usr = self.get("https://picasaweb.google.com/data/feed/api/user/110165600126232321372?alt=json", params=headers).json()
			for album in usr['feed']['entry']:
				if album['title']['$t'] == self.getevent():
					cherrypy.session['album'] = album['id']['$t'].replace('entry', 'feed')
		return cherrypy.session['album']
	
	# Wrapper for requests, ensuring nothing goes terribly wrong
	# This code is trash; it just works to avoid errors when running without internet
	def get(self, req, params=""):
		a = None
		try:
			a = requests.get(req, params=params)
			if a.status_code == 404:
				raise Exception
		except:
			#stupid lazy solution for local mode
			a = requests.get('http://127.0.0.1:8000/submit?data=json')
			cherrypy.session['album'] = 'http://127.0.0.1:8000/submit?data=json'
		return a
	#END OF CLASS

# Execution starts here
datapath = 'data_' + CURRENT_EVENT + '.db'

if not os.path.isfile(datapath):
	# Generate a new database with the three tables
	conn = sql.connect(datapath)
	cursor = conn.cursor()
	cursor.execute('''CREATE TABLE scout (team integer,match integer,auto_tote integer,auto_RC_zone integer
		,auto_RC_step integer,auto_stack integer,in_auto_zone integer,stack1 text,stack2 text,stack3 text,stack4 text
		,stack5 text,stack6 text,coop integer,tele_RC_step integer,coop_stack integer,tote_loc integer, flag integer)''')
	cursor.execute('''CREATE TABLE averages (team integer,auto real,step real,tote real,rc real
													,coop real,apr integer)''')
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

