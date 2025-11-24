import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from dotenv import load_dotenv
import sshtunnel

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración desde variables de entorno
app.secret_key = os.getenv('SECRET_KEY')

# Validar que todas las variables requeridas estén presentes
required_env_vars = ['SSH_HOST', 'SSH_USERNAME', 'SSH_KEY_PATH', 'DB_NAME', 'DB_PASSWORD', 'SECRET_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise Exception(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")

# Configuración SSH y MySQL
SSH_CONFIG = {
    'ssh_host': os.getenv('SSH_HOST'),
    'ssh_port': int(os.getenv('SSH_PORT', '22')),
    'ssh_username': os.getenv('SSH_USERNAME'),
    'ssh_pkey': os.getenv('SSH_KEY_PATH'),
    'remote_bind_address': ('127.0.0.1', 3306)
}

DB_CONFIG = {
    'host': '127.0.0.1',
    'database': os.getenv('DB_NAME', 'FormularioContacto'),
    'user': 'root',
    'password': os.getenv('DB_PASSWORD', 'ManriqueRojas18@'),
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Establece conexión con la base de datos a través de SSH tunnel"""
    try:
        print("🔒 Conectando a través de SSH tunnel...")
        
        # Crear túnel SSH
        tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG['ssh_host'], SSH_CONFIG['ssh_port']),
            ssh_username=SSH_CONFIG['ssh_username'],
            ssh_private_key=SSH_CONFIG['ssh_pkey'],
            remote_bind_address=SSH_CONFIG['remote_bind_address'],
            local_bind_address=('127.0.0.1', 0)
        )
        
        tunnel.start()
        print(f"✅ Túnel SSH establecido en puerto local: {tunnel.local_bind_port}")
        
        # Conectar a MySQL a través del túnel
        connection = pymysql.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=DB_CONFIG['cursorclass']
        )
        
        connection.tunnel = tunnel
        print("✅ Conexión a MySQL establecida correctamente")
        return connection
        
    except Exception as e:
        print(f'❌ Error de conexión: {str(e)}')
        return None

def close_db_connection(connection):
    """Cierra la conexión y el túnel SSH"""
    if connection and connection.open:
        connection.close()
    if hasattr(connection, 'tunnel') and connection.tunnel:
        connection.tunnel.close()

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe"""
    print("🗄️ Inicializando base de datos...")
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        phone VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                connection.commit()
                print("✅ Tabla 'contacts' verificada/creada correctamente")
        except Exception as e:
            print(f"❌ Error inicializando BD: {e}")
        finally:
            close_db_connection(connection)
    else:
        print("❌ No se pudo conectar a la base de datos")

# ... (el resto de tus rutas se mantienen igual)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip() or None
    
    if not full_name or not email:
        flash('Nombre completo y correo electrónico son obligatorios', 'error')
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    if not connection:
        flash('Error de conexión a la base de datos', 'error')
        return redirect(url_for('index'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO contacts (full_name, email, phone) VALUES (%s, %s, %s)',
                (full_name, email, phone)
            )
            connection.commit()
            flash('✅ Contacto agregado exitosamente!', 'success')
    except Exception as e:
        if 'Duplicate entry' in str(e):
            flash('❌ Error: El correo electrónico ya existe', 'error')
        else:
            flash(f'❌ Error al agregar contacto: {str(e)}', 'error')
    finally:
        close_db_connection(connection)
    
    return redirect(url_for('index'))

@app.route('/contacts')
def contacts():
    connection = get_db_connection()
    if not connection:
        flash('Error de conexión a la base de datos', 'error')
        return render_template('contacts.html', contacts=[])
    
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, full_name, email, phone, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at
                FROM contacts 
                ORDER BY created_at DESC
            ''')
            contacts = cursor.fetchall()
    except Exception as e:
        flash(f'Error al cargar contactos: {str(e)}', 'error')
        contacts = []
    finally:
        close_db_connection(connection)
    
    return render_template('contacts.html', contacts=contacts)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)