# para crear la imagen
docker build -t python-web:1.0 .

# para crear el contenedor
docker run  -d --rm -p 5000:5000 --name python-web-c python-web:1.0