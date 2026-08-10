document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // Core Application Architecture
    // ==========================================
    class AIWorkspace {
        constructor() {
            const contextMeta = document.getElementById('ai-context');
            this.articleTitle = contextMeta ? contextMeta.dataset.articleTitle : '';
            
            this.cards = new Map();
            this.toastEl = document.getElementById('ai-toast');
            
            // Defensive Guard for Bootstrap
            if (this.toastEl && typeof window.bootstrap !== 'undefined' && window.bootstrap.Toast) {
                this.toast = new window.bootstrap.Toast(this.toastEl, { delay: 3000 });
            }
            
            this.init();
        }

        init() {
            document.querySelectorAll('.ai-card').forEach(cardEl => {
                const card = new AIFeatureCard(cardEl, this);
                this.cards.set(card.featureKey, card);
            });
        }

        showToast(message, type = 'success') {
            if (!this.toast) {
                console.log(`[Toast]: ${message}`);
                return;
            }
            
            const body = this.toastEl.querySelector('#ai-toast-message');
            this.toastEl.classList.remove('bg-success', 'bg-danger');
            
            if (type === 'success') {
                this.toastEl.classList.add('bg-success');
                body.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${message}`;
            } else {
                this.toastEl.classList.add('bg-danger');
                body.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i> ${message}`;
            }
            
            this.toast.show();
        }
    }

    // ==========================================
    // Network Layer
    // ==========================================
    class AIService {

        static getCookie(name) {

            let cookieValue = null;

            if (document.cookie && document.cookie !== "") {

                const cookies = document.cookie.split(";");

                for (let cookie of cookies) {

                    cookie = cookie.trim();

                    if (cookie.startsWith(name + "=")) {

                        cookieValue = decodeURIComponent(
                            cookie.substring(name.length + 1)
                        );

                        break;
                    }
                }
            }

            return cookieValue;
        }

        static async fetchFeature(url, difficulty, query, signal) {

            const csrf = AIService.getCookie("csrftoken");

            const response = await fetch(url, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf,
                    "X-Requested-With": "XMLHttpRequest"
                },

                body: JSON.stringify({
                    difficulty: difficulty,
                    query: query
                }),

                signal: signal
            });



    if (!response.ok) {
        let errorMsg = `Server error (${response.status}).`;

        if (response.status === 404)
            errorMsg = "Feature route not found.";

        if (response.status === 403)
            errorMsg = "Permission denied.";

        if (response.status === 429)
            errorMsg = "Too many requests.";

        if (response.status === 500)
            errorMsg = "Internal server error.";

        if (response.status === 503)
            errorMsg = "Gemini service unavailable.";

        throw new Error(errorMsg);
    }

    return await response.json();
}
    }

    // ==========================================
    // Individual Card Controller
    // ==========================================
    class AIFeatureCard {
        constructor(cardElement, workspace) {
            this.workspace = workspace;
            this.card = cardElement;
            this.featureKey = cardElement.dataset.feature;
            this.endpointUrl = cardElement.dataset.aiUrl;
            
            this.abortController = null;
            this.hasGeneratedOnce = false;
            
            this.header = cardElement.querySelector('.ai-card-header');
            this.btnTrigger = cardElement.querySelector('.btn-trigger');
            this.difficultySelect = cardElement.querySelector('.ai-difficulty-select');
            
            this.ui = {
                loading: cardElement.querySelector('.state-loading'),
                loadingText: cardElement.querySelector('.state-loading .text-muted'),
                error: cardElement.querySelector('.state-error'),
                success: cardElement.querySelector('.state-success'),
                errorText: cardElement.querySelector('.error-text'),
                outputText: cardElement.querySelector('.ai-output-text'),
                genTime: cardElement.querySelector('.ai-time'),
                cachedBadge: cardElement.querySelector('.ai-cached-badge'),
                cachedDot: cardElement.querySelector('.ai-cached-dot'),
                tokenDot: cardElement.querySelector('.ai-token-dot'),
                tokens: cardElement.querySelector('.ai-tokens'),
                modelName: cardElement.querySelector('.ai-model-name'),
                chatInput: cardElement.querySelector('.chat-input'),
                chatButton: cardElement.querySelector('.chat-send-btn'),
                pdfButton: cardElement.querySelector('.btn-export-pdf'),
            };
            
            this.btnCopyText = cardElement.querySelector('.copy-text');
            this.btnCopyMd = cardElement.querySelector('.copy-md');
            this.btnCopy = cardElement.querySelector('.btn-copy');
            this.btnBookmark = cardElement.querySelector('.ai-bookmark-button');
            
            this.rawMarkdown = "";
            this.loaderInterval = null;
            this.loadingMessages = [
                "Analyzing article content...",
                "Extracting key concepts...",
                "Synthesizing response with Gemini 2.5 Flash...",
                "Formatting Markdown output..."
            ];

            this.bindEvents();
        }

        bindEvents() {
            this.header.addEventListener('click', () => this.toggleCollapse());

            if(this.btnTrigger){
                this.btnTrigger.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.generate();
                });

            }

            if (this.ui.chatButton) {

                this.ui.chatButton.addEventListener('click', (e) => {
                    
                    e.preventDefault();
                    e.stopPropagation();

                    this.generate();

                });

            }


            if (this.ui.chatInput) {

                this.ui.chatInput.addEventListener('keydown', (e) => {

                    if (e.key === 'Enter' && !e.shiftKey) {
                        

                        e.preventDefault();
                        e.stopPropagation();

                        if (this.ui.chatButton && !this.ui.chatButton.disabled) {
                            this.ui.chatButton.click();
                        }

                    }

                });

            }
            
            if (this.btnCopyText) {
                this.btnCopyText.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (!this.btnCopyText.classList.contains('disabled')) this.copyToClipboard('text');
                });
            }
            
            if (this.btnCopyMd) {
                this.btnCopyMd.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (!this.btnCopyMd.classList.contains('disabled')) this.copyToClipboard('markdown');
                });
            }

            if (this.btnBookmark) {
                this.btnBookmark.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    if (!this.btnBookmark.disabled) {
                        this.toggleBookmark();
                    }
                });
            }

            if (this.ui.pdfButton) {
                this.ui.pdfButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    if (!this.ui.pdfButton.disabled) {
                        this.exportPDF();
                    }
                });
            }

            this.card.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    if (!this.btnTrigger.disabled) this.generate();
                }
            });
        }


        toggleCollapse() {
            this.card.classList.toggle('is-expanded');
            if (this.card.classList.contains('is-expanded')) this.card.focus();
        }

        expand() {
            if (!this.card.classList.contains('is-expanded')) {
                this.card.classList.add('is-expanded');
            }
            this.card.focus();
            this.card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        startRotatingLoader() {
            let index = 0;
            if (this.ui.loadingText) this.ui.loadingText.textContent = this.loadingMessages[0];
            
            this.loaderInterval = setInterval(() => {
                index = (index + 1) % this.loadingMessages.length;
                if (this.ui.loadingText) this.ui.loadingText.textContent = this.loadingMessages[index];
            }, 1500);
        }

        stopRotatingLoader() {
            if (this.loaderInterval) {
                clearInterval(this.loaderInterval);
                this.loaderInterval = null;
            }
        }

        setLoadingState() {
            this.expand();
            this.startRotatingLoader();
            this.btnTrigger.disabled = true;
            this.btnTrigger.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Generating...`;
            
            if (this.hasGeneratedOnce) {
                this.ui.outputText.style.opacity = '0.4';
                this.ui.error.classList.add('d-none');
            } else {
                this.ui.loading.classList.remove('d-none');
                this.ui.error.classList.add('d-none');
                this.ui.success.classList.add('d-none');
            }
        }

        setSuccessState(htmlContent, serverTime, isCached, rawMarkdown, tokens, modelName) {
            this.stopRotatingLoader();
            this.hasGeneratedOnce = true;
            this.btnTrigger.disabled = true;
            
            this.btnTrigger.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> Generated';
            this.btnTrigger.classList.add('btn-success-state');
            
            this.ui.loading.classList.add('d-none');
            this.ui.error.classList.add('d-none');
            this.ui.success.classList.remove('d-none');
            
            this.ui.outputText.style.opacity = '1';
            this.ui.outputText.innerHTML = htmlContent;
            this.rawMarkdown = rawMarkdown || "";
            
            this.ui.genTime.textContent = `${serverTime}s`;
            if (this.ui.modelName && modelName) this.ui.modelName.textContent = modelName;
            
            if (isCached) {
                this.ui.cachedBadge.classList.remove('d-none');
                this.ui.cachedDot.classList.remove('d-none');
            } else {
                this.ui.cachedBadge.classList.add('d-none');
                this.ui.cachedDot.classList.add('d-none');
            }

            if (tokens > 0) {
                this.ui.tokenDot.classList.remove('d-none');
                this.ui.tokens.classList.remove('d-none');
                this.ui.tokens.textContent = `${tokens} tokens`;
            }

            this.btnCopy.disabled = false;
            this.btnCopyText.classList.remove('disabled');
            this.btnCopyMd.classList.remove('disabled');

            if (this.btnBookmark) {
                this.btnBookmark.disabled = false;
            }

            if (this.ui.pdfButton) {
                this.ui.pdfButton.disabled = false;
            }

            setTimeout(() => {
                this.btnTrigger.classList.remove('btn-success-state');
                this.btnTrigger.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Regenerate';
                this.btnTrigger.disabled = false;
            }, 1500);
        }

        async exportPDF() {

            if (!this.rawMarkdown) {
                this.workspace.showToast(
                    "There is no AI result to export.",
                    "warning"
                );
                return;
            }

            if (!this.ui.pdfButton) {
                return;
            }

            const button = this.ui.pdfButton;

            const originalHTML = button.innerHTML;

            button.disabled = true;

            button.innerHTML =
                '<i class="bi bi-hourglass-split"></i>';

            try {

                const response = await fetch(
                    button.dataset.pdfUrl,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json",
                            // "X-CSRFToken": this.getCookie("csrftoken"),
                            "X-CSRFToken": AIService.getCookie("csrftoken"),
                            "X-Requested-With": "XMLHttpRequest"
                        },

                        body: JSON.stringify({
                            title: this.card.dataset.title || document.title,
                            feature: this.featureKey,
                            content: this.rawMarkdown
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        `PDF export failed (${response.status}).`
                    );
                }

                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);

                const link = document.createElement("a");

                link.href = url;

                link.download = "KnowledgeHub-AI-Result.pdf";

                document.body.appendChild(link);

                link.click();

                link.remove();

                window.URL.revokeObjectURL(url);

                this.workspace.showToast(
                    "PDF exported successfully.",
                    "success"
                );

            } catch (error) {

                console.error(
                    "PDF export error:",
                    error
                );

                this.workspace.showToast(
                    "Unable to export PDF.",
                    "danger"
                );

            } finally {

                button.innerHTML = originalHTML;
                button.disabled = false;
            }
        }

        setErrorState(errorMessage) {
            this.stopRotatingLoader();
            this.btnTrigger.disabled = false;
            this.btnTrigger.innerHTML = 'Retry';
            this.btnTrigger.classList.remove('btn-success-state');
            
            this.ui.outputText.style.opacity = '1';
            this.ui.loading.classList.add('d-none');
            this.ui.success.classList.add('d-none');
            this.ui.error.classList.remove('d-none');
            this.ui.errorText.textContent = errorMessage;
        }

        async generate() {
            if (this.abortController) {
                this.abortController.abort();
            }
            this.abortController = new AbortController();

            let query = "";

            if (this.featureKey === "chat") {

                const input = this.card.querySelector(".chat-input");

                query = input ? input.value.trim() : "";

                if (!query) {

                    this.workspace.showToast(
                        "Please enter a question.",
                        "warning"
                    );

                    return;
                }
            }

            this.setLoadingState();

            try {
                // const difficulty = this.difficultySelect ? this.difficultySelect.value : 'standard';
                // const urlObj = new URL(this.endpointUrl, window.location.origin);
                // urlObj.searchParams.append('difficulty', difficulty);
                // const data = await AIService.fetchFeature(urlObj.toString(), this.abortController.signal);

                // const difficulty = this.difficultySelect? this.difficultySelect.value: "standard";
                // const query = "";
                // const data = await AIService.fetchFeature(
                //     this.endpointUrl,
                //     difficulty,
                //     query,
                //     this.abortController.signal
                // );


                const difficulty = this.difficultySelect
                    ? this.difficultySelect.value
                    : "standard";

                let query = "";
                
                console.log("Feature:", this.featureKey);
                


                if (this.featureKey === "chat") {

                    const input = this.card.querySelector(".chat-input");
                    console.log("Textarea element:", input);

                    query = input ? input.value.trim() : "";
                    console.log("Question:", query);

                    if (!query) {
                        this.workspace.showToast(
                            "Please enter a question.",
                            "warning"
                        );
                        return;
                    }
                }

                console.log("Sending to Django:", {
                    difficulty,
                    query
                });


                const data = await AIService.fetchFeature(
                    this.endpointUrl,
                    difficulty,
                    query,
                    this.abortController.signal
                );

                if (data.success) {
                    const serverTime = data.time ? data.time : "0.0";
                    const isCached = data.cached ? data.cached : false;
                    const rawMarkdown = data.raw_markdown ? data.raw_markdown : "";
                    const tokens = data.tokens ? data.tokens : 0;
                    const modelName = data.model ? data.model : "Gemini 2.5 Flash";
                    
                    this.setSuccessState(data.html, serverTime, isCached, rawMarkdown, tokens, modelName);
                } else {
                    this.setErrorState(data.message || 'Failed to generate response.');
                }

            } catch (error) {
                if (error.name === 'AbortError') return; 
                console.error(`AI Error (${this.featureKey}):`, error);
                this.setErrorState(error.message || 'Network connection failed.');
            }
        }


        async toggleBookmark() {

            if (!this.rawMarkdown) {
                this.workspace.showToast(
                    "Generate an AI response before bookmarking it.",
                    "warning"
                );
                return;
            }

            if (!this.btnBookmark) return;

            const csrf = AIService.getCookie("csrftoken");

            const bookmarkUrl =
                `${this.endpointUrl}bookmark/`;

            const question =
                this.featureKey === "chat" && this.ui.chatInput
                    ? this.ui.chatInput.value.trim()
                    : "";

            this.btnBookmark.disabled = true;

            try {

                const response = await fetch(bookmarkUrl, {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrf,
                        "X-Requested-With": "XMLHttpRequest"
                    },

                    body: JSON.stringify({
                        prompt: question,
                        response: this.rawMarkdown
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(
                        data.message || "Unable to update bookmark."
                    );
                }

                const icon = this.btnBookmark.querySelector("i");

                if (data.bookmarked) {

                    this.btnBookmark.classList.add("bookmarked");

                    if (icon) {
                        icon.classList.remove("bi-bookmark");
                        icon.classList.add("bi-bookmark-fill");
                    }

                    this.btnBookmark.title = "Remove from Favorites";

                    this.workspace.showToast(
                        "AI response saved to favorites.",
                        "success"
                    );

                } else {

                    this.btnBookmark.classList.remove("bookmarked");

                    if (icon) {
                        icon.classList.remove("bi-bookmark-fill");
                        icon.classList.add("bi-bookmark");
                    }

                    this.btnBookmark.title = "Save to Favorites";

                    this.workspace.showToast(
                        "AI response removed from favorites.",
                        "success"
                    );
                }

            } catch (error) {

                console.error("Bookmark error:", error);

                this.workspace.showToast(
                    error.message || "Failed to update bookmark.",
                    "error"
                );

            } finally {

                this.btnBookmark.disabled = false;
            }
        }

        async copyToClipboard(format = 'text') {
            let textToCopy = (format === 'markdown' && this.rawMarkdown) 
                ? this.rawMarkdown 
                : (this.ui.outputText.innerText || this.ui.outputText.textContent);

            try {
                await navigator.clipboard.writeText(textToCopy);
                this.workspace.showToast(`Copied ${format === 'markdown' ? 'Markdown' : 'text'} to clipboard`, 'success');
            } catch (err) {
                console.error('Copy failed: ', err);
                this.workspace.showToast('Failed to copy text', 'error');
            }
        }
    }

    window.AppWorkspace = new AIWorkspace();
});



