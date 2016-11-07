#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#DATABASEURI = "sqlite:///test.db"

DATABASEURI = "postgresql://jab2397:q4wba@104.196.175.120/postgres"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index(): 
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM show_hosted_at")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result['name']
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)
  print "in here"


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/event
#
# notice that the functio name is event() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/event')
def event():
  return render_template("event.html")

@app.route('/<showid>')
def showinfo(showid):
  cmd = 'SELECT show_title FROM show_hosted_at WHERE show_id = :showid';
  c_title = g.conn.execute(text(cmd), showid=showid)

  cmd = 'SELECT show_date FROM show_hosted_at WHERE show_id = :showid';
  c_date = g.conn.execute(text(cmd), showid=showid)

  cmd = 'SELECT show_time FROM show_hosted_at WHERE show_id = :showid';
  c_time = g.conn.execute(text(cmd), showid=showid)

  cmd = 'SELECT show_venue FROM show_hosted_at WHERE show_id = :showid';
  c_venue = g.conn.execute(text(cmd), showid=showid)

  cmd = """
        SELECT X.perf_title, A.artist_name
        FROM (SELECT P.perf_title, P.artist_id
              FROM show_hosted_at S, performance P
              WHERE S.show_id = P.show_id
                    AND S.show_id = :showid) AS X,
             artist as A
        WHERE X.artist_id = A.artist_id""";
  c_perf_artist = g.conn.execute(text(cmd), showid=showid)

  cmd = 'SELECT vendor_name FROM sell WHERE show_id = :showid';
  c_vendor = g.conn.execute(text(cmd), showid=showid)

  cmd = """
        SELECT X.perf_title, A.artist_name
        FROM (SELECT P.perf_title, P.artist_id
              FROM show_hosted_at S, performance P
              WHERE S.show_id = P.show_id
                    AND S.show_id = :showid) AS X,
             artist as A
        WHERE X.artist_id = A.artist_id""";
  c_perf_artist = g.conn.execute(text(cmd), showid=showid)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  # print name
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/', methods=["post", "get"])
def display_name():
  name = request.form['a_name']
  begin_date_time = request.form['begin_date_time']
  end_date_time = request.form['end_date_time']
  print name
  print begin_date_time
  print end_date_time
  n1 = '%' + name + '%'
  
  if begin_date_time == '' and end_date_time == '':
    cmd = """SELECT DISTINCT ON(S2.show_id) S2.show_id, S2.show_title, S2.show_date
           FROM (SELECT S.show_id
                 FROM performs_music_of G, artist A, performance P, show_hosted_at S
                 WHERE G.artist_id = A.artist_id
                       AND A.artist_id = P.artist_id
                       AND P.show_id = S.show_id
                       AND (lower(A.artist_name) LIKE :n2
                            OR lower(S.show_title) LIKE :n2
                            OR lower(P.perf_title) LIKE :n2
                            OR lower(G.genre_type) LIKE :n2 
                            OR lower(S.venue_name) LIKE :n2 )) as X,
           show_hosted_at as S2
           WHERE X.show_id = S2.show_id""";

  elif begin_date_time != '' and end_date_time == '':
    cmd = """SELECT DISTINCT ON(S2.show_id) S2.show_id, S2.show_title, S2.show_date
           FROM (SELECT S.show_id
                 FROM performs_music_of G, artist A, performance P, show_hosted_at S
                 WHERE G.artist_id = A.artist_id
                       AND A.artist_id = P.artist_id
                       AND P.show_id = S.show_id
                       AND (lower(A.artist_name) LIKE :n2
                            OR lower(S.show_title) LIKE :n2
                            OR lower(P.perf_title) LIKE :n2
                            OR lower(G.genre_type) LIKE :n2 
                            OR lower(S.venue_name) LIKE :n2 )) as X,
           show_hosted_at as S2
           WHERE X.show_id = S2.show_id AND S2.show_date >= :d1""";

  elif begin_date_time == '' and end_date_time != '':
    cmd = """SELECT DISTINCT ON(S2.show_id) S2.show_id, S2.show_title, S2.show_date
           FROM (SELECT S.show_id
                 FROM performs_music_of G, artist A, performance P, show_hosted_at S
                 WHERE G.artist_id = A.artist_id
                       AND A.artist_id = P.artist_id
                       AND P.show_id = S.show_id
                       AND (lower(A.artist_name) LIKE :n2
                            OR lower(S.show_title) LIKE :n2
                            OR lower(P.perf_title) LIKE :n2
                            OR lower(G.genre_type) LIKE :n2 
                            OR lower(S.venue_name) LIKE :n2 )) as X,
           show_hosted_at as S2
           WHERE X.show_id = S2.show_id AND S2.show_date <= :d2""";

  else:
    cmd = """SELECT DISTINCT ON(S2.show_id) S2.show_id, S2.show_title, S2.show_date
           FROM (SELECT S.show_id
                 FROM performs_music_of G, artist A, performance P, show_hosted_at S
                 WHERE G.artist_id = A.artist_id
                       AND A.artist_id = P.artist_id
                       AND P.show_id = S.show_id
                       AND (lower(A.artist_name) LIKE :n2
                            OR lower(S.show_title) LIKE :n2
                            OR lower(P.perf_title) LIKE :n2
                            OR lower(G.genre_type) LIKE :n2 
                            OR lower(S.venue_name) LIKE :n2 )) as X,
           show_hosted_at as S2
           WHERE X.show_id = S2.show_id AND (S2.show_date >= :d1 AND S2.show_date <= :d2
)""";

  cursor = g.conn.execute(text(cmd), n2=n1, d1=begin_date_time, d2=end_date_time)
  query_names = []
  for result in cursor:
    # print result
    query_names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(query_data = query_names, x=begin_date_time, y=end_date_time)
  return render_template("index.html", **context)
  #return redirect('/')



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
