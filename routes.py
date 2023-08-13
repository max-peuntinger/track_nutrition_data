from datetime import datetime
import pytz
from flask import request, render_template, redirect, url_for, session, flash
from foodninja_api import get_food_info_from_api
from data_manager import SQLite3Writer, SQLite3Reader

def register_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if 'food_item' in request.form:
                timestamp = request.form.get('timestamp')
                food_item = request.form.get('food_item')
                weight = request.form.get('weight')
                nutrition_data = get_food_info_from_api(food_item, weight)
                if nutrition_data:
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
        bodyweight_entry = sql_reader.read_single_data(id=id, table='bodyweight')  # Make sure this method is implemented

        if request.method == 'POST':
            weight_data = {}
            weight_data['date'] = request.form.get('date')
            weight_data['bodyweight'] = request.form.get('bodyweight')
            sql_writer = SQLite3Writer('bodyweight.db')
            sql_writer.update_data('bodyweight', weight_data, id)
    # Make sure this method is implemented
            flash('Bodyweight entry updated successfully!', 'success')  # Add a success message
            return redirect(url_for('manage_bodyweight'))  # Redirect back to the manage bodyweight page

        return render_template('modify_bodyweight.html', entry=bodyweight_entry)

    # @app.route('/dashboard', methods=['GET'])
    # def dashboard():
    #     dash_app.layout = create_layout()
    #     return dash_app.index()
    

def process_nutrition_data(food_item, weight, nutrition_data):
    berlin_tz = pytz.timezone('Europe/Berlin')
    berlin_time = datetime.now(berlin_tz)
    data = {}
    data["timestamp"] = berlin_time.isoformat()
    for key, value in nutrition_data["items"][0].items():
        if key == "name":
            data[key] = value
            continue  
        data[key] = float(value) * float(weight)/100.0
    return data