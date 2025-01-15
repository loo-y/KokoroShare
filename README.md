# KokoroShare

### Docker Image Build
```bash
docker build -t kokoroshare .
```

### Docker Run
```bash
docker run -dp 7860:7860 --name kokoroTTS kokoroshare
```
or with gpu
```bash
docker run --gpus=all -dp 7860:7860 --name kokoroTTS kokoroshare
```

### Docker Exec
```bash
docker exec -it kokoroTTS /bin/bash
```

