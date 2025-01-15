# 安裝必要的系統套件
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製 ecoweb 和 config 目錄
COPY ecoweb/ ecoweb/
COPY config/ config/
COPY .env .env

# 設定工作目錄到 ecoweb
WORKDIR /app/ecoweb

# 開放應用程式運行的端口
EXPOSE 55555

# 啟動 Django 應用程式在 port 55555
CMD ["python", "manage.py", "runserver", "0.0.0.0:55555"]

