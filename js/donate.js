// PayPal link and QR image. Replace these two values when they are ready.
// DONATE_QR_SRC: "assets/donate-qr.png" or a full https URL. Leave "" to hide the QR.
var DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=KAPWYJ6Y4DD6A";
var DONATE_QR_SRC = "";

(function () {
  var button = document.getElementById("donate-paypal");
  var qr = document.getElementById("donate-qr");
  var frame = document.getElementById("donate-qr-frame");
  var url = typeof DONATE_URL === "string" ? DONATE_URL.trim() : "";
  var live = /^https?:\/\//i.test(url);

  if (button) {
    if (live) {
      button.href = url;
      button.target = "_blank";
      button.rel = "noopener noreferrer";
      button.removeAttribute("aria-disabled");
    } else {
      button.setAttribute("aria-disabled", "true");
      button.addEventListener("click", function (event) {
        event.preventDefault();
      });
    }
  }

  var src = typeof DONATE_QR_SRC === "string" ? DONATE_QR_SRC.trim() : "";
  if (!qr || !frame || !src || src === "#") return;

  var resolved = src;
  if (!/^(?:https?:)?\/\//i.test(src) && src.charAt(0) !== "/" && src.charAt(0) !== ".") {
    resolved = "../" + src;
  }

  var img = document.createElement("img");
  img.alt = "QR code for the Strings PayPal donation page";
  img.width = 240;
  img.height = 240;
  img.decoding = "async";
  img.addEventListener("error", function () {
    qr.hidden = true;
    frame.replaceChildren();
  });
  img.src = resolved;
  frame.replaceChildren(img);
  qr.hidden = false;
})();
