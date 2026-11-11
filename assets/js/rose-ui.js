/* ローゼンマイヤーの画面の動き: パララックス・カルーセル・スクロールで現れる表示・記事の読み進みバー。
   ライブラリは使わない。「視差効果を減らす」設定の人には動きを付けない。 */
(function () {
  "use strict";

  var reduceQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var prefersReduced = function () { return reduceQuery.matches; };

  /* ---------- スクロールで現れる表示 ---------- */
  function initReveal() {
    var items = document.querySelectorAll(".rz-reveal");
    if (!items.length) return;
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------- パララックス ---------- */
  function initParallax() {
    var layers = Array.prototype.slice.call(document.querySelectorAll("[data-rz-parallax]"));
    if (!layers.length) return;
    var ticking = false;

    function update() {
      ticking = false;
      if (prefersReduced()) {
        layers.forEach(function (el) { el.style.transform = ""; });
        return;
      }
      var vh = window.innerHeight;
      layers.forEach(function (el) {
        // ずらす前の位置で測るため、親の枠を基準にする
        var box = (el.parentElement || el).getBoundingClientRect();
        if (box.bottom < -200 || box.top > vh + 200) return;
        var shift;
        if (el.hasAttribute("data-rz-parallax-center")) {
          // 枠より大きい画像を枠の中で動かす。枠が画面の中央でずれ0、画面の端で余白ぶんまで。
          // 余白を超えると画像の端が見えるので、画面の高さによらず余白の中に収める
          var room = Math.max(0, (el.offsetHeight - box.height) / 2);
          var progress = ((box.top + box.height / 2) - vh / 2) / ((vh + box.height) / 2);
          shift = -Math.max(-1, Math.min(1, progress)) * room;
        } else {
          // ページ先頭でずれ0。数字が大きいほど速く流れる
          shift = window.scrollY * (parseFloat(el.getAttribute("data-rz-parallax")) || 0);
        }
        el.style.transform = "translate3d(0," + shift.toFixed(1) + "px,0)";
      });
    }

    function request() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request);
    if (reduceQuery.addEventListener) reduceQuery.addEventListener("change", request);
    update();
  }

  /* ---------- カルーセル（横スクロール＋スナップを土台に、ボタン・点・自動送りを足す） ---------- */
  function initCarousel(root) {
    var track = root.querySelector("[data-rz-track]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-rz-slide]"));
    if (!track || slides.length < 2) {
      // 1枚しか無いときは送る先が無いので、ボタンごと隠す
      var ui = root.querySelector(".rz-carousel__ui");
      if (ui) ui.hidden = true;
      return;
    }

    var prev = root.querySelector("[data-rz-prev]");
    var next = root.querySelector("[data-rz-next]");
    var dotsBox = root.querySelector("[data-rz-dots]");
    var toggle = root.querySelector("[data-rz-toggle]");
    var interval = parseInt(root.getAttribute("data-rz-autoplay"), 10) || 0;
    var dots = [];
    var current = 0;
    var timer = null;
    var stoppedByUser = false;
    var hovering = false;
    var focused = false;
    var onScreen = true;

    function behavior() { return prefersReduced() ? "auto" : "smooth"; }

    function centerOffset(slide) {
      return slide.offsetLeft - (track.clientWidth - slide.offsetWidth) / 2;
    }

    function maxScroll() { return track.scrollWidth - track.clientWidth; }

    var lastLeft = 0;
    var lastGoAt = 0;

    // そのスライドを中央に寄せたときのスクロール位置。端のスライドは寄せきれないので端で止める
    function targetLeft(slide) {
      return Math.max(0, Math.min(centerOffset(slide), maxScroll()));
    }

    function goTo(index) {
      var count = slides.length;
      var target = ((index % count) + count) % count;
      lastLeft = targetLeft(slides[target]);
      lastGoAt = Date.now();
      track.scrollTo({ left: lastLeft, behavior: behavior() });
    }

    /* 前後に1つ進む。小さいスライドが何枚も並ぶと、隣を中央に寄せても位置が変わらないことがあるので、
       「いまより実際に動く最初のスライド」を行き先にする。端まで来たら反対の端へ戻る。
       なめらかに動いている途中で続けて押されたときは、途中の位置ではなく行き先から数える */
    function step(dir) {
      var from = Date.now() - lastGoAt < 1000 ? lastLeft : track.scrollLeft;
      var i;
      if (dir > 0) {
        for (i = 0; i < slides.length; i++) {
          if (targetLeft(slides[i]) > from + 2) return goTo(i);
        }
        return goTo(0);
      }
      for (i = slides.length - 1; i >= 0; i--) {
        if (targetLeft(slides[i]) < from - 2) return goTo(i);
      }
      return goTo(slides.length - 1);
    }

    function nearest() {
      var mid = track.scrollLeft + track.clientWidth / 2;
      var best = 0;
      var bestDist = Infinity;
      slides.forEach(function (slide, i) {
        var dist = Math.abs(slide.offsetLeft + slide.offsetWidth / 2 - mid);
        if (dist < bestDist) { bestDist = dist; best = i; }
      });
      // 端まで来たら、中央に寄せきれない端のスライドを現在位置として扱う
      if (track.scrollLeft <= 2) best = 0;
      else if (track.scrollLeft >= maxScroll() - 2) best = slides.length - 1;
      return best;
    }

    function sync() {
      current = nearest();
      dots.forEach(function (dot, i) {
        if (i === current) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
      slides.forEach(function (slide, i) { slide.classList.toggle("is-current", i === current); });
    }

    if (dotsBox) {
      slides.forEach(function (_, i) {
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "rz-carousel__dot";
        dot.setAttribute("aria-label", (i + 1) + "枚目へ");
        dot.addEventListener("click", function () { goTo(i); });
        dotsBox.appendChild(dot);
        dots.push(dot);
      });
    }

    if (prev) prev.addEventListener("click", function () { step(-1); });
    if (next) next.addEventListener("click", function () { step(1); });

    track.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") { event.preventDefault(); step(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); step(1); }
    });

    var scrollTimer = null;
    track.addEventListener("scroll", function () {
      if (scrollTimer) return;
      scrollTimer = window.setTimeout(function () { scrollTimer = null; sync(); }, 80);
    }, { passive: true });
    window.addEventListener("resize", sync);

    /* 自動送り: 触っている間・画面外・タブが裏の間は止める。止めるボタンを押したら再開しない */
    function shouldRun() {
      return interval > 0 && !stoppedByUser && !hovering && !focused && onScreen &&
        !document.hidden && !prefersReduced();
    }

    function refresh() {
      if (timer) { window.clearInterval(timer); timer = null; }
      if (shouldRun()) timer = window.setInterval(function () { step(1); }, interval);
      if (toggle) {
        toggle.setAttribute("data-rz-state", stoppedByUser ? "stopped" : "playing");
        toggle.setAttribute("aria-label", stoppedByUser ? "自動送りを再開する" : "自動送りを止める");
      }
    }

    if (interval > 0) {
      if (toggle) {
        toggle.hidden = prefersReduced();
        toggle.addEventListener("click", function () { stoppedByUser = !stoppedByUser; refresh(); });
      }
      /* タッチ端末はタップのあとに合成の mouseenter だけが届き、外をタップするまで mouseleave が来ない。
         それで止めると再開ボタンを押しても動かないので、マウスのときだけ数える */
      var isMouse = function (event) { return !event.pointerType || event.pointerType === "mouse"; };
      var enterName = "PointerEvent" in window ? "pointerenter" : "mouseenter";
      var leaveName = "PointerEvent" in window ? "pointerleave" : "mouseleave";
      root.addEventListener(enterName, function (event) { if (isMouse(event)) { hovering = true; refresh(); } });
      root.addEventListener(leaveName, function (event) { if (isMouse(event)) { hovering = false; refresh(); } });
      /* キーボードで中を操作している間だけ止める。マウスで押したボタンにもフォーカスは残るが、
         それで止めると、カーソルを外しても止まったままになる（:focus-visible はキーボード操作のときだけ当たる）。
         別の窓に切り替えただけのときはフォーカスが中に残るので、focusout では実際の位置を見直す */
      var checkFocus = function () {
        var active = document.activeElement;
        var visible = false;
        try { visible = !!active && active.matches(":focus-visible"); } catch (e) { visible = true; }
        focused = !!active && root.contains(active) && visible;
        refresh();
      };
      root.addEventListener("focusin", checkFocus);
      // マウスで当てたフォーカスのままキーを押し始めた場合もここで拾う
      root.addEventListener("keyup", checkFocus);
      root.addEventListener("focusout", function () { window.setTimeout(checkFocus, 0); });
      // 指で触ったら（スワイプでも前後ボタン・点でも）止めて、ボタンの表示も「停止中」にそろえる。再開は停止ボタンから
      root.addEventListener("touchstart", function (event) {
        if (toggle && toggle.contains(event.target)) return;
        stoppedByUser = true;
        refresh();
      }, { passive: true });
      document.addEventListener("visibilitychange", refresh);
      if (reduceQuery.addEventListener) {
        reduceQuery.addEventListener("change", function () {
          if (toggle) toggle.hidden = prefersReduced();
          refresh();
        });
      }
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          onScreen = entries[0].isIntersecting;
          refresh();
        }, { threshold: 0.4 }).observe(root);
      }
    }

    root.classList.add("is-ready");
    sync();
    refresh();
  }

  /* ---------- 記事の読み進みバー ---------- */
  function initProgress() {
    var content = document.querySelector("#single_header ~ section .article-content");
    if (!content) return;
    var bar = document.createElement("div");
    bar.className = "rz-progress";
    bar.setAttribute("aria-hidden", "true");
    var fill = document.createElement("span");
    bar.appendChild(fill);
    document.body.appendChild(bar);
    var ticking = false;

    function update() {
      ticking = false;
      var box = content.getBoundingClientRect();
      var total = box.height - window.innerHeight;
      // 本文が1画面に収まる短いページでは進み具合を出しようがないので隠す
      bar.hidden = total <= 0;
      var ratio = total > 0 ? Math.max(0, Math.min(1, -box.top / total)) : 0;
      fill.style.transform = "scaleX(" + ratio.toFixed(4) + ")";
    }

    function request() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request);
    update();
  }

  function init() {
    window.__rzReady = true;
    initReveal();
    initParallax();
    document.querySelectorAll("[data-rz-carousel]").forEach(initCarousel);
    initProgress();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
