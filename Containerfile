FROM node:lts-alpine3.22
ENV NODE_ENV=production
ENV BITWARDEN_CLI_VERSION=2025.5.0
ENV SEMVER_VERSION=7.7.2

RUN npm install -g @bitwarden/cli@$BITWARDEN_CLI_VERSION semver@$SEMVER_VERSION && \
    apk add --no-cache dumb-init && \
    addgroup -S app && adduser -S app -G app

USER app

EXPOSE 8087

COPY --chmod=755 entrypoint.sh ./

ENTRYPOINT ["/usr/bin/dumb-init", "--", "sh", "./entrypoint.sh"]

CMD ["bw", "serve", "--hostname", "0.0.0.0"]
