/* toast.js — sistema de notificações flutuantes */
(function () {
  'use strict';

  var ROOT_ID = 'toast-root';
  var DURATION = 4000;

  function getRoot() {
    var el = document.getElementById(ROOT_ID);
    if (!el) {
      el = document.createElement('div');
      el.id = ROOT_ID;
      document.body.appendChild(el);
    }
    return el;
  }

  function show(msg, type) {
    var root = getRoot();
    var icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + (type || 'info');
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML =
      '<span style="font-size:1.1em">' + (icons[type] || icons.info) + '</span>' +
      '<span>' + String(msg) + '</span>';
    root.appendChild(toast);

    function remove() {
      toast.classList.add('removing');
      setTimeout(function () { if (toast.parentNode) { toast.parentNode.removeChild(toast); } }, 250);
    }
    var timer = setTimeout(remove, DURATION);
    toast.addEventListener('click', function () { clearTimeout(timer); remove(); });
  }

  window._toast = {
    show: show,
    success: function (msg) { show(msg, 'success'); },
    error:   function (msg) { show(msg, 'error'); },
    info:    function (msg) { show(msg, 'info'); },
    warning: function (msg) { show(msg, 'warning'); },
  };
}());
