FROM node:25-slim

WORKDIR /app
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=$VITE_API_BASE
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
