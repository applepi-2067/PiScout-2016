import cherrypy
import sqlite3 as sql
import os
from ast import literal_eval

class ScoutServer(object):
	@cherrypy.expose
	def index(self):
		conn = sql.connect('data.db')
		things = conn.cursor().execute('SELECT * FROM scout').fetchall()
		conn.close()
		return '''
		<html>
			<head>
				<title>PiScout</title>
				<link href="http://fonts.googleapis.com/css?family=Chau+Philomene+One" rel="stylesheet" type="text/css">
         		<link href="/static/css/style.css" rel="stylesheet">
			</head>
			<body>
				<h1>PiScout</h1>
				<h2>FRC Team 2067</h2>
				<br><br>
				<p class="main">Choose a Team</p>
				<form method="get" action="team">
					<input id="team" type="text" maxlength="4" name="n" autocomplete="off"/>
					<br>
					<button id="submit" type="submit">Submit</button>
				</form>
			</body>
		</html>'''

	@cherrypy.expose()
	def team(self, n=2067):
		conn = sql.connect('data.db')
		things = conn.cursor().execute('SELECT * FROM scout WHERE team=?', (n,)).fetchall()
		conn.close()

		return "check out these neato memes:\n" + str(things)

	@cherrypy.expose
	def submit(self, data=''):
		d = literal_eval(data)
		conn = sql.connect('data.db')
		conn.cursor().execute('INSERT INTO scout VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',((d['team'],d['match']
			,d['auto_tote'],d['auto_RC_zone'],d['auto_RC_step'],int(d['auto_stack']),int(d['in_auto_zone']))
			+ tuple(map(str, d['stacks'])) + (d['coop'],d['tele_RC_step'],int(d['coop_stack']),d['tote_loc'])))
		conn.commit()
		conn.close()
		return data

if not os.path.isfile('data.db'):
	conn = sql.connect('data.db')
	conn.cursor().execute('''CREATE TABLE scout (team integer,match integer,auto_tote integer,auto_RC_zone integer
		,auto_RC_step integer,auto_stack integer,in_auto_zone integer,stack1 text,stack2 text,stack3 text,stack4 text
		,stack5 text,stack6 text,coop integer,tele_RC_step integer,coop_stack integer,tote_loc integer)''')
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
cherrypy.quickstart(ScoutServer(), '/', conf)