// RinnovoCasa JavaScript

// ========================================
// Animazioni e effetti moderni 2025
// ========================================

// Intersection Observer per animazioni
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('animate-fade-in');
            }, index * 100);
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Parallax effect
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroElements = document.querySelectorAll('.hero-content, .hero-parallax');
    
    heroElements.forEach(hero => {
        if (hero) {
            hero.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });
});

// Navbar scroll effect
let lastScrollTop = 0;
window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset;
    const navbar = document.querySelector('.navbar-modern');
    
    if (navbar) {
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    
    // Newsletter form submission
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iscrizione...';
            submitBtn.disabled = true;
            
            fetch('/newsletter/signup/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    this.reset();
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                showNotification('Errore durante l\'iscrizione. Riprova più tardi.', 'error');
                console.error('Error:', error);
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // File upload drag and drop
    const fileUploadZones = document.querySelectorAll('.file-upload-zone');
    fileUploadZones.forEach(zone => {
        const input = zone.querySelector('input[type="file"]');
        
        zone.addEventListener('click', () => input.click());
        
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                updateFileDisplay(zone, files[0]);
            }
        });
        
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileDisplay(zone, e.target.files[0]);
            }
        });
    });
    
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Form validation enhancements
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Price range slider
    const priceSlider = document.getElementById('price-range');
    if (priceSlider) {
        priceSlider.addEventListener('input', function() {
            const value = this.value;
            const output = document.getElementById('price-output');
            if (output) {
                output.textContent = `€${parseInt(value).toLocaleString()}`;
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }
    
    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popover initialization
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Footer Newsletter Form
    const footerNewsletterForm = document.getElementById('footer-newsletter-form');
    if (footerNewsletterForm) {
        footerNewsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[name="email"]');
            const submitBtn = this.querySelector('.btn-newsletter-modern');
            const originalText = submitBtn.innerHTML;
            
            // Validazione email
            const email = emailInput.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!emailRegex.test(email)) {
                showToast('Inserisci un indirizzo email valido', 'error');
                emailInput.focus();
                return;
            }
            
            // Loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iscrizione...';
            submitBtn.disabled = true;
            
            // Simulazione API call (sostituire con vera chiamata)
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Iscritto!';
                submitBtn.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                
                showToast('Iscrizione completata! Ti abbiamo inviato una email di conferma.', 'success');
                emailInput.value = '';
                
                // Reset after 3 seconds
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = '';
                }, 3000);
            }, 2000);
        });
    }
    
    // Footer Stats Counter Animation
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target;
                const finalNumber = statNumber.textContent;
                
                animateCounter(statNumber, finalNumber);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-number').forEach(stat => {
        statsObserver.observe(stat);
    });
    
    // Footer Links Hover Effect
    document.querySelectorAll('.footer-links-modern a[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showToast(`Pagina "${page}" in arrivo! Stiamo lavorando per te 🚀`, 'info');
        });
    });
    
    // Social Links with tracking
    document.querySelectorAll('.social-modern').forEach(socialLink => {
        socialLink.addEventListener('click', function(e) {
            const platform = this.getAttribute('aria-label');
            
            // Analytics tracking (esempio)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'social_click', {
                    'platform': platform,
                    'location': 'footer'
                });
            }
            
            // Feedback visivo
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Contact items copy to clipboard
    document.querySelectorAll('.contact-item').forEach(item => {
        const link = item.querySelector('a[href^="tel:"], a[href^="mailto:"]');
        if (link) {
            item.addEventListener('click', function(e) {
                if (e.target !== link) {
                    const text = link.href.replace('tel:', '').replace('mailto:', '');
                    copyToClipboard(text);
                    showToast(`${text} copiato negli appunti!`, 'success');
                }
            });
            
            // Add cursor pointer
            item.style.cursor = 'pointer';
            item.title = 'Clicca per copiare';
        }
    });
    
    // Footer visibility animation
    const footerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('footer-visible');
                
                // Animate sections with delay
                const sections = entry.target.querySelectorAll('.footer-section-modern, .footer-brand-modern');
                sections.forEach((section, index) => {
                    setTimeout(() => {
                        section.style.opacity = '1';
                        section.style.transform = 'translateY(0)';
                    }, index * 150);
                });
            }
        });
    }, { threshold: 0.1 });
    
    const footer = document.querySelector('.ultra-modern-footer');
    if (footer) {
        footerObserver.observe(footer);
        
        // Initial state for sections
        footer.querySelectorAll('.footer-section-modern, .footer-brand-modern').forEach(section => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(30px)';
            section.style.transition = 'all 0.6s ease';
        });
    }
});

// Utility functions
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : `alert-${type}`;
    const icon = getIconForType(type);
    
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.innerHTML = alertHTML;
    
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = alertDiv.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-triangle',
        'warning': 'fas fa-exclamation-circle',
        'info': 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

