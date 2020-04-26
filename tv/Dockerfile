FROM ruby:2.5

ENV NODE_RED http://test.local/
ENV PORT 3030
EXPOSE $PORT

RUN apt-get update && apt-get install -y nodejs
RUN gem install bundler smashing

WORKDIR /dashboard

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

ENTRYPOINT ["smashing"]
CMD ["start", "-p", "$PORT"]