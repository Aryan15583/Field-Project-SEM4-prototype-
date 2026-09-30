FROM node:22-alpine AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /web/dist /usr/share/nginx/html
# "deploy" is an extra build context (see docker-compose.yml) pointing at ../deploy
COPY --from=deploy nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=deploy proxy.conf security-headers.conf /etc/nginx/snippets/
EXPOSE 8080
