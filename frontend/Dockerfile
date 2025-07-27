# --- Stage 1: Build React App ---
FROM node:20-slim AS builder
WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

RUN npm run build

# --- Stage 2: Serve with NGINX ---
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80
