# cloudContacts

# Configuración del Proyecto

## Variables de Entorno Requeridas

Crear archivo `.env` con:



# SSH Tunnel Configuration
SSH_HOST=44.207.64.115
SSH_PORT=22
SSH_USERNAME=ubuntu
SSH_KEY_PATH=C:/Users/Personal/Documents/aws/00.pem

# MySQL Database Configuration
DB_NAME=FormularioContacto
DB_PASSWORD="ManriqueRojas18@"

# Flask Configuration
SECRET_KEY=tu-clave-super-secreta-aqui-muy-larga-y-segura-2024

# ========================================
# FIN DE CONFIGURACIÓN SENSIBLE
# ========================================

# Diagrama de Arquitectura

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cliente Web   │    │     EC2-WEB      │    │     EC2-DB      │
│                 │    │                  │    │                 │
│  Navegador      │────│  Aplicación      │────│   Base de       │
│                 │    │     Flask        │    │   Datos MySQL   │
│  HTTP/HTTPS     │    │  Puerto 5000     │    │   Puerto 3306   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              └───── SSH Tunnel ────────┘
                                  Puerto 22 (SSH)

# Descripción Técnica
EC2-WEB (Instancia Web):

Sistema Operativo: Ubuntu 22.04 LTS

# Servicios:

Aplicación Flask (Puerto 5000)

Cliente SSH para túnel (Puerto 22)

Función: Servir la aplicación web y gestionar conexiones a la base de datos

EC2-DB (Instancia Base de Datos):

Sistema Operativo: Ubuntu 22.04 LTS

Servicios:

MySQL Server (Puerto 3306)

SSH Server (Puerto 22)

Función: Almacenar y gestionar datos de la aplicación

Conexión Segura:

SSH Tunnel: Conexión encriptada entre EC2-WEB y EC2-DB

Autenticación: Claves SSH para máxima seguridad

Puertos: 22 para SSH, 3306 para MySQL (solo acceso interno)



# Configuración de Grupos de Seguridad AWS
Grupo de Seguridad para EC2-WEB (Web Server)
Nombre: sg-web-server

Paso a paso desde AWS Console:
Acceder a AWS Console

Navegar a EC2 → Security Groups → Create Security Group

Configuración Básica

text
Security group name: sg-web-server
Description: Security group for Flask web application
VPC: Select your default VPC
Reglas de Entrada (Inbound Rules)

Tipo	Protocolo	Puerto	Origen	Descripción
SSH	TCP	22	My IP	SSH desde tu IP actual
Custom TCP	TCP	5000	0.0.0.0/0	Aplicación Flask
HTTP	TCP	80	0.0.0.0/0	Acceso web HTTP
SSH	TCP	22	sg-db-server	Conexión a base de datos
Reglas de Salida (Outbound Rules)

Mantener defaults (All traffic)

Grupo de Seguridad para EC2-DB (Database Server)
Nombre: sg-db-server

Paso a paso desde AWS Console:
Crear Nuevo Security Group

EC2 → Security Groups → Create Security Group

Configuración Básica

text
Security group name: sg-db-server
Description: Security group for MySQL database server
VPC: Same VPC as web server
Reglas de Entrada (Inbound Rules)

Tipo	Protocolo	Puerto	Origen	Descripción
SSH	TCP	22	sg-web-server	SSH desde web server
MYSQL/Aurora	TCP	3306	sg-web-server	MySQL desde web server
SSH	TCP	22	My IP	SSH para administración
Reglas de Salida (Outbound Rules)

Mantener defaults


# nstalación y Configuración de MySQL en EC2-DB
Paso 1: Conectar a EC2-DB
bash
# Conectar via SSH
ssh -i "your-key.pem" ubuntu@EC2-DB-PUBLIC-IP

# Actualizar sistema
sudo apt update && sudo apt upgrade -y
Paso 2: Instalar MySQL Server
bash
# Instalar MySQL Server
sudo apt install mysql-server -y

# Verificar instalación
sudo systemctl status mysql
Paso 3: Configurar Seguridad de MySQL
bash
# Ejecutar script de seguridad
sudo mysql_secure_installation

# Seguir las prompts:
# 1. Enter para ninguna contraseña root (si es fresh install)
# 2. Y para configurar contraseña root
# 3. Y para remover usuarios anónimos
# 4. Y para deshabilitar login root remoto
# 5. Y para remover base de datos test
# 6. Y para recargar privilegios
Paso 4: Configurar MySQL para la Aplicación
bash
# Acceder a MySQL
sudo mysql -u root -p

-- Crear base de datos
CREATE DATABASE FormularioContacto;

-- Crear usuario específico para la aplicación
CREATE USER 'app_user'@'%' IDENTIFIED BY 'StrongPassword123!';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON FormularioContacto.* TO 'app_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar usuarios
SELECT user, host FROM mysql.user;

-- Salir
EXIT;
Paso 5: Configurar Acceso Remoto
bash

# Editar configuración de MySQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Cambiar la línea bind-address:
bind-address = 0.0.0.0

# Reiniciar MySQL
sudo systemctl restart mysql

# Verificar que escucha en todos los interfaces
sudo netstat -tulpn | grep 3306
Paso 6: Probar Conexión Remota
Desde EC2-WEB probar conexión:

bash
mysql -h EC2-DB-PRIVATE-IP -u app_user -p

# Despliegue en EC2-WEB
# Paso 1: Conectar a EC2-WEB
bash
ssh -i "your-key.pem" ubuntu@EC2-WEB-PUBLIC-IP

# Paso 2: Instalar Dependencias del Sistema
bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install python3 python3-pip python3-venv git -y

# Verificar instalación
python3 --version
pip3 --version

# Paso 3: Clonar Repositorio
bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

# Verificar estructura de archivos
ls -la


# Paso 4: Configurar Entorno Virtual
bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list

# Paso 5: Configurar Variables de Entorno
bash
# Crear archivo .env
nano .env

# Contenido del archivo .env:

env
# Configuración SSH para Tunnel
SSH_HOST=PRIVATE-IP-EC2-DB
SSH_PORT=22
SSH_USERNAME=ubuntu
SSH_KEY_PATH=/home/ubuntu/.ssh/your-key.pem

# Configuración MySQL
DB_NAME=FormularioContacto
DB_PASSWORD=StrongPassword123!

# Configuración Flask
SECRET_KEY=your-super-secret-key-2024-make-this-very-long-and-secure

# Opcional: Configuración de entorno
FLASK_ENV=production
DEBUG=False

# Paso 6: Configurar Clave SSH para Tunnel

# Crear directorio .ssh
mkdir -p ~/.ssh

# Copiar clave PEM (desde tu máquina local)
# En tu máquina local ejecutar:
# scp -i "your-key.pem" your-key.pem ubuntu@EC2-WEB-PUBLIC-IP:/home/ubuntu/.ssh/

# Dar permisos correctos
chmod 600 ~/.ssh/your-key.pem

# Probar conexión SSH a EC2-DB
ssh -i ~/.ssh/your-key.pem ubuntu@PRIVATE-IP-EC2-DB

# Paso 7: Ejecutar la Aplicación

# Asegurarse que el entorno virtual está activado
source venv/bin/activate

# Ejecutar aplicación
python app.py


Paso 8: Verificar Despliegue
bash
# Verificar que la aplicación está corriendo
curl http://localhost:5000

# Verificar conexión a base de datos
# La aplicación debería mostrar mensajes de conexión exitosa

# Probar desde navegador
# http://EC2-WEB-PUBLIC-IP:5000