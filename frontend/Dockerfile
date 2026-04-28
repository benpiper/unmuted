# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install dependencies natively
# Install dependencies natively
RUN npm install

# Copy application source code
COPY . .

# Generate static Vite production build
RUN npm run build

# Production serving stage
FROM nginx:alpine

# Copy built artifacts stringently to Nginx HTML root
COPY --from=build /app/dist /usr/share/nginx/html

# Install reverse proxy config (as template for envsubst)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Expose the standard Nginx container port
EXPOSE 80

# Command to gracefully run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
