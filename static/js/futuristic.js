// ===== RINNOVOCASA FUTURISTIC JAVASCRIPT 2025 =====

// Inizializzazione
document.addEventListener('DOMContentLoaded', function() {
    initFuturisticEffects();
    initScrollAnimations();
    initParticleSystem();
    initCursorEffects();
    initFormEnhancements();
    initNewsletterForm();
});

// ===== EFFETTI FUTURISTICI =====
function initFuturisticEffects() {
    // Effetto glitch sui titoli
    const titles = document.querySelectorAll('.hero-title, .feature-title');
    titles.forEach(title => {
        title.addEventListener('mouseenter', () => {
            title.style.animation = 'glitch 0.3s ease-in-out';
        });
        
        title.addEventListener('animationend', () => {
            title.style.animation = '';
        });
    });

    // Effetto neon sui bottoni
    const buttons = document.querySelectorAll('.btn-hero, .btn-primary');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.boxShadow = `
                0 0 20px rgba(99, 102, 241, 0.8),
                0 0 40px rgba(99, 102, 241, 0.6),
                0 0 60px rgba(99, 102, 241, 0.4)
            `;
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.boxShadow = '';
        });
    });

    // Effetto hologram sulle cards
    const cards = document.querySelectorAll('.feature-card, .glass-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px) rotateX(5deg) rotateY(5deg)';
            card.style.transition = 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) rotateX(0) rotateY(0)';
        });
    });
}

// ===== ANIMAZIONI SCROLL =====
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Animazioni specifiche per tipo di elemento
                if (entry.target.classList.contains('feature-card')) {
                    entry.target.style.animation = 'slideInUp 0.8s ease-out forwards';
                } else if (entry.target.classList.contains('stat-item')) {
                    animateCounter(entry.target.querySelector('.stat-number'));
                }
            }
        });
    }, observerOptions);

    // Osserva tutti gli elementi animabili
    document.querySelectorAll('.feature-card, .stat-item, .floating-card').forEach(el => {
        observer.observe(el);
    });

    // Parallax navbar
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        const navbar = document.querySelector('.navbar-modern');
        
        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;

        // Parallax particelle
        const particles = document.querySelectorAll('.particle');
        particles.forEach((particle, index) => {
            const speed = 0.5 + (index * 0.1);
            particle.style.transform = `translateY(${currentScroll * speed}px)`;
        });
    });
}

// ===== SISTEMA PARTICELLE =====
function initParticleSystem() {
    const heroSection = document.querySelector('.hero-futuristic');
    if (!heroSection) return;

    // Crea particelle aggiuntive dinamiche
    for (let i = 0; i < 20; i++) {
        createFloatingParticle(heroSection);
    }
}

function createFloatingParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'floating-particle';
    particle.style.cssText = `
        position: absolute;
        width: ${Math.random() * 6 + 2}px;
        height: ${Math.random() * 6 + 2}px;
        background: radial-gradient(circle, #06b6d4, #a855f7);
        border-radius: 50%;
        opacity: ${Math.random() * 0.8 + 0.2};
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: floatRandom ${Math.random() * 10 + 5}s ease-in-out infinite;
        box-shadow: 0 0 10px currentColor;
        z-index: 1;
    `;
    
    container.appendChild(particle);
    
    // Rimuovi dopo l'animazione
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
        }
    }, 15000);
}

// ===== EFFETTI CURSORE =====
function initCursorEffects() {
    let cursor = document.querySelector('.cursor-glow');
    
    if (!cursor) {
        cursor = document.createElement('div');
        cursor.className = 'cursor-glow';
        cursor.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, rgba(99,102,241,0.6) 0%, rgba(6,182,212,0.4) 50%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            mix-blend-mode: screen;
            transition: transform 0.1s ease, scale 0.2s ease;
            scale: 0;
        `;
        document.body.appendChild(cursor);
    }
    
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX - 10 + 'px';
        cursor.style.top = e.clientY - 10 + 'px';
        cursor.style.scale = '1';
    });
    
    document.addEventListener('mouseleave', () => {
        cursor.style.scale = '0';
    });
    
    // Effetti speciali su hover
    document.querySelectorAll('a, button, .feature-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.style.scale = '2';
            cursor.style.background = 'radial-gradient(circle, rgba(168,85,247,0.8) 0%, rgba(6,182,212,0.6) 50%, transparent 70%)';
        });
        
        el.addEventListener('mouseleave', () => {
            cursor.style.scale = '1';
            cursor.style.background = 'radial-gradient(circle, rgba(99,102,241,0.6) 0%, rgba(6,182,212,0.4) 50%, transparent 70%)';
        });
    });
}

// ===== CONTATORI ANIMATI =====
function animateCounter(element) {
    if (!element || element.dataset.animated) return;
    
    const target = parseInt(element.textContent.replace(/[^\d]/g, ''));
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    
    element.dataset.animated = 'true';
    
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        const formatted = Math.floor(current).toLocaleString();
        const originalText = element.textContent;
        const suffix = originalText.replace(/[\d,]/g, '');
        element.textContent = formatted + suffix;
    }, 16);
}

// ===== MIGLIORAMENTI FORM =====
function initFormEnhancements() {
    // Effetti sui form inputs
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('focus', () => {
            input.style.boxShadow = '0 0 20px rgba(99, 102, 241, 0.5)';
            input.style.borderColor = '#6366f1';
        });
        
        input.addEventListener('blur', () => {
            input.style.boxShadow = '';
            input.style.borderColor = '';
        });
    });
}

// ===== NEWSLETTER FORM =====
function initNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = form.querySelector('input[name="email"]').value;
        const button = form.querySelector('button');
        const originalText = button.innerHTML;
        
        // Animazione loading
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iscrivendo...';
        button.disabled = true;
        
        try {
            // Simula chiamata API
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Successo
            button.innerHTML = '<i class="fas fa-check me-2"></i>Iscritto!';
            button.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            
            showToast('Iscrizione completata!', 'success');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
                button.style.background = '';
                form.reset();
            }, 3000);
            
        } catch (error) {
            button.innerHTML = '<i class="fas fa-times me-2"></i>Errore';
            button.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            
            showToast('Errore durante l\'iscrizione', 'error');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
                button.style.background = '';
            }, 3000);
        }
    });
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        color: white;
        z-index: 10000;
        transform: translateX(400px);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
        max-width: 350px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    `;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-triangle' : 
                 'info-circle';
    
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${icon} me-2 fs-5"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animazione entrata
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Rimozione automatica
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 400);
    }, 5000);
}

// ===== ANIMAZIONI CSS AGGIUNTIVE =====
const additionalStyles = `
@keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
}

@keyframes floatRandom {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    25% { transform: translate(30px, -30px) rotate(90deg); }
    50% { transform: translate(-20px, -60px) rotate(180deg); }
    75% { transform: translate(-40px, -20px) rotate(270deg); }
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translate3d(0, 40px, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

.animate-in {
    animation-fill-mode: forwards;
}
`;

// Aggiungi gli stili al documento
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// ===== CONSOLE EASTER EGG =====
console.log(`
🚀 RinnovoCasa - Futuro Mode Activated!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Diagnostics: ONLINE
🔮 Hologram Effects: ACTIVE  
⚡ Quantum Particles: FLOWING
🎨 Neon Aesthetics: GLOWING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the future of home renovation!
`);
