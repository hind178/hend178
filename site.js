/* Small progressive enhancements. Everything works without this file:
   the menu stays visible, all projects are listed, the email is a normal link. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) { setOpen(false); toggle.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (nav.classList.contains("open") && !e.target.closest(".site-head")) setOpen(false);
    });
  }

  /* ---------- Project filter + "Explore more" ---------- */
  var works = document.getElementById("works");
  if (works) {
    var cards = Array.prototype.slice.call(works.querySelectorAll(".card"));
    var filterBtns = Array.prototype.slice.call(document.querySelectorAll(".filter"));
    var moreBtn = document.getElementById("more-btn");
    var status = document.getElementById("works-status");
    var INITIAL = 6;
    var current = "all";
    var expanded = false;

    // Counts on the filter buttons
    filterBtns.forEach(function (btn) {
      var f = btn.getAttribute("data-filter");
      var n = f === "all" ? cards.length : cards.filter(function (c) {
        return (" " + c.getAttribute("data-cat") + " ").indexOf(" " + f + " ") > -1;
      }).length;
      var span = btn.querySelector(".n");
      if (span) span.textContent = n;
    });

    var render = function (animate) {
      var shown = 0;
      var featuredIndex = 0;
      cards.forEach(function (card) {
        var match = current === "all" ||
          (" " + card.getAttribute("data-cat") + " ").indexOf(" " + current + " ") > -1;
        var visible = match && (current !== "all" || expanded || featuredIndex < INITIAL);
        if (current === "all") featuredIndex++;
        var wasHidden = card.hidden;
        card.hidden = !visible;
        if (visible) {
          shown++;
          if (animate && wasHidden && !reduce) {
            card.classList.remove("enter");
            void card.offsetWidth;
            card.classList.add("enter");
          }
        }
      });
      if (moreBtn) {
        var showMore = current === "all" && cards.length > INITIAL;
        moreBtn.parentNode.hidden = !showMore;
        moreBtn.setAttribute("aria-expanded", String(expanded));
        moreBtn.querySelector(".label").textContent =
          moreBtn.getAttribute(expanded ? "data-less" : "data-more");
      }
      if (status) {
        status.textContent = (status.getAttribute("data-template") || "{n}").replace("{n}", shown);
      }
    };

    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        current = btn.getAttribute("data-filter");
        filterBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        render(true);
      });
    });

    if (moreBtn) {
      moreBtn.addEventListener("click", function () {
        var firstNew = null;
        expanded = !expanded;
        if (expanded) firstNew = cards[INITIAL];
        render(true);
        if (expanded && firstNew) {
          var link = firstNew.querySelector("h3 a, h3 button");
          if (link) link.focus({ preventScroll: true });
          firstNew.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        } else if (!expanded) {
          works.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        }
      });
    }
    render(false);
  }

  /* ---------- Lightbox for pieces without a case-study page ---------- */
  var box = document.getElementById("lightbox");
  if (box && typeof box.showModal === "function") {
    var boxImg = box.querySelector("img");
    var boxTitle = box.querySelector("[data-lb-title]");
    var boxText = box.querySelector("[data-lb-text]");
    var lastTrigger = null;
    document.querySelectorAll("[data-lightbox]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var card = btn.closest(".card");
        var img = card.querySelector("img");
        boxImg.src = btn.getAttribute("data-lightbox");
        boxImg.alt = img ? img.alt : "";
        boxTitle.textContent = btn.textContent.trim();
        var desc = card.querySelector(".desc");
        boxText.textContent = desc ? desc.textContent.trim() : "";
        lastTrigger = btn;
        box.showModal();
      });
    });
    box.querySelector(".close").addEventListener("click", function () { box.close(); });
    box.addEventListener("click", function (e) { if (e.target === box) box.close(); });
    box.addEventListener("close", function () { if (lastTrigger) lastTrigger.focus(); });
  } else {
    // No <dialog> support: open the image itself
    document.querySelectorAll("[data-lightbox]").forEach(function (btn) {
      btn.addEventListener("click", function () { window.location.href = btn.getAttribute("data-lightbox"); });
    });
  }

  /* ---------- Copy email ---------- */
  var copyBtn = document.getElementById("copy-email");
  if (copyBtn) {
    var copyStatus = document.getElementById("copy-status");
    var email = copyBtn.getAttribute("data-email");
    var done = function (ok) {
      copyStatus.textContent = copyBtn.getAttribute(ok ? "data-ok" : "data-fail");
      clearTimeout(copyBtn._t);
      copyBtn._t = setTimeout(function () { copyStatus.textContent = ""; }, 4000);
    };
    copyBtn.addEventListener("click", function () {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(email).then(function () { done(true); }, function () { fallback(); });
      } else { fallback(); }
    });
    var fallback = function () {
      var t = document.createElement("textarea");
      t.value = email; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
      document.body.appendChild(t); t.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(t);
      done(ok);
    };
  }

  /* ---------- Gentle reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (!reduce && "IntersectionObserver" in window && revealEls.length) {
    doc.classList.add("reveal-on");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }
})();
