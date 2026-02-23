# Use a Node.js image as the base for building
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Vue.js application for production
RUN npm run build

# No need for a second stage with Nginx here,
# as the built assets will be copied to the main Nginx container
# via docker-compose.
# This Dockerfile is primarily for building the frontend assets.
