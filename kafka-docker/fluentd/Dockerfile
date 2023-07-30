FROM fluent/fluentd:v1.13-1
USER root

# 필요한 라이브러리와 빌드 도구 설치
RUN apk add --no-cache --update \
    build-base \
    ruby-dev

# Kafka 플러그인 설치
RUN gem install fluent-plugin-kafka --no-document

USER root