/**
 * PATRIC FARLEY — PORTFOLIO 2026
 * Real-time Community Hub with Live Data
 */

(function() {
    'use strict';

    const API_BASE = window.location.hostname === 'localhost' 
        ? 'http://localhost:3002' 
        : '';

    const CACHE_DURATION = 180000; // 3 minutes
    let lastFetch = 0;
    let cachedData = null;

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        initNavigation();
        initScrollReveal();
        initCounters();
        initCommunity();
        initLiveData();
    }

    // ========================================
    // LIVE DATA FROM DEXSCREENER
    // ========================================
    async function fetchLiveData() {
        const now = Date.now();
        
        // Return cached data if fresh
        if (cachedData && now - lastFetch < CACHE_DURATION) {
            return cachedData;
        }
        
        try {
            // Try to fetch from API bridge
            const response = await fetch(`${API_BASE}/api/scanner`, {
                signal: AbortSignal.timeout(10000)
            });
            
            if (!response.ok) throw new Error('API failed');
            
            const data = await response.json();
            cachedData = data;
            lastFetch = now;
            
            return data;
        } catch (err) {
            console.log('API not available, using fallback data');
            return getFallbackData();
        }
    }

    function getFallbackData() {
        // Fallback when API is down
        return {
            movers: [
                { token: 'BONK', change24h: '+12.5', liquidity: 2500000 },
                { token: 'WIF', change24h: '-8.3', liquidity: 1800000 },
                { token: 'PEPE', change24h: '+45.2', liquidity: 3200000 }
            ],
            dips: [
                { token: 'TROLL', change24h: '-42.0', score: 85 },
                { token: 'WOBBLES', change24h: '-38.5', score: 72 }
            ],
            updated: new Date().toISOString()
        };
    }

    function initLiveData() {
        updateScannerFeed();
        
        // Auto-refresh every 3 minutes
        setInterval(updateScannerFeed, 180000);
    }

    async function updateScannerFeed() {
        const feed = document.getElementById('scanner-feed');
        if (!feed) return;
        
        feed.innerHTML = `
            <div class="scanner-item">
                <span class="token">Loading...</span>
                <span class="change neutral">Fetching live data</span>
                <span class="time">Now</span>
            </div>
        `;
        
        const data = await fetchLiveData();
        
        if (data.movers && data.movers.length > 0) {
            const topMover = data.movers[0];
            const isUp = parseFloat(topMover.change24h) > 0;
            
            feed.innerHTML = `
                <div class="scanner-item">
                    <span class="token">${topMover.token}</span>
                    <span class="change ${isUp ? 'up' : 'down'}">${isUp ? '+' : ''}${topMover.change24h}%</span>
                    <span class="time">Live</span>
                </div>
                ${data.movers.slice(1, 3).map(m => {
                    const up = parseFloat(m.change24h) > 0;
                    return `
                        <div class="scanner-item" style="margin-top: 8px; opacity: 0.7;">
                            <span class="token">${m.token}</span>
                            <span class="change ${up ? 'up' : 'down'}">${up ? '+' : ''}${m.change24h}%</span>
                        </div>
                    `;
                }).join('')}
            `;
        } else {
            feed.innerHTML = `
                <div class="scanner-item">
                    <span class="token">No alerts</span>
                    <span class="change neutral">Market quiet</span>
                    <span class="time">--</span>
                </div>
            `;
        }
    }

    // ========================================
    // AI COMMANDS
    // ========================================
    window.runCommand = async function(command) {
        const terminal = document.getElementById('terminal-body');
        if (!terminal) return;
        
        // Show loading
        terminal.innerHTML = `<p class="terminal-line"><strong>> ${command}</strong></p>
            <p class="terminal-line" style="color: var(--color-text-secondary);">Running...</p>`;
        
        const data = await fetchLiveData();
        
        const responses = {
            'dipping': () => {
                if (data.dips && data.dips.length > 0) {
                    const dips = data.dips.slice(0, 3);
                    return `💎 Dip Opportunities Found:\n\n${dips.map((d, i) => 
                        `${i + 1}. ${d.token}: ${d.change24h}% (Score: ${d.score})`
                    ).join('\n')}\n\n⚠️ DYOR - High risk plays`;
                }
                return `📉 No major dips detected\n\nMarket is relatively stable. Check again in 15 min.`;
            },
            
            'early-hold': () => {
                const holds = data.movers?.filter(m => parseFloat(m.change24h) > 5 && parseFloat(m.change24h) < 30) || [];
                if (holds.length > 0) {
                    return `💎 Early Hold Candidates:\n\n${holds.slice(0, 3).map((h, i) => 
                        `${i + 1}. ${h.token}: +${h.change24h}% (${(h.liquidity / 1000000).toFixed(1)}M liq)`
                    ).join('\n')}\n\n✅ Moderate growth, established liquidity`;
                }
                return `💎 No ideal hold candidates\n\nMarket either too hot or too cold.\nCheck trending tokens.`;
            },
            
            'gem-finder': () => {
                const gems = data.movers?.filter(m => parseFloat(m.change24h) > 30) || [];
                if (gems.length > 0) {
                    return `🚀 High Momentum Tokens:\n\n${gems.slice(0, 3).map((g, i) => 
                        `${i + 1}. ${g.token}: +${g.change24h}% 🔥`
                    ).join('\n')}\n\n⚠️ High volatility - Manage risk`;
                }
                return `💎 No gems detected\n\nMarket quiet. No major pumps.`;
            },
            
            'status': () => {
                return `📊 Portfolio Status:\n\nBalance: $241.20 (+5.20)\nPositions: 0 (flat)\nLast Update: ${new Date(data.updated).toLocaleTimeString()}\n\n✅ All systems operational`;
            }
        };
        
        const response = responses[command] ? responses[command]() : 'Command not recognized. Try: dipping, early-hold, gem-finder, status';
        
        terminal.innerHTML = `<p class="terminal-line"><strong>> ${command}</strong></p>
            <p class="terminal-line" style="white-space: pre-line; color: var(--color-text-secondary); margin-top: 12px;">${response}</p>`;
    };

    window.runScanner = async function(type) {
        await updateScannerFeed();
    };

    // ========================================
    // NAVIGATION (from original)
    // ========================================
    function initNavigation() {
        const nav = document.getElementById('nav');
        const navToggle = document.getElementById('nav-toggle');
        const navLinks = document.getElementById('nav-links');
        
        if (navToggle) {
            navToggle.addEventListener('click', () => {
                navToggle.classList.toggle('active');
                navLinks.classList.toggle('active');
            });
        }
        
        // Smooth scroll for nav links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    // Close mobile menu
                    navToggle?.classList.remove('active');
                    navLinks?.classList.remove('active');
                }
            });
        });
        
        // Nav background on scroll
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                nav?.classList.add('scrolled');
            } else {
                nav?.classList.remove('scrolled');
            }
        }, { passive: true });
    }

    // ========================================
    // SCROLL REVEAL
    // ========================================
    function initScrollReveal() {
        const reveals = document.querySelectorAll('[data-reveal]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px'
        });
        
        reveals.forEach(el => observer.observe(el));
    }

    // ========================================
    // COUNTERS
    // ========================================
    function initCounters() {
        const counters = document.querySelectorAll('[data-count]');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => observer.observe(counter));
    }

    function animateCounter(element) {
        const target = parseFloat(element.dataset.count);
        const prefix = element.dataset.prefix || '';
        const suffix = element.dataset.suffix || '';
        const duration = 1500;
        const start = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 4);
            const current = target * eased;
            
            if (target % 1 === 0) {
                element.textContent = prefix + Math.round(current).toLocaleString() + suffix;
            } else {
                element.textContent = prefix + current.toFixed(2) + suffix;
            }
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }

    // ========================================
    // SMART MONEY FEATURES
    // ========================================
    window.loadSmartMoney = async function() {
        const feed = document.getElementById('smart-money-feed');
        if (!feed) return;
        
        feed.innerHTML = `
            <div class="scanner-item">
                <span class="token">Fetching...</span>
                <span class="change neutral">Loading whale data</span>
            </div>
        `;
        
        try {
            const response = await fetch(`${API_BASE}/api/smart-money`);
            if (!response.ok) throw new Error('Failed');
            
            const data = await response.json();
            
            if (data.whales && data.whales.length > 0) {
                feed.innerHTML = data.whales.slice(0, 3).map(w => {
                    const netPositive = parseFloat(w.netFlow) > 0;
                    return `
                        <div class="scanner-item">
                            <span class="token">${w.token}</span>
                            <span class="change ${netPositive ? 'up' : 'down'}">${netPositive ? '+' : ''}${w.netFlow} SOL</span>
                            <span class="time">${w.holders} holders</span>
                        </div>
                    `;
                }).join('');
            } else {
                feed.innerHTML = `
                    <div class="scanner-item">
                        <span class="token">No whales</span>
                        <span class="change neutral">Market quiet</span>
                    </div>
                `;
            }
        } catch (err) {
            feed.innerHTML = `
                <div class="scanner-item">
                    <span class="token">Error</span>
                    <span class="change neutral">Try again</span>
                </div>
            `;
        }
    };
    
    // ========================================
    // COMMUNITY FEATURES
    // ========================================
    function initCommunity() {
        // Initialize any community-specific features
        console.log('🚀 Community Hub initialized');
        console.log('📊 Live data fetching every 3 minutes');
        console.log('🐋 Smart Money tracking active');
    }

    // Expose to global scope
    window.Portfolio = {
        refresh: init,
        fetchData: fetchLiveData
    };

})();
