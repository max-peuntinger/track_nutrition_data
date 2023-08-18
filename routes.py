from flask import (
    flash,
    Flask,
    redirect,
    render_template,
    Response,
    request,
    url_for,
    session,
)
from api.foodninja_api import get_food_info_from_api
from data_tools.data_manager import SQLite3Writer, DataReader
from data_tools.data_processing import process_nutrition_data
from typing import Dict, Optional


def register_routes(app: Flask) -> None:
    """
    Registers the routes for the Flask application.

    Args:
        app (Flask): The Flask application to register the routes for.
    """

    @app.route("/", methods=["GET", "POST"])
    def index() -> Response:
        """Handles the main index page, allowing users to input food or bodyweight data and also displays the dashboard used to investigate eating and weight patterns.

        Returns:
            Response: The rendered HTML template or a redirect to the same page.
        """

        if request.method == "POST":
            if "food_item" in request.form:
                timestamp = request.form.get("timestamp")
                food_item = request.form.get("food_item")
                weight = request.form.get("weight")
                nutrition_data = get_food_info_from_api(food_item, weight)
                if not nutrition_data or not nutrition_data["items"]:
                    flash("invalid entry!", "failure")
                    session.pop("data_to_save", None)
                if nutrition_data and nutrition_data["items"]:
                    data = process_nutrition_data(weight, nutrition_data)
                    data["timestamp"] = timestamp
                    session["data_to_save"] = data
                    sqlwriter = SQLite3Writer("data/bodyweight.db")
                    sqlwriter.create_data("food_eaten", session["data_to_save"])
                    flash("Data saved successfully!", "success")
            elif "bodyweight" in request.form:
                weight_data = {}
                weight_data["date"] = request.form.get("date")
                weight_data["bodyweight"] = request.form.get("bodyweight")
                sql3writer = SQLite3Writer("data/bodyweight.db")
                sql3writer.create_data("bodyweight", weight_data)
                flash("Data saved successfully!", "success")
            else:
                flash("Aborted entry!", "failure")
            session.pop("data_to_save", None)
            return redirect("/")
        return render_template("index.html", data=session.get("data_to_save"))

    @app.route("/manage_food", methods=["GET"])
    def manage_food() -> Response:
        """Displays the management page for food data where entries made on the index page can be edited or deleted.

        Returns:
            Response: The rendered HTML template for managing food data.
        """
        data_reader = DataReader("data/bodyweight.db")
        food_data = data_reader.read_food_eaten_data()
        return render_template("manage_food.html", food_data=food_data)

    @app.route("/delete_food_eaten/<int:entry_id>", methods=["POST"])
    def delete_food_eaten(entry_id: int) -> Response:
        """Deletes a specific food entry.

        Args:
            entry_id (int): The ID of the food entry to delete.

        Returns:
            Response: A redirect to the manage_food page.
        """
        sql_writer = SQLite3Writer("data/bodyweight.db")
        sql_writer.delete_data("food_eaten", entry_id)
        flash("Entry deleted successfully!", "success")
        return redirect(url_for("manage_food"))

    @app.route("/modify_food/<int:id>", methods=["GET", "POST"])
    def modify_food(id: int) -> Response:
        """Allows the user to modify a specific food entry. If the type of food or the weight is changed, a new API call is performed. If the date is changed, the value is just edited.

        Args:
            id (int): The ID of the food entry to modify.

        Returns:
            Response: The rendered HTML template for modifying food data or a redirect to the manage_food page.
        """
        data_reader = DataReader("data/bodyweight.db")
        food_entry = data_reader.read_single_food_entry(id=id)
        old_name = food_entry.iloc[0]["name"]
        old_serving_size_g = food_entry.iloc[0]["serving_size_g"]

        if request.method == "POST":
            food_data = {}
            food_data["timestamp"] = request.form.get("timestamp")
            food_data["name"] = request.form.get("name")
            food_data["serving_size_g"] = request.form.get("serving_size_g")

            # Check if the name of the food has changed, then the api needs to be called
            if (
                food_data["name"] != old_name
                or food_data["serving_size_g"] != old_serving_size_g
            ):
                weight = food_data["serving_size_g"]
                nutrition_data = get_food_info_from_api(food_data["name"], weight)
                food_data.update(
                    process_nutrition_data(
                        weight,
                        nutrition_data,
                        timestamp=food_data["timestamp"],
                    )
                )

            sql_writer = SQLite3Writer("data/bodyweight.db")
            sql_writer.update_data("food_eaten", food_data, id)
            flash("Food entry updated successfully!", "success")
            return redirect(url_for("manage_food"))

        food_entry_dict = food_entry.iloc[0].to_dict()
        return render_template("modify_food.html", entry=food_entry_dict)

    @app.route("/manage", methods=["GET"])
    def manage_bodyweight() -> Response:
        """Displays the management page for bodyweight data.

        Returns:
            Response: The rendered HTML template for managing bodyweight data.
        """
        data_reader = DataReader("data/bodyweight.db")
        bodyweight_data = data_reader.read_bodyweight_data()
        return render_template(
            "manage_bodyweight.html", bodyweight_data=bodyweight_data
        )

    @app.route("/delete_bodyweight/<int:entry_id>", methods=["POST"])
    def delete_bodyweight(entry_id: int) -> Response:
        """Deletes a specific bodyweight entry.

        Args:
            entry_id (int): The ID of the bodyweight entry to delete.

        Returns:
            Response: A redirect to the manage_bodyweight page.
        """
        sql_writer = SQLite3Writer("data/bodyweight.db")
        sql_writer.delete_data("bodyweight", entry_id)
        flash("Entry deleted successfully!", "success")
        return redirect(url_for("manage_bodyweight"))

    @app.route("/modify_bodyweight/<int:id>", methods=["GET", "POST"])
    def modify_bodyweight(id: int) -> Response:
        """Allows the user to modify a specific bodyweight entry.

        Args:
            id (int): The ID of the bodyweight entry to modify.

        Returns:
            Response: The rendered HTML template for modifying bodyweight data or a redirect to the manage_bodyweight page.
        """
        data_reader = DataReader("data/bodyweight.db")
        bodyweight_entry = data_reader.read_single_bodyweight_entry(id=id)

        if request.method == "POST":
            weight_data = {}
            weight_data["date"] = request.form.get("date")
            weight_data["bodyweight"] = request.form.get("bodyweight")
            sql_writer = SQLite3Writer("data/bodyweight.db")
            sql_writer.update_data("bodyweight", weight_data, id)
            flash("Bodyweight entry updated successfully!", "success")
            return redirect(url_for("manage_bodyweight"))
        bodyweight_entry_dict = bodyweight_entry.iloc[0].to_dict()
        return render_template("modify_bodyweight.html", entry=bodyweight_entry_dict)
