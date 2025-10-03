import psycopg2

# ¡Usa las mismas credenciales que en tus otros archivos!
db_config = {
    "host": "localhost",
    "database": "mi_base",
    "user": "postgres",
    "password": "0503"
}

try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Crear la tabla 'personas'
    cur.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id SERIAL PRIMARY KEY,
            nombre_completo VARCHAR(100) NOT NULL,
            cargo VARCHAR(50)
        );
    """)

    # Insertar datos de ejemplo (solo si la tabla está vacía)
    cur.execute("SELECT id FROM personas LIMIT 1;")
    if cur.fetchone() is None:
        nombres_de_ejemplo = [
            ('Ana García', 'Desarrolladora Principal'),
            ('Carlos Rodríguez', 'Diseñador UX/UI'),
            ('Laura Martínez', 'Gerente de Proyectos'),
            ('Javier Hernández', 'Especialista en Marketing'),
            ('María López', 'Analista de Datos'),
            ('Pedro Sánchez', 'Administrador de Sistemas'),
            ('Sofía Ramírez', 'Ingeniera en Ciberseguridad'),
            ('Luis Torres', 'Arquitecto de Software'),
            ('Elena Fernández', 'Reclutadora de Talento'),
            ('Andrés Morales', 'Soporte Técnico')
        ]
        cur.executemany("INSERT INTO personas (nombre_completo, cargo) VALUES (%s, %s)", nombres_de_ejemplo)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ ¡Tabla 'personas' creada y poblada con 10 registros exitosamente!")

except psycopg2.Error as e:
    print(f"❌ Error al trabajar con la tabla 'personas': {e}")