function updateFileDisplay(zone, file) {
    const preview = zone.querySelector('.file-preview');
    if (preview) {
        preview.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file me-2"></i>
                <span>${file.name}</span>
                <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
            </div>
        `;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function performSearch(query) {
    // Implement search logic
    console.log('Searching for:', query);
}

// AJAX utility
function makeRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
        }
    };
    
    return fetch(url, { ...defaults, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Loading state management
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Caricamento...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('it-IT', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// ========================================
// Funzioni di autenticazione avanzata
// ========================================

// API helper function
async function makeApiCall(url, data = null, method = 'GET') {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: 'Errore di connessione' };
    }
}

// Get CSRF token
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Magic Link functionality
async function sendMagicLink(email) {
    if (!email || !isValidEmail(email)) {
        showNotification('❌ Inserisci un\'email valida.', 'error');
        return false;
    }
    
    showLoadingState('sendMagicLinkBtn', true);
    
    const result = await makeApiCall('/utenti/api/send-magic-link/', { email }, 'POST');
    
    showLoadingState('sendMagicLinkBtn', false);
    
    if (result.success) {
        showNotification('✨ ' + result.message, 'success');
        return true;
    } else {
        showNotification('❌ ' + (result.error || 'Errore nell\'invio del link'), 'error');
        return false;
    }
}

// Check if user exists
async function checkUserExists(email) {
    if (!email || !isValidEmail(email)) {
        return false;
    }
    
    const result = await makeApiCall('/utenti/api/check-user/', { email }, 'POST');
    return result.exists || false;
}

// Reset password request
async function requestPasswordReset(email) {
    if (!email || !isValidEmail(email)) {
        showNotification('❌ Inserisci un\'email valida.', 'error');
        return false;
    }
    
    const result = await makeApiCall('/utenti/api/reset-password/', { email }, 'POST');
    
    if (result.success) {
        showNotification('📧 ' + result.message, 'success');
        return true;
    } else {
        showNotification('❌ ' + (result.error || 'Errore nella richiesta'), 'error');
        return false;
    }
}

// Email validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show loading state on buttons
function showLoadingState(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    const icon = button.querySelector('i');
    const originalClass = button.dataset.originalIcon || icon.className;
    
    if (isLoading) {
        button.dataset.originalIcon = originalClass;
        icon.className = 'fas fa-spinner fa-spin';
        button.disabled = true;
    } else {
        icon.className = originalClass;
        button.disabled = false;
        delete button.dataset.originalIcon;
    }
}

// Auto-complete email suggestions
function setupEmailAutoComplete(inputElement, suggestionsElement) {
    const commonDomains = [
        'gmail.com', 'yahoo.it', 'hotmail.it', 'outlook.it', 'libero.it', 
        'tiscali.it', 'tin.it', 'virgilio.it', 'alice.it', 'fastwebnet.it'
    ];
    
    inputElement.addEventListener('input', function() {
        const value = this.value;
        const atIndex = value.indexOf('@');
        
        if (atIndex > 0 && atIndex === value.length - 1) {
            showEmailSuggestions(value, commonDomains, suggestionsElement, inputElement);
        } else if (atIndex > 0) {
            const domain = value.substring(atIndex + 1);
            if (domain.length > 0) {
                const filtered = commonDomains.filter(d => 
                    d.toLowerCase().startsWith(domain.toLowerCase())
                );
                if (filtered.length > 0) {
                    showEmailSuggestions(value, filtered, suggestionsElement, inputElement);
                } else {
                    hideEmailSuggestions(suggestionsElement);
                }
            }
        } else {
            hideEmailSuggestions(suggestionsElement);
        }
        
        // Check if user exists (debounced)
        clearTimeout(inputElement.checkUserTimeout);
        inputElement.checkUserTimeout = setTimeout(async () => {
            if (isValidEmail(value)) {
                const exists = await checkUserExists(value);
                if (exists) {
                    showNotification('👋 Utente riconosciuto! Puoi usare l\'accesso istantaneo.', 'info', 3000);
                }
            }
        }, 1000);
    });
}

function showEmailSuggestions(currentValue, domains, suggestionsElement, inputElement) {
    const atIndex = currentValue.indexOf('@');
    const localPart = currentValue.substring(0, atIndex + 1);
    
    suggestionsElement.innerHTML = '';
    domains.slice(0, 5).forEach(domain => {
        const suggestion = document.createElement('div');
        suggestion.className = 'email-suggestion';
        suggestion.textContent = localPart + domain;
        suggestion.addEventListener('click', function() {
            inputElement.value = this.textContent;
            hideEmailSuggestions(suggestionsElement);
            inputElement.dispatchEvent(new Event('input'));
        });
        suggestionsElement.appendChild(suggestion);
    });
    suggestionsElement.style.display = 'block';
}

function hideEmailSuggestions(suggestionsElement) {
    suggestionsElement.style.display = 'none';
}

// Social authentication handlers
function handleGoogleLogin() {
    showNotification('🔄 Reindirizzamento a Google...', 'info');
    // In produzione, redirect a Google OAuth
    setTimeout(() => {
        // window.location.href = '/auth/google/';
        showNotification('🔧 Integrazione Google in fase di configurazione.', 'warning');
    }, 1000);
}

function handleSpidLogin() {
    showNotification('🔄 Reindirizzamento a SPID...', 'info');
    // In produzione, redirect a SPID
    setTimeout(() => {
        // window.location.href = '/auth/spid/';
        showNotification('🔧 Integrazione SPID in fase di configurazione.', 'warning');
    }, 1000);
}

function handleCieLogin() {
    showNotification('🔄 Reindirizzamento a CIE...', 'info');
    // In produzione, redirect a CIE
    setTimeout(() => {
        // window.location.href = '/auth/cie/';
        showNotification('🔧 Integrazione CIE in fase di configurazione.', 'warning');
    }, 1000);
}

// ========================================
// Modern Footer Interactions
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Footer Newsletter Form
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[name="email"]');
            const submitBtn = this.querySelector('.btn-newsletter-modern');
            const originalText = submitBtn.innerHTML;
            
            // Validazione email
            const email = emailInput.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!emailRegex.test(email)) {
                showToast('Inserisci un indirizzo email valido', 'error');
                emailInput.focus();
                return;
            }
            
            // Loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iscrizione...';
            submitBtn.disabled = true;
            
            // Simulazione API call (sostituire con vera chiamata)
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Iscritto!';
                submitBtn.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                
                showToast('Iscrizione completata! Ti abbiamo inviato una email di conferma.', 'success');
                emailInput.value = '';
                
                // Reset after 3 seconds
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = '';
                }, 3000);
            }, 2000);
        });
    }
    
    // Footer Stats Counter Animation
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target;
                const finalNumber = statNumber.textContent;
                
                animateCounter(statNumber, finalNumber);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-number').forEach(stat => {
        statsObserver.observe(stat);
    });
    
    // Footer Links Hover Effect
    document.querySelectorAll('.footer-links-modern a[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showToast(`Pagina "${page}" in arrivo! Stiamo lavorando per te 🚀`, 'info');
        });
    });
    
    // Social Links with tracking
    document.querySelectorAll('.social-modern').forEach(socialLink => {
        socialLink.addEventListener('click', function(e) {
            const platform = this.getAttribute('aria-label');
            
            // Analytics tracking (esempio)
            if (typeof gtag !== 'undefined') {
                gtag('event', 'social_click', {
                    'platform': platform,
                    'location': 'footer'
                });
            }
            
            // Feedback visivo
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Contact items copy to clipboard
    document.querySelectorAll('.contact-item').forEach(item => {
        const link = item.querySelector('a[href^="tel:"], a[href^="mailto:"]');
        if (link) {
            item.addEventListener('click', function(e) {
                if (e.target !== link) {
                    const text = link.href.replace('tel:', '').replace('mailto:', '');
                    copyToClipboard(text);
                    showToast(`${text} copiato negli appunti!`, 'success');
                }
            });
            
            // Add cursor pointer
            item.style.cursor = 'pointer';
            item.title = 'Clicca per copiare';
        }
    });
    
    // Footer visibility animation
    const footerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('footer-visible');
                
                // Animate sections with delay
                const sections = entry.target.querySelectorAll('.footer-section-modern, .footer-brand-modern');
                sections.forEach((section, index) => {
                    setTimeout(() => {
                        section.style.opacity = '1';
                        section.style.transform = 'translateY(0)';
                    }, index * 150);
                });
            }
        });
    }, { threshold: 0.1 });
    
    const footer = document.querySelector('.ultra-modern-footer');
    if (footer) {
        footerObserver.observe(footer);
        
        // Initial state for sections
        footer.querySelectorAll('.footer-section-modern, .footer-brand-modern').forEach(section => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(30px)';
            section.style.transition = 'all 0.6s ease';
        });
    }
});

// Utility Functions
function animateCounter(element, target) {
    const duration = 2000;
    const start = 0;
    const startTime = performance.now();
    
    // Parse target number (handle "+" and other suffixes)
    const isPlus = target.includes('+');
    const suffix = target.match(/[^0-9]/g)?.join('') || '';
    const targetNumber = parseInt(target.replace(/[^0-9]/g, ''));
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (targetNumber - start) * easeOut);
        
        element.textContent = current + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target; // Ensure exact final value
        }
    }
    
    requestAnimationFrame(updateCounter);
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-modern');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast-modern toast-${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-triangle',
        warning: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="toast-content">
            <i class="${icons[type]} me-2"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}
