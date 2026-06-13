/* router.js — SPA hash-router melhorado */
(function () {
  'use strict';

  function Router() {
    this._routes = {};
    this._active = null;
    this._container = null;
    this._notFound = null;
    var self = this;
    window.addEventListener('hashchange', function () { self._dispatch(); });
  }

  Router.prototype.setContainer = function (el) {
    this._container = typeof el === 'string' ? document.getElementById(el) : el;
    return this;
  };

  Router.prototype.setNotFound = function (fn) {
    this._notFound = fn;
    return this;
  };

  Router.prototype.register = function (path, renderFn) {
    this._routes[path] = renderFn;
    return this;
  };

  Router.prototype.navigate = function (path) {
    window.location.hash = path;
  };

  Router.prototype.start = function () {
    this._dispatch();
  };

  Router.prototype._dispatch = function () {
    var hash = window.location.hash.replace(/^#\/?/, '') || '';
    var parts = hash.split('/');
    var base  = '/' + parts[0];
    var params = parts.slice(1);
    var renderFn = this._routes[base] || this._routes[hash ? '#/' + hash : '/'];
    if (!renderFn) {
      var keys = Object.keys(this._routes);
      for (var i = 0; i < keys.length; i++) {
        var pattern = keys[i].replace(/:[^/]+/g, '([^/]+)');
        var m = hash.match(new RegExp('^' + pattern.replace(/^\//, '') + '$'));
        if (m) { renderFn = this._routes[keys[i]]; params = m.slice(1); break; }
      }
    }
    if (!renderFn && this._notFound) { renderFn = this._notFound; }
    if (!renderFn) { return; }
    this._active = hash;
    if (this._container) { this._container.innerHTML = ''; }
    renderFn.apply(null, params);
  };

  window.Router = Router;
}());
