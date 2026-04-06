# 🎵 TikTok Downloader

## Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/tiktok-downloader.git
cd tiktok-downloader
```

---

## 2. Elige una versión y ejecútala

### Versión Base
```bash
docker build -t tiktok-app:v1.0 .
docker run -d -p 5000:5000 --name tiktok-container tiktok-app:v1.0
```

### Versión Optimizada
```bash
docker build -f Dockerfile.optimizado -t tiktok-app:v1.1-optimizado .
docker run -d -p 5000:5000 --name tiktok-container tiktok-app:v1.1-optimizado
```

### Versión Multi-stage
```bash
docker build -f Dockerfile.multistage -t tiktok-app:v1.2-multistage .
docker run -d -p 5000:5000 --name tiktok-container tiktok-app:v1.2-multistage
```

---

## 3. Abre la app

```
http://localhost:5000
```
