# Imagem do backend FastAPI do e_seller.
# Usa uv para instalação rápida e determinística.
FROM python:3.14-slim

# uv — gerenciador de dependências rápido (Rust); instalado como binário Python-agnostic.
RUN pip install --no-cache-dir uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copia apenas os arquivos de dependências para aproveitar o cache de camadas.
COPY requirements.txt ./
# --system: instala no Python do sistema (não em venv); --no-cache: reduz tamanho da imagem.
RUN uv pip install --system --no-cache -r requirements.txt

COPY app ./app
COPY seeds ./seeds
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

RUN mkdir -p /app/data /app/storage/ebooks

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
