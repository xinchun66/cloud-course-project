# -- Stage 1: install dependencies --------------------------------
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
# Install dependencies into /build/packages without polluting runtime image
RUN pip install --no-cache-dir -r requirements.txt --target /build/packages

# -- Stage 2: runtime image ---------------------------------------
FROM python:3.11-slim
WORKDIR /app
# Copy only dependency packages and code
COPY --from=builder /build/packages /app/packages
COPY . .
ENV PYTHONPATH=/app/packages
EXPOSE 5000
CMD ["python", "app.py"]
