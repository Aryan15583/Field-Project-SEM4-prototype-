# ---- build ----
FROM node:22-alpine AS build
WORKDIR /web
ENV NEXT_TELEMETRY_DISABLED=1
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---- run: Next.js standalone server, non-root ----
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
COPY --from=build --chown=node:node /web/.next/standalone ./
COPY --from=build --chown=node:node /web/.next/static ./.next/static
COPY --from=build --chown=node:node /web/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
