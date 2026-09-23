/**
 * Direct browser-to-S3 multipart upload for admin video fields.
 * See users/direct_upload.py for the server side.
 */
(function () {
  'use strict';

  if (window.__directVideoUploadLoaded) return;
  window.__directVideoUploadLoaded = true;

  var CONCURRENCY = 4;
  var MAX_RETRIES = 5;
  var activeUploads = 0;

  function csrfToken(input) {
    var form = input.form;
    var el = form && form.querySelector('input[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function postJSON(url, body, csrf) {
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify(body)
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (!r.ok) throw new Error(data.error || ('Server error ' + r.status));
        return data;
      });
    });
  }

  function putPart(url, blob, onProgress) {
    return new Promise(function (resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open('PUT', url);
      xhr.upload.onprogress = function (e) { onProgress(e.loaded); };
      xhr.onload = function () {
        var etag = xhr.getResponseHeader('ETag');
        if (xhr.status >= 200 && xhr.status < 300 && etag) resolve(etag);
        else if (xhr.status >= 200 && xhr.status < 300) reject(new Error('S3 did not expose the ETag header (check bucket CORS ExposeHeaders).'));
        else reject(new Error('S3 responded ' + xhr.status));
      };
      xhr.onerror = function () { reject(new Error('Network/CORS error while uploading to S3')); };
      xhr.send(blob);
    });
  }

  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function formatMB(bytes) { return (bytes / 1048576).toFixed(1) + ' MB'; }

  function setStatus(el, html, color) {
    el.innerHTML = html;
    el.style.color = color || '#374151';
  }

  function uploadFile(input) {
    var wrapper = input.closest('[data-direct-upload-wrapper]');
    if (!wrapper) return;
    var tokenInput = wrapper.querySelector('[data-direct-upload-token]');
    var status = wrapper.querySelector('[data-direct-upload-status]');
    var file = input.files && input.files[0];
    tokenInput.value = '';
    if (!file) { setStatus(status, ''); return; }

    var csrf = csrfToken(input);
    var uploadToken = null;
    var loaded = [];
    var started = Date.now();
    activeUploads++;

    function render() {
      var done = loaded.reduce(function (a, b) { return a + b; }, 0);
      var secs = Math.max((Date.now() - started) / 1000, 0.5);
      var speed = done / secs;
      var eta = speed > 0 ? Math.round((file.size - done) / speed) : 0;
      var pct = Math.min(100, Math.floor(done * 100 / file.size));
      setStatus(status,
        '<div style="height:6px;background:#e5e7eb;border-radius:9999px;overflow:hidden;max-width:420px;">' +
        '<div style="height:100%;width:' + pct + '%;background:#2563eb;transition:width .2s;"></div></div>' +
        '<div style="margin-top:4px;">Uploading directly to storage: ' + pct + '% (' + formatMB(done) + ' / ' +
        formatMB(file.size) + ') &middot; ' + formatMB(speed) + '/s &middot; ~' + eta + 's left. ' +
        '<strong>Please wait before clicking Save.</strong></div>');
    }

    setStatus(status, 'Preparing upload…');

    postJSON(input.dataset.initiateUrl, {
      field: input.dataset.directUpload,
      filename: file.name,
      size: file.size,
      content_type: file.type || 'video/mp4'
    }, csrf).then(function (init) {
      uploadToken = init.token;
      var partSize = init.part_size;
      var urls = init.urls;
      var etags = new Array(urls.length);
      var next = 0;
      loaded = urls.map(function () { return 0; });

      function uploadPart(index, attempt) {
        var start = index * partSize;
        var blob = file.slice(start, Math.min(start + partSize, file.size));
        return putPart(urls[index], blob, function (n) { loaded[index] = n; render(); })
          .then(function (etag) { etags[index] = etag; loaded[index] = blob.size; render(); })
          .catch(function (err) {
            loaded[index] = 0;
            if (attempt >= MAX_RETRIES) throw err;
            return wait(1000 * Math.pow(2, attempt)).then(function () { return uploadPart(index, attempt + 1); });
          });
      }

      function worker() {
        if (next >= urls.length) return Promise.resolve();
        var index = next++;
        return uploadPart(index, 0).then(worker);
      }

      var workers = [];
      for (var i = 0; i < Math.min(CONCURRENCY, urls.length); i++) workers.push(worker());
      return Promise.all(workers).then(function () {
        setStatus(status, 'Finalizing upload…');
        return postJSON(input.dataset.completeUrl, {
          token: uploadToken,
          parts: etags.map(function (etag, i) { return { PartNumber: i + 1, ETag: etag }; })
        }, csrf);
      });
    }).then(function (result) {
      tokenInput.value = result.value;
      input.value = '';  // the file is already in S3; don't send it again with the form
      var secs = Math.round((Date.now() - started) / 1000);
      setStatus(status, '&#10003; ' + file.name + ' uploaded (' + formatMB(file.size) + ' in ' + secs +
        's). Click <strong>Save</strong> to attach it. It will be optimized for mobile streaming automatically.', '#166534');
    }).catch(function (err) {
      if (uploadToken) postJSON(input.dataset.abortUrl, { token: uploadToken }, csrf).catch(function () {});
      setStatus(status, 'Direct upload failed (' + err.message + '). The file will be uploaded the normal (slower) way when you click Save.', '#b45309');
    }).then(function () {
      activeUploads--;
    });
  }

  document.addEventListener('change', function (e) {
    var input = e.target;
    if (input && input.matches && input.matches('input[type=file][data-direct-upload]')) uploadFile(input);
  });

  document.addEventListener('submit', function (e) {
    if (activeUploads > 0) {
      e.preventDefault();
      e.stopImmediatePropagation();
      window.alert('A video is still uploading. Please wait until it finishes, then click Save again.');
    }
  }, true);

  window.addEventListener('beforeunload', function (e) {
    if (activeUploads > 0) { e.preventDefault(); e.returnValue = ''; }
  });
})();
