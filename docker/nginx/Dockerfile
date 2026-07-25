FROM nginx:1.25-alpine

COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/healthz || exit 1
