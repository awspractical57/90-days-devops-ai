# Base image — official nginx
FROM nginx:alpine

# Add metadata
LABEL maintainer="awspractical57"
LABEL description="My DevOps journey webpage"
LABEL version="1.0"

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy our custom HTML
COPY index.html /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# nginx starts automatically — no CMD needed
# (inherited from base image)
