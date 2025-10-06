FROM node:20.19.5-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server (accessible from host)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
