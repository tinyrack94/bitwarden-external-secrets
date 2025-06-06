FROM node:24-alpine

RUN npm install -g @bitwarden/cli

EXPOSE 8087

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

CMD ["bw", "serve", "--hostname", "0.0.0.0"]