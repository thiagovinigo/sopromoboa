FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# NEXT_PUBLIC_* são embutidas no bundle em tempo de build.
ARG NEXT_PUBLIC_API_URL=https://api.quepromo.com.br
ARG NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-8215576310884543
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_ADSENSE_CLIENT_ID=$NEXT_PUBLIC_ADSENSE_CLIENT_ID
# A VPS divide ~2 GB com outros sites: o teto do heap evita que o build seja morto pelo kernel.
ENV NODE_OPTIONS="--max-old-space-size=420"
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
