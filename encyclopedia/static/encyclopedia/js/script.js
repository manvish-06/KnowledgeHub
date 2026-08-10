/* ==========================================
   KnowledgeHub JavaScript v2.0
   Part 1 - Core & Utilities
========================================== */

"use strict";

/* ==========================================
   Application
========================================== */

class KnowledgeHub {
  constructor() {
    this.init();
  }

  init() {
    this.cacheDOM();

    this.initializeModules();

    console.log("KnowledgeHub Initialized");
  }

  cacheDOM() {
    this.body = document.body;

    this.navbar = document.querySelector(".navbar");

    this.scrollTopBtn = document.getElementById("scrollTopBtn");

    this.progressBar = document.getElementById("reading-progress");
  }

  initializeModules() {
    new NavbarManager();

    new ScrollManager();

    new AnimationManager();

    new ThemeManager();

    new KeyboardManager();

    new UtilityManager();

    new SearchManager();

    new FormManager();

    new AlertManager();

    new CopyManager();

    new ImageManager();

    new DashboardManager();

    new CardManager();

    new LiveSearchManager();

    new CommandPalette();

    new ErrorManager();
  }
}

/* ==========================================
   Navbar Manager
========================================== */

class NavbarManager {
  constructor() {
    this.navbar = document.querySelector(".navbar");

    if (!this.navbar) return;

    this.initialize();
  }

  initialize() {
    this.updateNavbar();

    window.addEventListener("scroll", () => this.updateNavbar());

    this.highlightActiveLink();
  }

  updateNavbar() {
    if (window.scrollY > 20) {
      this.navbar.classList.add("navbar-scrolled");
    } else {
      this.navbar.classList.remove("navbar-scrolled");
    }
  }

  highlightActiveLink() {
    const current = window.location.pathname.replace(/\/$/, "");

    document.querySelectorAll(".nav-link").forEach((link) => {
      const href = new URL(link.href).pathname.replace(/\/$/, "");

      if (href === current) {
        link.classList.add("active");
      }
    });
  }
}

/* ==========================================
   Scroll Manager
========================================== */

class ScrollManager {
  constructor() {
    this.button = document.getElementById("scrollTopBtn");

    this.progress = document.getElementById("reading-progress");

    this.initialize();
  }

  initialize() {
    this.update();

    window.addEventListener(
      "scroll",

      () => this.update(),
    );

    if (this.button) {
      this.button.addEventListener(
        "click",

        () => {
          window.scrollTo({
            top: 0,

            behavior: "smooth",
          });
        },
      );
    }
  }

  update() {
    this.updateButton();

    this.updateProgress();
  }

  updateButton() {
    if (!this.button) return;

    if (window.scrollY > 500) {
      this.button.classList.add("show");
    } else {
      this.button.classList.remove("show");
    }
  }

  updateProgress() {
    if (!this.progress) return;

    const scrollTop = window.scrollY;

    const height =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;

    if (height <= 0) return;

    const percentage = (scrollTop / height) * 100;

    this.progress.style.width = percentage + "%";
  }
}

/* ==========================================
   Animation Manager
========================================== */

class AnimationManager {
  constructor() {
    this.initializeFade();

    this.initializeCounters();
  }

  initializeFade() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("show");
          }
        });
      },

      {
        threshold: 0.15,
      },
    );

    document
      .querySelectorAll(".fade-up,.card,.article-card,.stat-card")
      .forEach((element) => observer.observe(element));
  }

  initializeCounters() {
    const counters = document.querySelectorAll(".stat-card h2");

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          this.animateCounter(entry.target);

          observer.unobserve(entry.target);
        });
      },

      {
        threshold: 0.6,
      },
    );

    counters.forEach((counter) => observer.observe(counter));
  }

  animateCounter(counter) {
    const target = Number(counter.innerText.replace(/,/g, ""));

    if (Number.isNaN(target)) return;

    let current = 0;

    const increment = Math.ceil(target / 60);

    const timer = setInterval(() => {
      current += increment;

      if (current >= target) {
        counter.innerText = target.toLocaleString();

        clearInterval(timer);
      } else {
        counter.innerText = current.toLocaleString();
      }
    }, 20);
  }
}

/* ==========================================
   Theme Manager
========================================== */

class ThemeManager {
  constructor() {
    this.button = document.getElementById("themeToggle");

    if (!this.button) return;

    this.initialize();
  }

  initialize() {
    const theme = localStorage.getItem("theme");

    if (theme === "dark") {
      document.body.classList.add("dark-theme");
    }

    this.button.addEventListener(
      "click",

      () => this.toggle(),
    );
  }

