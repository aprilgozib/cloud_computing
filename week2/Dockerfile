FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

# 18.04는 EOL이라 기본 미러가 404 날 수 있어서 old-releases로 변경
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list \
 && sed -i 's|http://security.ubuntu.com/ubuntu/|http://old-releases.ubuntu.com/ubuntu/|g' /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y nginx \
 && rm -rf /var/lib/apt/lists/*

# 웹 파일/사이트 설정 복사
COPY index.html /usr/share/nginx/html/index.html
COPY default /etc/nginx/sites-available/default
# 필요시: ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 80
CMD ["nginx","-g","daemon off;"]
