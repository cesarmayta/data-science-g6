# housing-api-g6
api para modelo de machine learning housing price
## como desplegar el proyecto en local

### paso 1 - creamos el entorno virtual
```
python -m venv venv
```
### paso 2 - activamos el entorno virtual
```
source venv/Scripts/activate
```
### paso 3 - instalamos dependencias
```
pip install -r requirements.txt
```
### documentación del API

Base URL en local:

```text
http://127.0.0.1:5000
```

### 1. `GET /`
Endpoint de bienvenida para validar que la API está activa.

Respuesta exitosa:

```json
{
  "message": "Bienvenido a mi API",
  "title": "FLASK API VERSION 1.0"
}
```

### 2. `POST /housing_price`
Predice el precio de una vivienda a partir del número de habitaciones, sin guardar el resultado en la base de datos.

Body:

```json
{
  "rooms": 3
}
```

Respuesta exitosa:

```json
{
  "message": "precio predicho",
  "habitaciones": 3,
  "precio": 123456.78
}
```

### 3. `POST /housing`
Predice el precio usando el modelo de machine learning y guarda el registro en la base de datos.

Body:

```json
{
  "rooms": 4
}
```

Respuesta exitosa:

```json
{
  "id": 1,
  "rooms": 4,
  "price": 185000.25
}
```

### 4. `GET /housing`
Lista todos los registros almacenados en la tabla `housing`.

Respuesta exitosa:

```json
[
  {
    "id": 1,
    "rooms": 4,
    "price": 185000.25
  },
  {
    "id": 2,
    "rooms": 2,
    "price": 98000.0
  }
]
```

### 5. `GET /housing/<id>`
Obtiene un registro por su identificador.

Ejemplo:

```text
GET /housing/1
```

Respuesta exitosa:

```json
{
  "id": 1,
  "rooms": 4,
  "price": 185000.25
}
```

Si el registro no existe, la API responde con código `404`.

### 6. `PUT /housing/<id>`
Actualiza el número de habitaciones de un registro existente y recalcula el precio usando el modelo.

Body:

```json
{
  "rooms": 5
}
```

Respuesta exitosa:

```json
{
  "id": 1,
  "rooms": 5,
  "price": 210000.5
}
```

Respuesta cuando el registro no existe:

```json
{
  "message": "Registro no encontrado"
}
```

### 7. `DELETE /housing/<id>`
Elimina un registro de la base de datos por su identificador.

Ejemplo:

```text
DELETE /housing/1
```

Respuesta exitosa:

```json
{
  "message": "Registro eliminado correctamente"
}
```

Respuesta cuando el registro no existe:

```json
{
  "message": "Registro no encontrado"
}
```

### estructura del modelo `Housing`
Los registros almacenados en la base de datos tienen esta estructura:

```json
{
  "id": 1,
  "rooms": 4,
  "price": 185000.25
}
```

### notas importantes
- Los endpoints `POST /housing_price`, `POST /housing` y `PUT /housing/<id>` esperan un body JSON con la propiedad `rooms`.
- El campo `price` no se envía desde el cliente: la API lo calcula con el modelo de machine learning.
- La conexión a la base de datos se configura con la variable de entorno `DATABASE_URL`.
