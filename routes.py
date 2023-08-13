from datetime import datetime
import pytz
from flask import request, render_template, redirect, url_for, session, flash
from api.foodninja_api import get_food_info_from_api
from data.data_manager import SQLite3Writer, SQLite3Reader

def register_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if 'food_item' in request.form:
                timestamp = request.form.get('timestamp')
                food_item = request.form.get('food_item')
                weight = request.form.get('weight')
                nutrition_data = get_food_info_from_api(food_item, weight)
                if not nutrition_data or not nutrition_data["items"]:
                    flash('invalid entry!', 'failure')
                    session.pop('data_to_save', None)
                if nutrition_data and nutrition_data["items"]:
                    data = process_nutrition_data(food_item, weight, nutrition_data)
                    data["timestamp"] = timestamp
                    session['data_to_save'] = data
                    sqlwriter = SQLite3Writer('bodyweight.db')
                    sqlwriter.create_data("food_eaten", session["data_to_save"])
                    flash('Data saved successfully!', 'success')
            elif 'bodyweight' in request.form:
                weight_data = {}
                weight_data['date'] = request.form.get('date')
                weight_data['bodyweight'] = request.form.get('bodyweight')
                sql3writer = SQLite3Writer('bodyweight.db')
                sql3writer.create_data('bodyweight', weight_data)
                flash('Data saved successfully!', 'success')
            else:
                flash('Aborted entry!', 'failure')
            session.pop('data_to_save', None)
            return redirect('/')
        return render_template('index.html', data=session.get('data_to_save'))

    @app.route('/manage_food', methods=['GET'])
    def manage_food():
        sql_reader =SQLite3Reader('bodyweight.db')
        food_data = sql_reader.read_data("SELECT * FROM food_eaten ORDER BY timestamp DESC")

        # Render the template and pass the data
        return render_template('manage_food.html', food_data=food_data)

    @app.route('/delete_food_eaten/<int:entry_id>', methods=['POST'])
    def delete_food_eaten(entry_id):
        # Delete the entry from the database
        sql_writer = SQLite3Writer('bodyweight.db')
        sql_writer.delete_data("food_eaten", entry_id)

        # flash a success message
        flash('ENtry deleted successfully!', 'success')

        # Redirect back to the manage food page
        return redirect(url_for('manage_food'))

    @app.route('/manage', methods=['GET'])
    def manage_bodyweight():
        # Read all the bodyweight entries from the database
        sql_reader = SQLite3Reader("bodyweight.db")
        bodyweight_data = sql_reader.read_data("SELECT * FROM bodyweight ORDER BY date DESC")

        # Render the template and pass the data
        return render_template('manage_bodyweight.html', bodyweight_data=bodyweight_data)

    @app.route('/delete_bodyweight/<int:entry_id>', methods=['POST'])
    def delete_bodyweight(entry_id):
        # Delete the entry from the database
        sql_writer = SQLite3Writer('bodyweight.db')
        sql_writer.delete_data('bodyweight', entry_id)

        # Flash a success message
        flash('Entry deleted successfully!', 'success')

        # Redirect back to the manage bodyweight page
        return redirect(url_for('manage_bodyweight'))

    @app.route('/modify_bodyweight/<int:id>', methods=['GET', 'POST'])
    def modify_bodyweight(id):
        sql_reader = SQLite3Reader('bodyweight.db')
        bodyweight_entry = sql_reader.read_single_data(id=id, table='bodyweight')

        if request.method == 'POST':
            weight_data = {}
            weight_data['date'] = request.form.get('date')
            weight_data['bodyweight'] = request.form.get('bodyweight')
            sql_writer = SQLite3Writer('bodyweight.db')
            sql_writer.update_data('bodyweight', weight_data, id)
    # Make sure this method is implemented
            flash('Bodyweight entry updated successfully!', 'success')
            return redirect(url_for('manage_bodyweight'))  # Redirect back to the manage bodyweight page
        bodyweight_entry_dict = bodyweight_entry.iloc[0].to_dict()
        return render_template('modify_bodyweight.html', entry=bodyweight_entry_dict)

    @app.route('/modify_food/<int:id>', methods=['GET', 'POST'])
    def modify_food(id):
        sql_reader = SQLite3Reader('bodyweight.db')
        food_entry = sql_reader.read_single_data(id=id, table='food_eaten')
        old_name = food_entry.iloc[0]['name']
        old_serving_size_g = food_entry.iloc[0]['serving_size_g']

        if request.method == 'POST':
            food_data = {}
            food_data['timestamp'] = request.form.get('timestamp')
            food_data['name'] = request.form.get('name')
            food_data['serving_size_g'] = request.form.get('serving_size_g')

            # Check if the name of the food has changed, then the api needs to be called
            if food_data['name'] != old_name or food_data['serving_size_g'] != old_serving_size_g:
                weight = food_data['serving_size_g']
                nutrition_data = get_food_info_from_api(food_data['name'], weight)
                food_data.update(process_nutrition_data(food_data['name'], weight, nutrition_data, timestamp = food_data['timestamp']))

            sql_writer = SQLite3Writer('bodyweight.db')
            sql_writer.update_data('food_eaten', food_data, id)
            flash('Food entry updated successfully!', 'success')
            return redirect(url_for('manage_food'))  # Redirect back to the manage food page

        food_entry_dict = food_entry.iloc[0].to_dict()
        return render_template('modify_food.html', entry=food_entry_dict)
    

def process_nutrition_data(food_item, weight, nutrition_data, timestamp=None):
    data = {}
    if not timestamp:
        berlin_tz = pytz.timezone('Europe/Berlin')
        berlin_time = datetime.now(berlin_tz)
        data["timestamp"] = berlin_time.isoformat()
    else:
        data["timestamp"] = timestamp
    for key, value in nutrition_data["items"][0].items():
        if key == "name":
            data[key] = value
            continue  
        data[key] = float(value) * float(weight)/100.0
    return data