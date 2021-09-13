FROM node

ENV NODE_VERSION stable
ENV NPM_SCRIPT start

RUN git clone https://github.com/radiantearth/stac-browser.git && cd stac-browser && git checkout v3

WORKDIR /stac-browser

EXPOSE 1234

ENTRYPOINT ["npm", "start"]


# Install app dependencies
RUN npm install
