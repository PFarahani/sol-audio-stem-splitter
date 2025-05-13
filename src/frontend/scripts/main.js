// SPDX-FileCopyrightText: 2025 Peyman Farahani (@PFarahani)
// SPDX-License-Identifier: Apache-2.0

(function () {
    // [Important] Access parent window's document (outside the iframe)
    const parentDocument = window.parent.document;

    function moveButton() {
        const shutdownBtn = parentDocument.querySelector('.st-key-shutdown_button');
        const deployBtnContainer = parentDocument.querySelector('.stAppDeployButton');

        if (shutdownBtn && deployBtnContainer) {
            // 1. Move the button after the Deploy button
            deployBtnContainer.parentNode.insertBefore(
                shutdownBtn,
                deployBtnContainer.nextSibling
            );

            // 2. Remove the original Deploy button container
            deployBtnContainer.remove();

        } else {
            // Retry every 100ms until elements are found
            setTimeout(moveButton, 100);
        }
    }
    moveButton(); // Start the process
})();



(function () {
    // [Important] Access parent window's document (outside the iframe)
    const parentDoc = window.parent.document;

    // 1. Core scrolling function
    function scrollDialogToTop() {
        const dialog = parentDoc.querySelector('div[role="dialog"]');
        if (!dialog) return;

        dialog.scrollTop = 0;

        const innerContent = dialog.querySelector('[data-testid="stMarkdownContainer"]');
        if (innerContent) {
            innerContent.scrollTop = 0;
            new ResizeObserver(() => innerContent.scrollTop = 0).observe(innerContent);
        }
    }

    // 2. Initialize observer in PARENT window
    function initObserver() {
        const observer = new MutationObserver(() => {
            if (parentDoc.querySelector('div[role="dialog"]')) {
                scrollDialogToTop();
            }
        });

        observer.observe(parentDoc.body, {
            childList: true,
            subtree: true
        });

        // Initial check
        scrollDialogToTop();
    }

    // 3. Start when parent DOM is ready
    if (parentDoc.readyState === 'complete') {
        initObserver();
    } else {
        window.parent.addEventListener('load', initObserver);
    }
})();



(function () {
    // [Important] Access parent window's document (outside the iframe)
    const parentDoc = window.parent.document;

    function removeStreamlitCredit() {
        const dialog = parentDoc.querySelector('div[role="dialog"]');
        if (!dialog) return;

        // Find all paragraphs in the dialog content
        const paragraphs = dialog.querySelectorAll('[data-testid="stMarkdownContainer"] p');

        if (paragraphs.length > 0) {
            const lastParagraph = paragraphs[paragraphs.length - 1];

            // Check if it's the Streamlit credit paragraph
            if (lastParagraph.textContent.includes('Made with Streamlit')) {
                lastParagraph.remove();
                console.log('Removed Streamlit credit paragraph');

                // Optional: Also remove the empty parent container if needed
                const container = lastParagraph.closest('[data-testid="stMarkdownContainer"]');
                if (container && container.children.length === 0) {
                    container.remove();
                }
            }
        }
    }

    // Run immediately and set up observer for dynamic content
    function init() {
        removeStreamlitCredit();

        const observer = new MutationObserver(() => {
            removeStreamlitCredit();
        });

        observer.observe(parentDoc.body, {
            childList: true,
            subtree: true
        });
    }

    // Start when parent document is ready
    if (parentDoc.readyState === 'complete') {
        init();
    } else {
        window.parent.addEventListener('load', init);
    }
})();



(function () {
    const parentWindow = window.parent;
    const currentPort = parseInt(parentWindow.location.port);
    const shutdownPort = currentPort + 1;
    
    function terminateApp() {
        const shutdownUrl = `http://${parentWindow.location.hostname}:${shutdownPort}/shutdown`;
        navigator.sendBeacon(shutdownUrl);
    }

    parentWindow.addEventListener('beforeunload', terminateApp);
})();