const proxy = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(proxy('/infoReturn', {target: 'http://localhost:8000/'}));
};