  toggle() {
    document.body.classList.toggle("dark-theme");

    localStorage.setItem(
      "theme",

      document.body.classList.contains("dark-theme") ? "dark" : "light",
    );
  }
}

/* ==========================================
   Keyboard Manager
========================================== */

class KeyboardManager {
  constructor() {
    document.addEventListener(
      "keydown",

      (event) => this.shortcuts(event),
    );
  }

  shortcuts(event) {
    if (
      event.key === "/" &&
      !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)
    ) {
      event.preventDefault();

      const search = document.querySelector('input[name="q"]');

      if (search) {
        search.focus();
      }
    }
  }
}

/* ==========================================
   Utility Manager
========================================== */

class UtilityManager {
  constructor() {
    this.enableLazyImages();

    this.enableSmoothAnchors();

    this.enableTooltips();
  }

  enableLazyImages() {
    document
      .querySelectorAll("img")

      .forEach((img) => {
        img.loading = "lazy";
      });
  }

  enableSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener(
        "click",

        (event) => {
          const id = anchor.getAttribute("href");

          if (id === "#") return;

          const target = document.querySelector(id);

          if (!target) return;

          event.preventDefault();

          target.scrollIntoView({
            behavior: "smooth",
          });
        },
      );
    });
  }

  enableTooltips() {
    if (typeof bootstrap === "undefined") return;

    document
      .querySelectorAll('[data-bs-toggle="tooltip"]')
      .forEach((element) => new bootstrap.Tooltip(element));
  }
}

/* ==========================================
   Start Application
========================================== */

document.addEventListener(
  "DOMContentLoaded",

  () => {
    new KnowledgeHub();
  },
);

/* ==========================================
   Part 2
   Forms • Search • Notifications
========================================== */

/* ==========================================
   Search Manager
========================================== */

class SearchManager {
  constructor() {
    this.input = document.querySelector('input[name="q"]');

    if (!this.input) return;

    this.initialize();
  }

  initialize() {
    this.autoFocus();

    this.registerShortcuts();

    this.rememberSearch();
  }

  autoFocus() {
    if (window.location.pathname.includes("search")) {
      this.input.focus();
    }
  }

  registerShortcuts() {
    this.input.addEventListener(
      "keydown",

      (event) => {
        if (event.key === "Escape") {
          this.input.blur();
        }
      },
    );
  }

  rememberSearch() {
    this.input.form?.addEventListener(
      "submit",

      () => {
        localStorage.setItem(
          "lastSearch",

          this.input.value,
        );
      },
    );
  }
}

/* ==========================================
   Form Manager
========================================== */

class FormManager {
  constructor() {
    this.initialize();
  }

  initialize() {
    this.preventDoubleSubmit();

    this.autoResize();
  }

