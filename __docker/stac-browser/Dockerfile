FROM node:14

ENV NODE_VERSION stable
ENV NPM_SCRIPT start
# ENV NODE_OPTIONS=--openssl-legacy-provider

RUN git clone https://github.com/radiantearth/stac-browser.git && cd stac-browser && git checkout dev

WORKDIR /stac-browser

EXPOSE 1234

ENTRYPOINT ["npm", "start"]

# Install app dependencies
RUN npm install
