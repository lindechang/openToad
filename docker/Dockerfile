FROM node:22-alpine

WORKDIR /app

RUN npm install -g pnpm@10.23.0

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY tsconfig.json ./

COPY packages ./packages
COPY extensions ./extensions

RUN pnpm install --frozen-lockfile

COPY packages/core/src ./packages/core/src
COPY packages/database/src ./packages/database/src
COPY packages/monetization/src ./packages/monetization/src
COPY extensions/wechat/src ./extensions/wechat/src
COPY extensions/web-widget/src ./extensions/web-widget/src

RUN pnpm build

EXPOSE 18789

ENV NODE_ENV=production

CMD ["pnpm", "run", "gateway"]