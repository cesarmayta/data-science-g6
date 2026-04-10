# para ver versión de docker
docker version

# para descargar una imagen
docker pull nginx

# para ver mis imagenes
docker images

# para desplegar un contenedor
docker run -d -p 8080:80 --name mi-nginx nginx

# para desplegar un contenedor y poder detenerlo y eliminarlo al mismo tiempo
docker run -d --rm -p 8080:80 --name mi-nginx nginx

# para ver mis contenedores
docker ps

# para detener un contenedor
docker stop mi-nginx

# para eliminar un contenedor
docker rm mi-nginx 

# para interactuar con nuestro contenedor

## para ver los logs
docker logs mi-nginx

## para ejecutar un comando dentro del contenedor

docker exec mi-gninx ls

## para ingresar al terminal de mi contenedor
docker exec -it mi-gninx bash

# VOLUMENES
docker volume ls
docker volume create web
docker run -d --rm -p 8080:80 -v c:/html:/usr/share/nginx/html --name nginx-codigo nginx:alpine
