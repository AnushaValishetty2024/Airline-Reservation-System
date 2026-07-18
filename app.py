"""Airline Reservation System - Main Application."""

import os

from flask import Flask, render_template, request, redirect, url_for, session, g

from models.user import get_db_connection

from routes.auth import auth_bp
from routes.admin_new import admin_new_bp
from routes.user import user_bp
from routes.booking import booking_bp
from routes.payment import payment_bp
from routes.analytics import analytics_bp
from routes.reports import reports
from routes.export_routes import export_bp
from routes.powerbi_routes import powerbi_bp


from services.notification_service import get_unread_count


print("RUNNING APP FROM:", __file__)


app = Flask(
    __name__,
    template_folder="templates"
)

import os

print("APP ROOT:", app.root_path)

print(
    "CANCELLATION FILE:",
    os.path.exists(
        os.path.join(
            app.root_path,
            "templates",
            "analytics",
            "cancellation.html"
        )
    )
)

app.secret_key = os.environ.get(
    'SECRET_KEY',
    'airline_reservation_secret_key_2026'
)


# Register Jinja globals
app.jinja_env.globals['get_unread_count'] = get_unread_count



# Register Blueprints
app.register_blueprint(auth_bp)

app.register_blueprint(admin_new_bp)

app.register_blueprint(user_bp)

app.register_blueprint(booking_bp)

app.register_blueprint(payment_bp)

app.register_blueprint(analytics_bp)

from routes.reports import reports

app.register_blueprint(reports)
app.register_blueprint(export_bp)
app.register_blueprint(powerbi_bp)


@app.before_request
def load_logged_in_user():

    from services.user_service import get_user_by_id

    user_id = session.get("user_id")

    if user_id is None:
        g.current_user = None

    else:
        g.current_user = get_user_by_id(user_id)



@app.context_processor
def inject_user():

    return dict(
        current_user=g.current_user
    )



@app.route('/')
def index():

    return redirect(
        url_for('auth.login')
    )

@app.route("/admin/exports")
def export_page():
    return render_template("admin/exports.html")


# Debug: Show all registered routes
print(app.url_map)



if __name__ == '__main__':

    print("\n========== REGISTERED ROUTES ==========")

    for rule in app.url_map.iter_rules():
        print(rule)

    print("======================================\n")

    app.run(debug=True)