from main import BUILD
from main.routes import dm, um

app=BUILD()

@app.context_processor
def inject_globals():
    return {
        "dm": dm,
        "um": um
    }

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)