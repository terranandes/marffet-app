FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.12-slim
LABEL "language"="python"
LABEL "framework"="fastapi"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
