# para crear la imagen
```
docker build -t flask_app:1.1 . 
```


# para crear el contenedor
```
 docker run -d -p 5000:5000 --name mi-flask-web flask_app:1.1 
```