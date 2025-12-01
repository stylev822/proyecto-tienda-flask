# app.py (Versión simplificada sin variables de entorno)

import os
from flask import Flask, render_template, request, redirect, url_for, g, jsonify, session
# IMPORTAMOS NUESTRO NUEVO MÓDULO DE CONEXIÓN
import psycopg2
from database import get_db, close_db 
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'mi_clave_super_secreta_y_dificil'

# Registramos la función para cerrar la BD automáticamente
app.teardown_appcontext(close_db)
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


@app.route('/usuarios')
def listar_usuarios():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM usuarios ORDER BY id;")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios/nuevo')
def mostrar_formulario_usuario():
    return render_template('registro.html')

@app.route('/usuarios/crear', methods=['POST'])
def crear_usuario():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    # ¡AQUÍ ESTÁ LA MAGIA DEL CIFRADO!
    # Convertimos "12345" en algo como "scrypt:32768:8:1$..."
    password_hash = generate_password_hash(password)

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)",
            (username, password_hash, role)
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        return "El nombre de usuario ya existe. Intenta con otro."
    finally:
        cur.close()

    # --- BORRA LA LÍNEA QUE DICE: return redirect(url_for('listar_usuarios')) ---
    # --- Y PEGA ESTE BLOQUE NUEVO EN SU LUGAR: ---

    # Si quien registra es un admin que ya inició sesión (panel de control)
    if 'user_id' in session and session.get('role') == 'admin':
        return redirect(url_for('listar_usuarios'))
    
    # Si es un usuario normal registrándose desde fuera
    return redirect(url_for('login'))

@app.route('/usuarios/eliminar/<int:id>')
def eliminar_usuario(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    return redirect(url_for('listar_usuarios'))

# app.py (Agrega esto después de la ruta de eliminar_usuario)

@app.route('/usuarios/editar/<int:id>')
def editar_usuario(id):
    """Muestra el formulario con los datos del usuario a editar"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM usuarios WHERE id = %s", (id,))
    usuario = cur.fetchone()
    cur.close()
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/actualizar', methods=['POST'])
def actualizar_usuario():
    """Guarda los cambios del usuario en la BD"""
    id_usuario = request.form['id']
    username = request.form['username']
    role = request.form['role']
    password = request.form['password'] # Puede venir vacía si no la quieren cambiar

    conn = get_db()
    cur = conn.cursor()

    if password:
        # Si escribieron una nueva contraseña, la ciframos y actualizamos todo
        password_hash = generate_password_hash(password)
        cur.execute(
            "UPDATE usuarios SET username = %s, role = %s, password = %s WHERE id = %s",
            (username, role, password_hash, id_usuario)
        )
    else:
        # Si la contraseña está vacía, solo actualizamos nombre y rol
        cur.execute(
            "UPDATE usuarios SET username = %s, role = %s WHERE id = %s",
            (username, role, id_usuario)
        )
    
    conn.commit()
    cur.close()
    return redirect(url_for('listar_usuarios'))


@app.route('/productos/editar/<int:id>')
def editar_producto(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cur.fetchone()
    cur.close()
    return render_template('editar_producto.html', producto=producto)

@app.route('/productos/actualizar', methods=['POST'])
def actualizar_producto():
    id_prod = request.form['id']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE productos SET nombre = %s, descripcion = %s, precio = %s WHERE id = %s",
        (nombre, descripcion, precio, id_prod)
    )
    conn.commit()
    cur.close()
    return redirect(url_for('listar_productos'))

# app.py

@app.route('/api/check_producto/<nombre>')
def check_producto(nombre):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM productos WHERE nombre = %s", (nombre,))
    count = cur.fetchone()[0]
    cur.close()
    # Devuelve {'existe': true} si ya hay uno, sino false
    return jsonify({'existe': count > 0})

# app.py

@app.route('/api/check_usuario/<username>')
def check_usuario(username):
    conn = get_db()
    cur = conn.cursor()
    # Buscamos si existe alguien con ese username exacto
    cur.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
    count = cur.fetchone()[0]
    cur.close()
    
    # Retorna { "existe": true } si ya hay alguien, o false si está libre
    return jsonify({'existe': count > 0})

# app.py

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        usuario = cur.fetchone() # usuario es un diccionario o tupla
        cur.close()

        if usuario:
            # Verificamos la contraseña cifrada
            # Asegúrate de tener: from werkzeug.security import check_password_hash
            if check_password_hash(usuario['password'], password):
                # ¡LOGIN EXITOSO! Guardamos datos en la sesión del navegador
                session['user_id'] = usuario['id']
                session['username'] = usuario['username']
                session['role'] = usuario['role']
                return redirect(url_for('index'))
            else:
                return "Contraseña incorrecta"
        else:
            return "Usuario no encontrado"
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Borra la sesión del navegador
    return redirect(url_for('login'))

# --- ARRANQUE DE LA APLICACIÓN ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')