FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY frontend/ .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "start"]
