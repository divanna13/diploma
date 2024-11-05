FROM nginx:latest
COPY index.html /usr/share/nginx/html/
COPY 1.jpg /usr/share/nginx/html/
RUN apt-get update && apt-get install -y nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
