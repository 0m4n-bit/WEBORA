/* WEBORA – site behaviour (no dependencies) */
(function () {
  'use strict';

  var WHATSAPP_NUMBER = '96897464626';

  // Mobile menu
  var header = document.querySelector('.site-header');
  var burger = document.querySelector('.burger');
  if (header && burger) {
    burger.addEventListener('click', function () {
      var open = header.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) {
        header.classList.remove('is-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.focus();
      }
    });
  }

  // Contact form -> WhatsApp with a prefilled message
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var nameField = form.querySelector('[name="name"]');
      var wrap = nameField.closest('.field');
      var name = nameField.value.trim();
      if (!name) {
        wrap.classList.add('has-error');
        nameField.setAttribute('aria-invalid', 'true');
        nameField.focus();
        return;
      }
      wrap.classList.remove('has-error');
      nameField.removeAttribute('aria-invalid');

      var d = form.dataset;
      var biz = form.querySelector('[name="business"]').value;
      var msg = form.querySelector('[name="message"]').value.trim() || '-';
      var text = d.intro + '\n' + d.lName + ': ' + name + '\n' + d.lBiz + ': ' + biz + '\n' + d.lMsg + ': ' + msg;
      var url = 'https://wa.me/' + WHATSAPP_NUMBER + '?text=' + encodeURIComponent(text);
      var win = window.open(url, '_blank', 'noopener');
      if (!win) window.location.href = url;
    });
  }
})();
