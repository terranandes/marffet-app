# Use Bun (oven/bun) - significantly faster than Node.js
FROM oven/bun:1 AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json bun.lockb* package-lock.json* ./
# Bun supports package-lock.json natively
RUN bun install --frozen-lockfile || bun install

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Next.js telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Bun run build
RUN bun run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# Create non-root user
# Use built-in bun user
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set permissions
RUN mkdir .next
RUN chown bun:bun .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=bun:bun /app/.next/standalone ./
COPY --from=builder --chown=bun:bun /app/.next/static ./.next/static

USER bun

EXPOSE 3000

ENV PORT 3000

# Run with Bun
CMD ["bun", "server.js"]
