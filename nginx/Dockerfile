FROM nginx:1.17.4-alpine

# Change default config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d