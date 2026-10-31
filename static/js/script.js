/**
 * TreapMate AI - Modern Interactive Frontend Controller
 * Follows modern web standards & accessibility guidelines
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatForm = document.getElementById("chatForm");
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatViewport = document.getElementById("chatViewport");
    const messagesContainer = document.getElementById("messagesContainer");
    const welcomeHero = document.getElementById("welcomeHero");
    const thinkingContainer = document.getElementById("thinkingContainer");
    const thinkingTimer = document.getElementById("thinkingTimer");
    const historyList = document.getElementById("historyList");
    const newChatBtn = document.getElementById("newChatBtn");
    const clearHistoryBtn = document.getElementById("clearHistoryBtn");
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const closeSidebarBtn = document.getElementById("closeSidebarBtn");
    const sidebar = document.getElementById("sidebar");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");
    const currentTripTitle = document.getElementById("currentTripTitle");
    const printPlanBtn = document.getElementById("printPlanBtn");
    const chipBar = document.getElementById("chipBar");
    const userLocationText = document.getElementById("userLocationText");
    const sidebarLocationVal = document.getElementById("sidebarLocationVal");
    const editLocationBtn = document.getElementById("editLocationBtn");
    const locationBadge = document.getElementById("locationBadge");

    // State Variables
    let currentThreadId = generateThreadId();
    let isGenerating = false;
    let timerInterval = null;
    let timerSeconds = 0;
    let currentUserLocation = "Dhaka, Bangladesh";

    // Storage Keys
    const STORAGE_KEY_HISTORY = "treapmate_history_v1";
    const STORAGE_KEY_THEME = "color-scheme";
    const STORAGE_KEY_LOCATION = "treapmate_user_location";
    const STORAGE_KEY_SIDEBAR = "treapmate_sidebar_collapsed";

    // -------------------------------------------------------------
    // 1. Theme Management (Complying with modern-web-guidance)
    // -------------------------------------------------------------
    function initTheme() {
        const metaTheme = document.querySelector('meta[name="color-scheme"]');
        const storedTheme = localStorage.getItem(STORAGE_KEY_THEME);
        if (storedTheme && metaTheme) {
            metaTheme.content = storedTheme;
        }

        themeToggleBtn.addEventListener("click", () => {
            const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
            const currentRendered = metaTheme.content === "light dark" 
                ? (isDark ? "dark" : "light") 
                : metaTheme.content;
            
            const targetTheme = currentRendered === "dark" ? "light" : "dark";

            // If target matches OS default, revert to system preference
            if ((targetTheme === "dark" && isDark) || (targetTheme === "light" && !isDark)) {
                localStorage.removeItem(STORAGE_KEY_THEME);
                metaTheme.content = "light dark";
            } else {
                localStorage.setItem(STORAGE_KEY_THEME, targetTheme);
                metaTheme.content = targetTheme;
            }
        });

        // Listen for changes from other tabs
        window.addEventListener("storage", (e) => {
            if (e.key === STORAGE_KEY_THEME && metaTheme) {
                metaTheme.content = e.newValue ?? "light dark";
            }
        });
    }

    // -------------------------------------------------------------
    // 2. Automatic Location Identification & Preference
    // -------------------------------------------------------------
    function updateLocationUI(locationStr) {
        if (!locationStr) return;
        currentUserLocation = locationStr;
        localStorage.setItem(STORAGE_KEY_LOCATION, locationStr);
        if (userLocationText) userLocationText.textContent = locationStr;
        if (sidebarLocationVal) sidebarLocationVal.textContent = locationStr;
    }

    function getUserLocation() {
        return currentUserLocation || localStorage.getItem(STORAGE_KEY_LOCATION) || "Dhaka, Bangladesh";
    }

    async function detectUserLocation() {
        // 1. Check if user already set their location preference
        const savedLoc = localStorage.getItem(STORAGE_KEY_LOCATION);
        if (savedLoc) {
            updateLocationUI(savedLoc);
            return;
        }

        // 2. Try fast client-side IP-based geocoding
        try {
            const res = await fetch("https://ipapi.co/json/", { signal: AbortSignal.timeout(2500) });
            if (res.ok) {
                const data = await res.json();
                if (data.city && data.country_name) {
                    const detected = `${data.city}, ${data.country_name}`;
                    updateLocationUI(detected);
                    return;
                } else if (data.country_name) {
                    updateLocationUI(data.country_name);
                    return;
                }
            }
        } catch (e) {
            // Network or adblocker blocked external IP API, fallback to timezone heuristic
        }

        // 3. Timezone Heuristic (instant & offline)
        try {
            const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
            if (tz.includes("Dhaka")) {
                updateLocationUI("Dhaka, Bangladesh");
                return;
            } else if (tz.includes("Kolkata") || tz.includes("Calcutta") || tz.includes("Delhi")) {
                updateLocationUI("Delhi, India");
                return;
            } else if (tz.includes("Karachi")) {
                updateLocationUI("Karachi, Pakistan");
                return;
            } else if (tz.includes("London")) {
                updateLocationUI("London, United Kingdom");
                return;
            } else if (tz.includes("New_York")) {
                updateLocationUI("New York, United States");
                return;
            } else if (tz.includes("Dubai")) {
                updateLocationUI("Dubai, United Arab Emirates");
                return;
            } else if (tz.includes("Tokyo")) {
                updateLocationUI("Tokyo, Japan");
                return;
            }
        } catch (e) {}

        // 4. Default fallback
        updateLocationUI("Dhaka, Bangladesh");
    }

    function promptEditLocation() {
        const current = getUserLocation();
        const userInput = prompt("Enter your departure location or current city (e.g., 'India', 'Dhaka', 'London'):", current);
        if (userInput && userInput.trim()) {
            updateLocationUI(userInput.trim());
        }
    }

    function initLocation() {
        detectUserLocation();
        if (editLocationBtn) {
            editLocationBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                promptEditLocation();
            });
        }
        if (locationBadge) {
            locationBadge.addEventListener("click", promptEditLocation);
        }
    }

    // -------------------------------------------------------------
    // 2. Textarea Auto-sizing Fallback
    // -------------------------------------------------------------
    function initTextareaAutoResize() {
        if (!CSS.supports("field-sizing", "content")) {
            messageInput.addEventListener("input", () => {
                messageInput.style.height = "auto";
                messageInput.style.height = Math.min(messageInput.scrollHeight, 180) + "px";
            });
        }
    }

    // -------------------------------------------------------------
    // 3. Thread & History Storage Management
    // -------------------------------------------------------------
    function generateThreadId() {
        return "user_" + Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
    }

    function getSavedJourneys() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY_HISTORY) || "[]");
        } catch (e) {
            return [];
        }
    }

    function saveJourney(threadId, query, answerData) {
        let journeys = getSavedJourneys();
        const existingIdx = journeys.findIndex(j => j.threadId === threadId);

        const title = extractTripTitle(query);

        const journeyData = {
            threadId,
            title,
            firstQuery: query,
            timestamp: Date.now(),
            messages: existingIdx >= 0 ? journeys[existingIdx].messages : []
        };

        journeyData.messages.push({
            role: "user",
            content: query
        });

        journeyData.messages.push({
            role: "agent",
            content: answerData.answer,
            flight_results: answerData.flight_results,
            hotel_results: answerData.hotel_results,
            itinerary: answerData.itinerary,
            llm_calls: answerData.llm_calls
        });

        if (existingIdx >= 0) {
            journeys[existingIdx] = journeyData;
        } else {
            journeys.unshift(journeyData);
        }

        // Limit to 20 recent journeys
        journeys = journeys.slice(0, 20);
        localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(journeys));
        renderHistory();
    }

    function extractTripTitle(query) {
        const cleaned = query.replace(/(plan|a|trip|treap|to|from|for|flights|days|day|\d+)/gi, "").trim();
        if (cleaned.length > 2) {
            return cleaned.charAt(0).toUpperCase() + cleaned.slice(1) + " Trip";
        }
        return query.slice(0, 24) + "...";
    }

    function renderHistory() {
        const journeys = getSavedJourneys();
        historyList.innerHTML = "";

        if (journeys.length === 0) {
            historyList.innerHTML = `<div class="empty-history">No saved trips yet.<br>Start planning below!</div>`;
            return;
        }

        journeys.forEach(j => {
            const item = document.createElement("div");
            item.className = `history-item ${j.threadId === currentThreadId ? "active" : ""}`;
            item.innerHTML = `
                <div class="history-item-content">
                    <span class="history-item-icon">✈️</span>
                    <span class="history-item-text" title="${escapeHtml(j.firstQuery)}">${escapeHtml(j.title)}</span>
                </div>
                <button class="history-delete-btn" title="Delete" aria-label="Delete journey">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            `;

            // Load journey on click
            item.querySelector(".history-item-content").addEventListener("click", () => {
                loadJourney(j.threadId);
                closeSidebar(true);
            });

            // Delete journey on button click
            item.querySelector(".history-delete-btn").addEventListener("click", (e) => {
                e.stopPropagation();
                deleteJourney(j.threadId);
            });

            historyList.appendChild(item);
        });
    }

    function loadJourney(threadId) {
        const journeys = getSavedJourneys();
        const found = journeys.find(j => j.threadId === threadId);
        if (!found) return;

        currentThreadId = threadId;
        currentTripTitle.textContent = found.title;
        welcomeHero.style.display = "none";
        messagesContainer.innerHTML = "";

        found.messages.forEach(msg => {
            if (msg.role === "user") {
                appendUserMessage(msg.content);
            } else {
                appendAgentMessage(msg);
            }
        });

        renderHistory();
        scrollToBottom();
    }

    function deleteJourney(threadId) {
        let journeys = getSavedJourneys().filter(j => j.threadId !== threadId);
        localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(journeys));
        if (currentThreadId === threadId) {
            startNewJourney();
        } else {
            renderHistory();
        }
    }

    function startNewJourney() {
        currentThreadId = generateThreadId();
        messagesContainer.innerHTML = "";
        welcomeHero.style.display = "flex";
        currentTripTitle.textContent = "TreapMate AI";
        messageInput.value = "";
        renderHistory();
        closeSidebar(true);
    }

    // -------------------------------------------------------------
    // 4. Message Rendering & Multi-Tab Agent Card
    // -------------------------------------------------------------
    function appendUserMessage(text) {
        welcomeHero.style.display = "none";

        const row = document.createElement("div");
        row.className = "message-row user-row";
        row.innerHTML = `
            <div class="user-bubble">${escapeHtml(text)}</div>
        `;
        messagesContainer.appendChild(row);
        scrollToBottom();
    }

    function appendAgentMessage(data) {
        const row = document.createElement("div");
        row.className = "message-row agent-row";

        // Generate unique IDs for tabs in this card
        const cardId = "card_" + Math.random().toString(36).substring(2, 8);

        // Parse markdown content safely
        const renderedHtml = renderMarkdown(data.content || data.answer || "No response generated.");

        // Has extra flight/hotel details?
        const hasFlights = Boolean(data.flight_results && data.flight_results.trim());
        const hasHotels = Boolean(data.hotel_results && data.hotel_results.trim());

        row.innerHTML = `
            <div class="agent-avatar">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                </svg>
            </div>
            <div class="agent-card" id="${cardId}">
                <div class="agent-card-header">
                    <div class="pipeline-badge-list">
                        <span class="pipe-badge badge-green">✓ Flights Checked</span>
                        <span class="pipe-badge badge-green">✓ Stays Discovered</span>
                        <span class="pipe-badge badge-green">✓ Itinerary Planned</span>
                        <span class="pipe-badge">${data.llm_calls || 4} LLM Calls</span>
                    </div>

                    <div class="message-actions">
                        <button class="action-btn copy-btn" title="Copy Itinerary">
                            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                            <span>Copy</span>
                        </button>
                        <button class="action-btn print-card-btn" title="Print this Itinerary to PDF">
                            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 6 2 18 2 18 9"></polyline>
                                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                                <rect x="6" y="14" width="12" height="8"></rect>
                            </svg>
                            <span>Print PDF</span>
                        </button>
                    </div>
                </div>

                <!-- Tabs navigation if flights/hotels available -->
                <div class="agent-tabs">
                    <button class="agent-tab-btn active" data-tab="plan">📋 Comprehensive Plan</button>
                    ${hasFlights ? `<button class="agent-tab-btn" data-tab="flights">✈️ Live Flights</button>` : ""}
                    ${hasHotels ? `<button class="agent-tab-btn" data-tab="hotels">🏨 Hotel Intel</button>` : ""}
                </div>

                <!-- Tab 1: Comprehensive Itinerary Markdown -->
                <div class="tab-pane active" data-pane="plan">
                    <div class="markdown-body">${renderedHtml}</div>
                </div>

                <!-- Tab 2: Live Flight Data Breakdown -->
                ${hasFlights ? `
                <div class="tab-pane" data-pane="flights">
                    <div class="markdown-body">${renderMarkdown(data.flight_results)}</div>
                </div>` : ""}

                <!-- Tab 3: Hotel Search Intel -->
                ${hasHotels ? `
                <div class="tab-pane" data-pane="hotels">
                    <div class="markdown-body">${renderMarkdown(data.hotel_results)}</div>
                </div>` : ""}
            </div>
        `;

        // Wire Tab Clicking
        const cardElem = row.querySelector(".agent-card");
        const tabBtns = cardElem.querySelectorAll(".agent-tab-btn");
        const tabPanes = cardElem.querySelectorAll(".tab-pane");

        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");
                tabBtns.forEach(b => b.classList.remove("active"));
                tabPanes.forEach(p => p.classList.remove("active"));

                btn.classList.add("active");
                const activePane = cardElem.querySelector(`.tab-pane[data-pane="${targetTab}"]`);
                if (activePane) activePane.classList.add("active");
            });
        });

        // Wire Copy Button
        const copyBtn = cardElem.querySelector(".copy-btn");
        copyBtn.addEventListener("click", () => {
            const rawText = data.content || data.answer || "";
            navigator.clipboard.writeText(rawText).then(() => {
                copyBtn.innerHTML = `<span>✓ Copied!</span>`;
                setTimeout(() => {
                    copyBtn.innerHTML = `
                        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        <span>Copy</span>
                    `;
                }, 2000);
            });
        });

        // Wire Print PDF Button on Card
        const printCardBtn = cardElem.querySelector(".print-card-btn");
        if (printCardBtn) {
            printCardBtn.addEventListener("click", () => {
                printItineraryDocument(renderedHtml, currentTripTitle.textContent, getUserLocation());
            });
        }

        messagesContainer.appendChild(row);
        scrollToBottom();
    }

    // -------------------------------------------------------------
    // 5. Agent Thinking Simulation & Timer
    // -------------------------------------------------------------
    function startThinkingAnimation() {
        thinkingContainer.style.display = "flex";
        timerSeconds = 0;
        thinkingTimer.textContent = "0s";

        const stepFlight = document.getElementById("stepFlight");
        const stepHotel = document.getElementById("stepHotel");
        const stepItinerary = document.getElementById("stepItinerary");
        const stepFinal = document.getElementById("stepFinal");

        const steps = [stepFlight, stepHotel, stepItinerary, stepFinal];
        steps.forEach(s => {
            s.classList.remove("active", "done");
        });

        stepFlight.classList.add("active");

        timerInterval = setInterval(() => {
            timerSeconds++;
            thinkingTimer.textContent = `${timerSeconds}s`;

            if (timerSeconds === 2) {
                stepFlight.classList.remove("active");
                stepFlight.classList.add("done");
                stepHotel.classList.add("active");
            } else if (timerSeconds === 4) {
                stepHotel.classList.remove("active");
                stepHotel.classList.add("done");
                stepItinerary.classList.add("active");
            } else if (timerSeconds === 7) {
                stepItinerary.classList.remove("active");
                stepItinerary.classList.add("done");
                stepFinal.classList.add("active");
            }
        }, 1000);

        scrollToBottom();
    }

    function stopThinkingAnimation() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        thinkingContainer.style.display = "none";
    }

    // -------------------------------------------------------------
    // 6. Submit Travel Query API Call
    // -------------------------------------------------------------
    async function submitTravelQuery(queryText) {
        if (!queryText || isGenerating) return;

        isGenerating = true;
        sendBtn.disabled = true;
        messageInput.disabled = true;

        appendUserMessage(queryText);
        startThinkingAnimation();

        // Update top title if first message
        if (currentTripTitle.textContent === "TreapMate AI") {
            currentTripTitle.textContent = extractTripTitle(queryText);
        }

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: queryText,
                    thread_id: currentThreadId,
                    user_location: getUserLocation()
                })
            });

            if (!response.ok) {
                const errJson = await response.json().catch(() => ({}));
                throw new Error(errJson.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            stopThinkingAnimation();

            // Append agent response card
            appendAgentMessage(data);

            // Save to local journey history
            saveJourney(currentThreadId, queryText, data);

        } catch (error) {
            stopThinkingAnimation();
            appendAgentMessage({
                answer: `⚠️ **Travel Planning Error**\n\n${error.message}\n\nPlease check your internet connection and verify that your API credentials in \`.env\` are active.`,
                llm_calls: 0
            });
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
            messageInput.disabled = false;
            messageInput.value = "";
            messageInput.style.height = "auto";
            messageInput.focus();
        }
    }

    // -------------------------------------------------------------
    // 7. Event Listeners & Interactions
    // -------------------------------------------------------------
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = messageInput.value.trim();
        if (text) {
            submitTravelQuery(text);
        }
    });

    // Enter to submit, Shift+Enter for newline
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            const text = messageInput.value.trim();
            if (text) {
                submitTravelQuery(text);
            }
        }
    });

    // Prompt suggestion cards
    document.querySelectorAll(".prompt-card").forEach(card => {
        card.addEventListener("click", () => {
            const prompt = card.getAttribute("data-prompt");
            if (prompt) {
                submitTravelQuery(prompt);
            }
        });
    });

    // Chips bar append
    chipBar.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip");
        if (chip) {
            const appendText = chip.getAttribute("data-append") || "";
            messageInput.value = appendText;
            messageInput.focus();
        }
    });

    // -------------------------------------------------------------
    // Universal Sidebar Controller (Desktop Collapse & Mobile Drawer)
    // -------------------------------------------------------------
    function isMobile() {
        return window.innerWidth <= 768;
    }

    function isSidebarOpen() {
        if (!sidebar) return false;
        if (isMobile()) {
            return sidebar.classList.contains("open");
        } else {
            return !sidebar.classList.contains("collapsed");
        }
    }

    function updateSidebarAria() {
        const open = isSidebarOpen();
        if (mobileMenuBtn) {
            mobileMenuBtn.setAttribute("aria-expanded", open ? "true" : "false");
            mobileMenuBtn.setAttribute("title", open ? "Collapse Sidebar (Ctrl+B)" : "Expand Sidebar (Ctrl+B)");
        }
        if (closeSidebarBtn) {
            closeSidebarBtn.setAttribute("aria-expanded", open ? "true" : "false");
            closeSidebarBtn.setAttribute("title", isMobile() ? "Close Sidebar" : "Collapse Sidebar");
        }
    }

    function openSidebar() {
        if (!sidebar) return;
        if (isMobile()) {
            sidebar.classList.add("open");
            if (sidebarBackdrop) sidebarBackdrop.classList.add("active");
            document.body.style.overflow = "hidden";
        } else {
            sidebar.classList.remove("collapsed");
            localStorage.setItem(STORAGE_KEY_SIDEBAR, "false");
        }
        updateSidebarAria();
    }

    function closeSidebar(isMobileOnly = false) {
        if (!sidebar) return;
        if (isMobile()) {
            sidebar.classList.remove("open");
            if (sidebarBackdrop) sidebarBackdrop.classList.remove("active");
            document.body.style.overflow = "";
        } else if (!isMobileOnly) {
            sidebar.classList.add("collapsed");
            localStorage.setItem(STORAGE_KEY_SIDEBAR, "true");
        }
        updateSidebarAria();
    }

    function toggleSidebar() {
        if (isSidebarOpen()) {
            closeSidebar(false);
        } else {
            openSidebar();
        }
    }

    function initSidebar() {
        // Restore desktop preference on load
        if (!isMobile() && sidebar) {
            const isCollapsed = localStorage.getItem(STORAGE_KEY_SIDEBAR) === "true";
            if (isCollapsed) {
                sidebar.classList.add("collapsed");
            } else {
                sidebar.classList.remove("collapsed");
            }
        }
        updateSidebarAria();

        // 1. Hamburger Menu Button (Toggle Sidebar)
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                toggleSidebar();
            });
        }

        // 2. Close Sidebar Button (✕)
        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                closeSidebar(false);
            });
        }

        // 3. Mobile Backdrop click
        if (sidebarBackdrop) {
            sidebarBackdrop.addEventListener("click", () => {
                if (isMobile()) closeSidebar(true);
            });
        }

        // 4. Keyboard Shortcuts: Ctrl+B to toggle, Escape to close
        window.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
                e.preventDefault();
                toggleSidebar();
            } else if (e.key === "Escape") {
                if (isMobile() && sidebar && sidebar.classList.contains("open")) {
                    closeSidebar(true);
                }
            }
        });

        // 5. Window Resize Handler
        window.addEventListener("resize", () => {
            if (!isMobile()) {
                if (sidebar) sidebar.classList.remove("open");
                if (sidebarBackdrop) sidebarBackdrop.classList.remove("active");
                document.body.style.overflow = "";
                const isCollapsed = localStorage.getItem(STORAGE_KEY_SIDEBAR) === "true";
                if (sidebar) {
                    if (isCollapsed) {
                        sidebar.classList.add("collapsed");
                    } else {
                        sidebar.classList.remove("collapsed");
                    }
                }
            }
            updateSidebarAria();
        });
    }

    // New Journey Button
    newChatBtn.addEventListener("click", startNewJourney);

    // Clear History Button
    clearHistoryBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to clear all trip history?")) {
            localStorage.removeItem(STORAGE_KEY_HISTORY);
            startNewJourney();
        }
    });

    // Print / PDF Plan - Triggers high-fidelity printable view
    printPlanBtn.addEventListener("click", () => {
        const lastAgentCard = document.querySelector(".agent-card:last-of-type");
        if (!lastAgentCard) {
            alert("No travel plan to print yet! Please plan a journey first.");
            return;
        }
        const planPane = lastAgentCard.querySelector('.tab-pane[data-pane="plan"] .markdown-body');
        const contentHtml = planPane ? planPane.innerHTML : lastAgentCard.innerHTML;
        printItineraryDocument(contentHtml, currentTripTitle.textContent, getUserLocation());
    });

    function printItineraryDocument(itineraryHtml, title, locationStr) {
        if (!itineraryHtml || !itineraryHtml.trim()) {
            window.print();
            return;
        }

        const printWindow = window.open("", "_blank", "width=850,height=900");
        if (!printWindow) {
            // Popup blocker prevented new window, fallback to page print
            window.print();
            return;
        }

        const dateStr = new Date().toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        printWindow.document.write(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>${escapeHtml(title || "Travel Itinerary")} - TreapMate AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background: #ffffff;
            color: #111827;
            padding: 36px 48px;
            line-height: 1.6;
            font-size: 11pt;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        .doc-header {
            border-bottom: 2px solid #0284c7;
            padding-bottom: 14px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        .doc-brand {
            font-size: 20pt;
            font-weight: 800;
            color: #0284c7;
            letter-spacing: -0.02em;
        }
        .doc-title {
            font-size: 13pt;
            font-weight: 700;
            color: #1f2937;
            margin-top: 4px;
        }
        .doc-meta {
            font-size: 9pt;
            color: #6b7280;
            text-align: right;
            line-height: 1.5;
        }
        .markdown-body h1 { font-size: 16pt; margin: 20px 0 10px 0; color: #0f172a; }
        .markdown-body h2 { font-size: 13pt; margin: 20px 0 8px 0; color: #0284c7; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
        .markdown-body h3 { font-size: 11pt; margin: 14px 0 6px 0; color: #1e293b; font-weight: 700; }
        .markdown-body p { margin-bottom: 10px; color: #1f2937; }
        .markdown-body ul, .markdown-body ol { margin-bottom: 12px; padding-left: 22px; }
        .markdown-body li { margin-bottom: 4px; color: #1f2937; }
        .markdown-body table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 9pt; page-break-inside: avoid; }
        .markdown-body th { background: #f3f4f6; color: #111827; font-weight: 700; text-align: left; padding: 8px 10px; border: 1px solid #d1d5db; }
        .markdown-body td { padding: 8px 10px; border: 1px solid #e5e7eb; color: #374151; }
        .markdown-body blockquote { background: #f9fafb; border-left: 4px solid #0284c7; padding: 10px 14px; margin: 12px 0; color: #4b5563; font-style: italic; }
        .markdown-body code { font-family: 'JetBrains Mono', monospace; background: #f3f4f6; padding: 2px 5px; border-radius: 4px; font-size: 9pt; color: #0284c7; }
        .doc-footer {
            margin-top: 36px;
            padding-top: 14px;
            border-top: 1px solid #e5e7eb;
            font-size: 8.5pt;
            color: #9ca3af;
            text-align: center;
        }
        @media print {
            body { padding: 0; }
            .doc-header { margin-top: 10px; }
        }
    </style>
</head>
<body>
    <div class="doc-header">
        <div>
            <div class="doc-brand">✈️ TreapMate AI</div>
            <div class="doc-title">${escapeHtml(title || "Custom Travel Itinerary")}</div>
        </div>
        <div class="doc-meta">
            <div>Departure Point: <strong>${escapeHtml(locationStr || "Dhaka, Bangladesh")}</strong></div>
            <div>Date: <strong>${dateStr}</strong></div>
        </div>
    </div>
    <div class="markdown-body">
        ${itineraryHtml}
    </div>
    <div class="doc-footer">
        Generated by TreapMate AI • Live Flights via AviationStack • Stays via Tavily
    </div>
    <script>
        window.onload = function() {
            setTimeout(function() {
                window.print();
            }, 300);
        };
    <\/script>
</body>
</html>
        `);
        printWindow.document.close();
    }

    // -------------------------------------------------------------
    // 8. Helpers
    // -------------------------------------------------------------
    function scrollToBottom() {
        requestAnimationFrame(() => {
            chatViewport.scrollTop = chatViewport.scrollHeight;
        });
    }

    function escapeHtml(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function renderMarkdown(content) {
        if (!content) return "";
        if (window.marked && typeof window.marked.parse === "function") {
            try {
                return window.marked.parse(content);
            } catch (e) {
                console.error("Marked error:", e);
            }
        }

        // Lightweight fallback if marked is unavailable
        return escapeHtml(content)
            .replace(/\n\n/g, "<br><br>")
            .replace(/\n/g, "<br>");
    }

    // Initialize application components
    initTheme();
    initLocation();
    initTextareaAutoResize();
    initSidebar();
    renderHistory();
});

