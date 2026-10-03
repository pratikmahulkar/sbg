// Services dropdown: close on outside click, link click or Esc
document.addEventListener("click", function (x) {
  var d = document.querySelector(".dd");
  if (d.open && (!d.contains(x.target) || x.target.closest("a"))) d.open = false;
});
document.addEventListener("keydown", function (x) {
  if (x.key === "Escape") document.querySelector(".dd").open = false;
});

// Enquiry form: opens the visitor's email app with the message filled in
var form = document.getElementById("f");
form.addEventListener("submit", function (v) {
  v.preventDefault();
  var d = new FormData(form);
  location.href = "mailto:" + form.dataset.email +
    "?subject=" + encodeURIComponent("Enquiry from " + d.get("n")) +
    "&body=" + encodeURIComponent(d.get("m") + "\n\nPhone: " + d.get("p"));
});
