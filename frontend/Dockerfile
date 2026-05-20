FROM nginx:alpine

# Copy the frontend file
COPY index.html /usr/share/nginx/html/index.html.template

# Default backend URL (can be overridden at runtime)
ENV BACKEND_URL=http://localhost:8080

# Use a custom entrypoint to inject the environment variable into the HTML
# We use a template file and envsubst to replace ${BACKEND_URL}
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"]

EXPOSE 80
