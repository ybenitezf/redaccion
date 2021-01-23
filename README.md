# Sistema de redacción interna para adelante.cu

## Setup

```bash
docker-compose build
docker-compose up
```

Esperar a que la BD sea inicializada y correr las migraciones con:

```bash
docker-compose run app flask db upgrade
```

Inicializar el indice para las búsquedas:

```bash
docker-compose run app flask index create
```

Crear un usuario administrador

```bash
docker-compose run app flask security createuser --name Administrador --email admin@example.com admin PASSWORD
docker-compose run app flask security createrol admin
docker-compose run app flask security asignrol admin admin
```

Con el usuario admin ir a la interfaz administrativa y crear al menos un volumen con el camino relativo a la carpeta `uploads`, de crearse a mano la carpeta del volumen:

http://app.local:8080/admin/