  preventDoubleSubmit() {
    document
      .querySelectorAll("form")

      .forEach((form) => {
        form.addEventListener(
          "submit",

          () => {
            const button = form.querySelector('button[type="submit"]');

            if (!button) return;

            button.disabled = true;

            const original = button.innerHTML;

            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>

                            Saving...`;

            setTimeout(() => {
              button.disabled = false;

              button.innerHTML = original;
            }, 3000);
          },
        );
      });
  }


  autoResize() {
    document.querySelectorAll("textarea").forEach((textarea) => {
      const resize = () => {
        textarea.style.height = "auto";

        textarea.style.height = textarea.scrollHeight + "px";
      };

      textarea.addEventListener(
        "input",

        resize,
      );

      resize();
    });
  }
}

/* ==========================================
   Alert Manager
========================================== */

class AlertManager {
  constructor() {
    this.initialize();
  }

  initialize() {
    document.querySelectorAll(".alert").forEach((alert) => {
      setTimeout(() => {
        alert.classList.remove("show");

        setTimeout(() => {
          alert.remove();
        }, 500);
      }, 5000);
    });
  }
}

/* ==========================================
   Copy Link Manager
========================================== */

class CopyManager {
  constructor() {
    this.initialize();
  }

  initialize() {
    document.querySelectorAll(".copy-link").forEach((button) => {
      button.addEventListener(
        "click",

        () => this.copy(button),
      );
    });
  }

  async copy(button) {
    try {
      await navigator.clipboard.writeText(window.location.href);

      const html = button.innerHTML;

      button.innerHTML = `<i class="bi bi-check-circle-fill"></i> Copied`;

      setTimeout(() => {
        button.innerHTML = html;
      }, 2000);
    } catch (error) {
      console.error(error);
    }
  }
}

/* ==========================================
   Image Manager
========================================== */

class ImageManager {
  constructor() {
    this.initialize();
  }

  initialize() {
    document
      .querySelectorAll("img")

      .forEach((img) => {
        if (img.complete) {
          img.classList.add("loaded");
        } else {
          img.addEventListener(
            "load",

            () => {
              img.classList.add("loaded");
            },
          );
        }
      });
  }
}

/* ==========================================
   Notification Manager
========================================== */

class NotificationManager {
  static success(message) {
    this.show(
      message,

      "success",
    );
  }

  static error(message) {
    this.show(
      message,

      "danger",
    );
  }

  static info(message) {
    this.show(
      message,

      "primary",
    );
  }

  static show(
    message,

    type,
  ) {
    const toast = document.createElement("div");

    toast.className = `alert alert-${type}

             position-fixed`;

    toast.style.top = "20px";

    toast.style.right = "20px";

    toast.style.zIndex = "9999";

    toast.innerHTML = message;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
}

/* ==========================================
   Part 3
   Dashboard • Search • Performance
==========================================*/

/* ==========================================
   Performance Utilities
========================================== */

class Performance {
  static debounce(callback, delay = 300) {
    let timeout;

    return (...args) => {
      clearTimeout(timeout);

      timeout = setTimeout(() => {
        callback(...args);
      }, delay);
    };
  }

  static throttle(callback, limit = 200) {
    let waiting = false;

    return (...args) => {
      if (waiting) return;

      callback(...args);

      waiting = true;

      setTimeout(() => {
        waiting = false;
      }, limit);
    };
  }
}

/* ==========================================
   Dashboard Manager
========================================== */

class DashboardManager {
  constructor() {
    this.cards = document.querySelectorAll(".stat-card");

    if (!this.cards.length) return;

    this.initialize();
  }

  initialize() {
    this.hoverEffects();

    this.animateCards();
  }

  hoverEffects() {
    this.cards.forEach((card) => {
      card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-8px) scale(1.02)";
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
      });
    });
  }

  animateCards() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("fade-up");
          }
        });
      },

      {
        threshold: 0.2,
      },
    );

    this.cards.forEach((card) => {
      observer.observe(card);
    });
  }
}

/* ==========================================
   Card Manager
========================================== */

class CardManager {

    constructor() {

        this.cards = document.querySelectorAll(".article-card");

        this.initialize();

    }

    initialize() {

        this.cards.forEach(card => {

            card.addEventListener("mouseenter", () => {

                card.style.transform =
                    "translateY(-10px) scale(1.02)";

            });

            card.addEventListener("mouseleave", () => {

                card.style.transform = "";

            });

        });

    }

}

/* ==========================================
   Live Search Manager
========================================== */

class LiveSearchManager {
  constructor() {
    this.input = document.querySelector('input[name="q"]');

    if (!this.input) return;

    this.initialize();
  }

  initialize() {
    this.input.addEventListener(
      "input",

      Performance.debounce(
        () => {
          this.search();
        },

        300,
      ),
    );
  }

  search() {
    const value = this.input.value.trim();

    if (value.length < 2) return;

    console.log(
      "Future AJAX Search:",

      value,
    );

    /*
            Future:

            fetch("/search-api/?q=" + value)

        */
  }
}

/* ==========================================
   Command Palette
========================================== */

class CommandPalette {
  constructor() {
    document.addEventListener(
      "keydown",

      (event) => {
        if (event.ctrlKey && event.key.toLowerCase() === "k") {
          event.preventDefault();

          this.open();
        }
      },
    );
  }

  open() {
    const search = document.querySelector('input[name="q"]');

    if (!search) return;

    search.focus();

    search.select();

    NotificationManager.info("Quick Search");
  }
}

/* ==========================================
   Loading Overlay
========================================== */

class LoadingOverlay {
  static show() {
    if (document.getElementById("loading-overlay")) return;

    const overlay = document.createElement("div");

    overlay.id = "loading-overlay";

    overlay.innerHTML = `

            <div class="spinner-border text-light">

            </div>

        `;

    overlay.style.position = "fixed";

    overlay.style.top = 0;

    overlay.style.left = 0;

    overlay.style.width = "100%";

    overlay.style.height = "100%";

    overlay.style.background = "rgba(0,0,0,.5)";

    overlay.style.display = "flex";

    overlay.style.alignItems = "center";

    overlay.style.justifyContent = "center";

    overlay.style.zIndex = "99999";

    document.body.appendChild(overlay);
  }

  static hide() {
    const overlay = document.getElementById("loading-overlay");

    if (overlay) overlay.remove();
  }
}

/* ==========================================
   Global Error Handler
========================================== */

class ErrorManager {
  constructor() {
    window.addEventListener(
      "error",

      (event) => {
        console.error(
          "KnowledgeHub:",

          event.message,
        );
      },
    );

    window.addEventListener(
      "unhandledrejection",

      (event) => {
        console.error(event.reason);
      },
    );
  }
}

/* ==========================================
   Part 4
   Future Features & Final Initialization
========================================== */

/* ==========================================
   Storage Manager
========================================== */

class StorageManager {
  static save(key, value) {
    localStorage.setItem(
      key,

      JSON.stringify(value),
    );
  }

  static load(key, fallback = null) {
    const data = localStorage.getItem(key);

    if (!data) return fallback;

    try {
      return JSON.parse(data);
    } catch {
      return fallback;
    }
  }
}

/* ==========================================
   Reading History
========================================== */

class ReadingHistory {
  constructor() {
    this.saveCurrentArticle();
  }

  saveCurrentArticle() {
    const article = document.querySelector("h1");

    if (!article) return;

    const history = StorageManager.load(
      "readingHistory",

      [],
    );

    const item = {
      title: article.innerText,

      url: window.location.pathname,

      date: new Date().toISOString(),
    };

    const filtered = history.filter((h) => h.url !== item.url);

    filtered.unshift(item);

    StorageManager.save(
      "readingHistory",

      filtered.slice(0, 20),
    );
  }
}

/* ==========================================
   Recent Searches
========================================== */

class RecentSearches {
  constructor() {
    this.form = document.querySelector('form[action*="search"]');

    if (!this.form) return;

    this.initialize();
  }

  initialize() {
    this.form.addEventListener(
      "submit",

      () => {
        const input = this.form.querySelector('input[name="q"]');

        if (!input) return;

        let searches = StorageManager.load(
          "recentSearches",

          [],
        );

        searches = searches.filter((item) => item !== input.value);

        searches.unshift(input.value);

        StorageManager.save(
          "recentSearches",

          searches.slice(0, 10),
        );
      },
    );
  }
}

/* ==========================================
   Like Manager
========================================== */

class LikeManager {
  constructor() {
    this.buttons = document.querySelectorAll(".like-button");

    this.initialize();
  }

  initialize() {
    this.buttons.forEach((button) => {
      button.addEventListener(
        "click",

        () => this.like(button),
      );
    });
  }

  async like(button) {
    /*
            Future Django Endpoint

            POST /api/like/

        */

    button.classList.toggle("liked");

    NotificationManager.success("Article liked!");
  }
}

/* ==========================================
   Bookmark Manager
========================================== */

class BookmarkManager {
  constructor() {
    this.buttons = document.querySelectorAll(".bookmark-button");

    this.initialize();
  }

  initialize() {
    this.buttons.forEach((button) => {
      button.addEventListener(
        "click",

        () => this.bookmark(button),
      );
    });
  }

  bookmark(button) {
    button.classList.toggle("bookmarked");

    NotificationManager.success("Bookmark saved.");
  }
}

/* ==========================================
   Wikipedia Integration
========================================== */

class WikipediaSearch {
  constructor() {
    this.input = document.querySelector('input[name="q"]');

    if (!this.input) return;
  }

  async search(query) {
    /*
            This is intentionally left as a stub.

            We'll connect it to your Django backend
            after we build the Wikipedia search
            feature.

            The backend will fetch results from
            Wikipedia and return JSON.
        */

    console.log(
      "Wikipedia Search:",

      query,
    );
  }
}

/* ==========================================
   Analytics
========================================== */

class Analytics {
  constructor() {
    this.pageView();
  }

  pageView() {
    console.log(
      "Visited:",

      window.location.pathname,
    );
  }
}

/* ==========================================
   App Extensions
========================================== */

KnowledgeHub.prototype.initializeModules = function () {
  new NavbarManager();

  new ScrollManager();

  new AnimationManager();

  new ThemeManager();

  new KeyboardManager();

  new UtilityManager();

  new SearchManager();

  new FormManager();

  new AlertManager();

  new CopyManager();

  new ImageManager();

  new DashboardManager();

  new CardManager();

  new LiveSearchManager();

  new CommandPalette();

  new ErrorManager();

  new ReadingHistory();

  new RecentSearches();

  new LikeManager();

  new BookmarkManager();

  new WikipediaSearch();

  new Analytics();
};


