FROM node:18-alpine3.17 AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine3.17 AS production

WORKDIR /app

COPY --from=build /app/build ./build

COPY --from=build /app/package.json .

RUN npm install --production

COPY ./static ./static

EXPOSE 3000
CMD ["node", "./build"]
