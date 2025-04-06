FROM alpine:3.21.3

RUN adduser -D nonrootuser

RUN apk add --no-cache libc6-compat 

USER nonrootuser

COPY stabilize /stabilize

ENTRYPOINT ["/stabilize"]
