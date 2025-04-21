<<<<<<< HEAD
from website import create_app, db
from flask_migrate import Migrate
from flask.cli import with_appcontext

import click
app = create_app()
migrate = Migrate(app, db)

# Optional: Register CLI commands manually (not always needed, but helpful for clarity)
@app.cli.command("create_db")
@with_appcontext
def create_db():
    db.create_all()
    print("Database Created!")
    
if __name__ == '__main__':
=======
from website import create_app, db
from flask_migrate import Migrate
from flask.cli import with_appcontext

import click
app = create_app()
migrate = Migrate(app, db)

# Optional: Register CLI commands manually (not always needed, but helpful for clarity)
@app.cli.command("create_db")
@with_appcontext
def create_db():
    db.create_all()
    print("Database Created!")
    
if __name__ == '__main__':
>>>>>>> 11087191ba6c9c67c5ba75a139af05d657e2bf97
    app.run(debug=False)