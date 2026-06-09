FROM nginx:1.25-alpine
# Copy custom nginx config over the default config
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy frontend static files to the Nginx default directory
COPY static/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
