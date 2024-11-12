# Import the dependencies.
# 1. import Flask
import os
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


os.chdir(os.path.dirname(os.path.realpath(__file__)))
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# HTML Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= '2016-08-23').all()
    session.close()


    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)
   
# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query for the dates and temperature observations of the most active station for the last year of data
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(
        func.count(Measurement.station).desc()).first()[0]
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station).filter(
        Measurement.date >= '2016-08-23').all()
    session.close()

    tobs_data = [{date: tobs} for date, tobs in results]
    return jsonify(tobs_data)

# Start route (for temperature stats)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start=None, end=None):
    session = Session(engine)

# Query for temperature statistics
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        # If end date is provided, filter between start and end date
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        # If no end date, filter from start date onward
        results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    # Convert the query results to a list
    temps_data = list(results[0])
    return jsonify({"TMIN": temps_data[0], "TAVG": temps_data[1], "TMAX": temps_data[2]})


# @app.route("/")
# def index():
#     # raw html
#     content = (
#         "Hello, world!<br>"
#         "To learn more please visit our <a href='/about'>About</a> page<br>"       
#         "Contact us as at <a href='/contact'>Contact</a> page<br>"
#         "/api/v1.0/tobs<br>"
#         "/api/v1.0/tstats/&lt;start&gt;<br>"
#         "/api/v1.0/tstats/&lt;start&gt;/&lt;end&gt;<br>"
#         )
#     return content

#################################################
# API Routes
#################################################

# @app.route("/api/v1.0/tstats/<start>/")
# @app.route("/api/v1.0/tstats/<start>/<end>/")
# def tstats(start, end=dt.date.max):
#     session = Session(engine)

#     session.close()
#     return jsonify([start, end])

if __name__ == "__main__":
    app.run(debug=True)
