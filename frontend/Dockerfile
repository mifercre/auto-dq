# Step 1: Build and compile the frontend
FROM tiangolo/node-frontend:10 as build-stage

WORKDIR /app
COPY package*.json /app/
RUN npm install
COPY ./ /app/
RUN npm run build

# Step 2: Copy compiled app to be served by nginx
FROM nginx:1.15

COPY --from=build-stage /app/build/ /usr/share/nginx/html
COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf
