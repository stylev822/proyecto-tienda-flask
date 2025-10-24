# app.py (Versión simplificada sin variables de entorno)

from flask import Flask, render_template, request, redirect, url_for, g
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA BASE DE DATOS (Directa en el código) ---
# Aquí ponemos los datos de conexión directamente para simplificar.
db_config = {
    "host": "localhost",
    "database": "mi_base",
    "user": "postgres",
    "password": "1234" # ¡Recuerda no subir esto a repositorios públicos!
}

# --- GESTIÓN DE LA BASE DE DATOS (BUENA PRÁCTICA) ---

def get_db():
    """
    Crea y devuelve una conexión a la BD para la petición actual.
    La conexión se reutiliza si se llama a get_db() de nuevo.
    """
    if 'db' not in g:
        # Se conecta usando el diccionario 'db_config' de arriba.
        g.db = psycopg2.connect(**db_config, cursor_factory=DictCursor)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Cierra la conexión a la BD al finalizar la petición."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/equipo')
def equipo():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nombre_completo, cargo FROM personas ORDER BY id;")
    lista_de_personas = cur.fetchall()
    cur.close()
    return render_template('equipo.html', personas=lista_de_personas)

@app.route('/productos')
def listar_productos():
    """Muestra la lista de todos los productos."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, descripcion, precio FROM productos ORDER BY id;")
    lista_de_productos = cur.fetchall()
    cur.close()
    return render_template('productos.html', productos=lista_de_productos)

@app.route('/productos/nuevo')
def mostrar_formulario_producto():
    """Muestra el formulario para agregar un nuevo producto."""
    return render_template('Produc_form.html')

@app.route('/productos', methods=['POST'])
def agregar_producto():
    """Recibe los datos del formulario y los guarda en la BD."""
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s)",
        (nombre, descripcion, precio)
    )
    conn.commit()
    cur.close()
    
    return redirect(url_for('listar_productos'))


# --- ARRANQUE DE LA APLICACIÓN ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)