// PayPilot AI — Intelligent Shopping & Payment Assistant Logic

const API_BASE = window.location.port === '8000'
  ? '/api'
  : 'http://127.0.0.1:8000/api';

const state = {
  activeTab: 'overview',
  products: [],
  comparedIds: [1, 2], // Pre-select Sony & Bose for instant comparison view
  activeCategory: 'All',
  searchQuery: '',
  orders: [],
  payments: [],
  selectedCheckoutProduct: null
};

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupEventListeners();
  loadAllData();
});

function setupNavigation() {
  const navButtons = document.querySelectorAll('.nav-item');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;

  // Update Nav Active state
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Switch Tab Panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.remove('active');
  });
  const activePane = document.getElementById(`tab-${tabId}`);
  if (activePane) activePane.classList.add('active');

  // Update Header Titles
  const titleMap = {
    'overview': {
      title: 'Shop Smarter with PayPilot AI',
      subtitle: 'Your intelligent shopping companion, from discovery to checkout.'
    },
    'assistant': {
      title: 'AI Shopping Assistant',
      subtitle: 'Real-time conversational product discovery, spec analysis, and budget matching'
    },
    'comparison': {
      title: 'Product Comparison Matrix',
      subtitle: 'Side-by-side technical specs, battery life, user ratings, and value rating'
    },
    'advisor': {
      title: 'AI Purchase Advisor',
      subtitle: 'Algorithmic price drop detection, verified deal ratings, and buying recommendations'
    },
    'orders': {
      title: 'My Orders',
      subtitle: 'Track your recent purchases and active delivery shipments'
    },
    'payments': {
      title: 'Payment History',
      subtitle: 'Verified PayPal transaction history and order receipts'
    }
  };

  if (titleMap[tabId]) {
    document.getElementById('pageTitle').innerText = titleMap[tabId].title;
    document.getElementById('pageSubtitle').innerText = titleMap[tabId].subtitle;
  }

  // Refresh tab views
  if (tabId === 'comparison') renderComparisonView();
  if (tabId === 'orders') loadOrders();
  if (tabId === 'payments') loadPayments();
  if (tabId === 'advisor') loadAdvisorDeals();
}

function setupEventListeners() {
  // Search Form
  const searchForm = document.getElementById('heroSearchForm');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('aiShoppingSearchInput');
      state.searchQuery = input.value.trim();
      loadProducts();
    });
  }

  // Category filter buttons
  document.querySelectorAll('.filter-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeCategory = btn.getAttribute('data-category');
      loadProducts();
    });
  });

  // Chat Form
  const chatForm = document.getElementById('chatForm');
  if (chatForm) {
    chatForm.addEventListener('submit', handleChatSubmit);
  }

  // Close modals on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
    }
  });
}

// --- Data Fetching ---

async function loadAllData() {
  await Promise.all([
    loadOverviewStats(),
    loadProducts(),
    loadAdvisorDeals(),
    loadOrders(),
    loadPayments()
  ]);
  renderComparisonView();
}

async function loadOverviewStats() {
  try {
    const res = await fetch(`${API_BASE}/overview`);
    if (!res.ok) throw new Error('API unavailable');
    const data = await res.json();

    document.getElementById('kpiTotalProducts').innerText = data.total_products;
    document.getElementById('kpiTotalOrders').innerText = data.total_orders;
    setSystemStatus(true);
  } catch (err) {
    console.error('Failed to load overview:', err);
    setSystemStatus(false);
  }
}

async function loadProducts() {
  try {
    let url = `${API_BASE}/products?`;
    if (state.activeCategory && state.activeCategory !== 'All') {
      url += `category=${encodeURIComponent(state.activeCategory)}&`;
    }
    if (state.searchQuery) {
      url += `q=${encodeURIComponent(state.searchQuery)}&`;
    }

    const res = await fetch(url);
    const data = await res.json();
    state.products = data;
    renderProductsGrid(data);
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

function renderProductsGrid(products) {
  const container = document.getElementById('productsGrid');
  if (!products || products.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
        No products match your search. Try searching for "Headphones", "Laptops", or "Mouse".
      </div>
    `;
    return;
  }

  container.innerHTML = products.map(p => {
    const isCompared = state.comparedIds.includes(p.id);
    const specs = p.specs || {};
    const specsChips = Object.entries(specs).slice(0, 3).map(([k, v]) => `
      <span class="spec-chip">${k}: ${v}</span>
    `).join('');

    let badgeHtml = '';
    if (p.badge) {
      let badgeClass = 'badge-deal';
      if (p.badge.includes('Best')) badgeClass = 'badge-best-seller';
      if (p.badge.includes('Editor') || p.badge.includes('Choice')) badgeClass = 'badge-editor';
      badgeHtml = `<span class="badge-tag ${badgeClass}">${p.badge}</span>`;
    }

    return `
      <div class="product-card">
        <div class="product-badge-row">
          <span class="product-category-label">${escapeHtml(p.category)}</span>
          ${badgeHtml}
        </div>

        <h4 class="product-title">${escapeHtml(p.name)}</h4>

        <div class="product-rating-row">
          <span>★ ${p.rating.toFixed(1)}</span>
          <span class="rating-count">(${p.reviews_count} reviews)</span>
        </div>

        <p class="product-desc">${escapeHtml(p.description)}</p>

        <div class="product-specs-list">
          ${specsChips}
        </div>

        <div class="product-price-row">
          <span class="product-curr-price">${formatCurrency(p.price)}</span>
          ${p.original_price ? `<span class="product-orig-price">${formatCurrency(p.original_price)}</span>` : ''}
          ${p.original_price ? `<span class="product-discount-pill">Save ${formatCurrency(p.original_price - p.price)}</span>` : ''}
        </div>

        <div class="product-actions-row">
          <button class="btn-compare ${isCompared ? 'selected' : ''}" onclick="toggleCompare(${p.id})">
            ${isCompared ? 'Comparing ✓' : '+ Compare'}
          </button>
          <button class="btn-buy-paypal" onclick="openPayPalCheckout(${p.id})">
            <span>PayPal Buy</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// --- Product Comparison ---

function toggleCompare(productId) {
  const idx = state.comparedIds.indexOf(productId);
  if (idx > -1) {
    state.comparedIds.splice(idx, 1);
  } else {
    if (state.comparedIds.length >= 4) {
      showToast('Maximum 4 items can be compared simultaneously.', 'info');
      return;
    }
    state.comparedIds.push(productId);
  }

  updateCompareBadges();
  renderProductsGrid(state.products);
  renderComparisonView();
}

function resetComparison() {
  state.comparedIds = [];
  updateCompareBadges();
  renderProductsGrid(state.products);
  renderComparisonView();
}

function updateCompareBadges() {
  const count = state.comparedIds.length;
  document.getElementById('compareCountBadge').innerText = count;
  document.getElementById('compareTrayNum').innerText = count;
  const kpiEl = document.getElementById('kpiCompareSelected');
  if (kpiEl) kpiEl.innerText = count;
}

async function renderComparisonView() {
  updateCompareBadges();
  const overviewBox = document.getElementById('overviewComparisonContainer');
  const fullBox = document.getElementById('fullComparisonContainer');

  if (state.comparedIds.length === 0) {
    const emptyHtml = `
      <div style="text-align: center; padding: 36px; color: var(--text-muted);">
        <p>No products selected for comparison.</p>
        <button class="btn btn-secondary btn-sm" style="margin-top: 10px;" onclick="switchTab('overview')">Select Products to Compare</button>
      </div>
    `;
    if (overviewBox) overviewBox.innerHTML = emptyHtml;
    if (fullBox) fullBox.innerHTML = emptyHtml;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_ids: state.comparedIds })
    });
    if (!res.ok) throw new Error('Could not compare');
    const data = await res.json();
    const items = data.products;

    // Collect all spec keys across items
    const allSpecKeys = new Set();
    items.forEach(item => {
      if (item.specs && typeof item.specs === 'object') {
        Object.keys(item.specs).forEach(k => allSpecKeys.add(k));
      }
    });

    const tableHtml = `
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Specification</th>
            ${items.map(i => `
              <th>
                <div style="color:#fff;font-weight:700;">${escapeHtml(i.name)}</div>
                <div style="color:var(--accent-cyan);font-size:0.75rem;">${escapeHtml(i.category)}</div>
              </th>
            `).join('')}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="comp-feature-name">Current Price</td>
            ${items.map(i => `<td class="comp-price-cell">${formatCurrency(i.price)}</td>`).join('')}
          </tr>
          <tr>
            <td class="comp-feature-name">User Rating</td>
            ${items.map(i => `<td>★ ${i.rating.toFixed(1)} <small style="color:var(--text-muted);">(${i.reviews_count} reviews)</small></td>`).join('')}
          </tr>
          ${Array.from(allSpecKeys).map(specKey => `
            <tr>
              <td class="comp-feature-name">${specKey}</td>
              ${items.map(i => `<td>${(i.specs && i.specs[specKey]) || '—'}</td>`).join('')}
            </tr>
          `).join('')}
          <tr>
            <td class="comp-feature-name">Checkout</td>
            ${items.map(i => `
              <td>
                <button class="btn-buy-paypal" style="padding:6px 12px;font-size:0.78rem;" onclick="openPayPalCheckout(${i.id})">
                  PayPal Checkout
                </button>
              </td>
            `).join('')}
          </tr>
        </tbody>
      </table>
    `;

    if (overviewBox) overviewBox.innerHTML = tableHtml;
    if (fullBox) fullBox.innerHTML = tableHtml;
  } catch (err) {
    console.error('Comparison error:', err);
  }
}

// --- Purchase Advisor ---

async function loadAdvisorDeals() {
  try {
    const res = await fetch(`${API_BASE}/advisor/deals`);
    const deals = await res.json();

    const previewGrid = document.getElementById('advisorPreviewGrid');
    const fullGrid = document.getElementById('advisorFullGrid');

    const html = deals.map(d => `
      <div class="deal-card">
        <div class="deal-card-header">
          <span class="deal-tag">${d.discount_pct}% OFF DEAL</span>
          <span style="color:var(--accent-amber);font-size:0.78rem;">★ ${d.rating}</span>
        </div>
        <div class="deal-title">${escapeHtml(d.name)}</div>
        <div class="deal-pricing">
          <span class="deal-curr-price">${formatCurrency(d.current_price)}</span>
          <span class="deal-orig-price">${formatCurrency(d.original_price)}</span>
        </div>
        <div class="deal-advice-text">
          💡 ${escapeHtml(d.advice)}
        </div>
        <div style="margin-top: 12px; display: flex; gap: 8px;">
          <button class="btn btn-secondary btn-sm" onclick="toggleCompare(${d.product_id})">Compare</button>
          <button class="btn-buy-paypal" style="font-size:0.75rem;padding:5px 10px;" onclick="openPayPalCheckout(${d.product_id})">PayPal</button>
        </div>
      </div>
    `).join('');

    if (previewGrid) previewGrid.innerHTML = html.slice(0, 3);
    if (fullGrid) fullGrid.innerHTML = html;
  } catch (err) {
    console.error('Failed to load deals:', err);
  }
}

// --- Orders and Payments ---

async function loadOrders() {
  try {
    const res = await fetch(`${API_BASE}/orders`);
    const orders = await res.json();
    state.orders = orders;

    const tbody = document.getElementById('ordersTableBody');
    if (!orders || orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:20px;color:var(--text-muted);">No orders found.</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map(o => `
      <tr>
        <td><strong>${escapeHtml(o.order_number)}</strong></td>
        <td>${escapeHtml(o.product_name)}</td>
        <td style="font-family:var(--font-mono);font-weight:700;color:#fff;">${formatCurrency(o.price)}</td>
        <td>
          <span class="status-tag status-${o.status.toLowerCase().replace(' ', '-')}">${o.status}</span>
        </td>
        <td>${o.order_date}</td>
        <td>
          <span class="badge-paypal">${o.payment_method}</span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to load orders:', err);
  }
}

async function loadPayments() {
  try {
    const res = await fetch(`${API_BASE}/payments`);
    const payments = await res.json();
    state.payments = payments;

    const tbody = document.getElementById('paymentsTableBody');
    if (!payments || payments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--text-muted);">No payment records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = payments.map(p => `
      <tr>
        <td style="font-family:var(--font-mono);color:var(--accent-cyan);">${escapeHtml(p.transaction_id)}</td>
        <td><strong>${escapeHtml(p.order_number)}</strong></td>
        <td style="font-family:var(--font-mono);font-weight:700;color:#fff;">${formatCurrency(p.amount)}</td>
        <td>${p.currency}</td>
        <td><span class="badge-paypal">${p.gateway}</span></td>
        <td><span class="status-tag status-completed">${p.status}</span></td>
        <td style="color:var(--text-muted);font-size:0.8rem;">${p.timestamp}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to load payments:', err);
  }
}

// --- PayPal Checkout Entry Point ---

function openPayPalCheckout(productId) {
  const product = state.products.find(p => p.id === productId);
  if (!product) return;

  state.selectedCheckoutProduct = product;
  document.getElementById('checkoutProductName').innerText = product.name;
  document.getElementById('checkoutProductCategory').innerText = product.category;
  document.getElementById('checkoutProductPrice').innerText = formatCurrency(product.price);

  const estimatedTax = roundNumber(product.price * 0.08, 2);
  const total = roundNumber(product.price + estimatedTax, 2);

  document.getElementById('checkoutTax').innerText = formatCurrency(estimatedTax);
  document.getElementById('checkoutTotal').innerText = formatCurrency(total);

  openModal('paypalCheckoutModal');
}

function handlePayPalEntryClick() {
  showToast('PayPal Checkout Entry Point verified. Production gateway integration will proceed in next phase.', 'info');
  closeModal('paypalCheckoutModal');
}

// --- AI Shopping Assistant Chat ---

async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  await sendChatMessage(message);
}

async function sendChatMessage(message) {
  const chatMessages = document.getElementById('chatMessages');

  // Render User Message
  chatMessages.insertAdjacentHTML('beforeend', `
    <div class="chat-bubble user-msg">
      <div class="bubble-header">You</div>
      <div class="bubble-body">${escapeHtml(message)}</div>
      <div class="bubble-time">Just now</div>
    </div>
  `);

  // Render Typing Indicator
  const typingId = `typing-${Date.now()}`;
  chatMessages.insertAdjacentHTML('beforeend', `
    <div class="chat-bubble ai-msg" id="${typingId}">
      <div class="bubble-header">PayPilot AI</div>
      <div class="bubble-body"><span style="color:var(--accent-cyan);">Analyzing live catalog specifications and pricing...</span></div>
    </div>
  `);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch(`${API_BASE}/ai/shopping-assistant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    const typingElem = document.getElementById(typingId);
    if (typingElem) typingElem.remove();

    if (data.source === 'gemini-ai') {
      document.getElementById('aiSourceBadge').innerText = 'Gemini 1.5 Live AI';
    } else {
      document.getElementById('aiSourceBadge').innerText = 'Shopping Engine';
    }

    chatMessages.insertAdjacentHTML('beforeend', `
      <div class="chat-bubble ai-msg">
        <div class="bubble-header">PayPilot AI • ${data.source === 'gemini-ai' ? 'Gemini 1.5' : 'Shopping Engine'}</div>
        <div class="bubble-body">${renderMarkdown(data.reply)}</div>
        <div class="bubble-time">Just now</div>
      </div>
    `);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (err) {
    const typingElem = document.getElementById(typingId);
    if (typingElem) typingElem.remove();

    chatMessages.insertAdjacentHTML('beforeend', `
      <div class="chat-bubble ai-msg">
        <div class="bubble-header">System</div>
        <div class="bubble-body" style="color:var(--accent-rose);">Error connecting to shopping assistant backend. Ensure server is running.</div>
      </div>
    `);
  }
}

function sendChatPrompt(promptText) {
  switchTab('assistant');
  const input = document.getElementById('chatInput');
  input.value = promptText;
  document.getElementById('chatForm').dispatchEvent(new Event('submit'));
}

function quickSearch(query) {
  document.getElementById('aiShoppingSearchInput').value = query;
  state.searchQuery = query;
  loadProducts();
}

// --- Utilities ---

function formatCurrency(val) {
  const num = Number(val) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(num);
}

function roundNumber(value, decimals) {
  return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderMarkdown(md) {
  if (!md) return '';
  let html = md;
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/### (.*?)\n/g, '<h4 style="margin:8px 0 4px;color:#fff;">$1</h4>');
  html = html.replace(/## (.*?)\n/g, '<h3 style="margin:10px 0 6px;color:#fff;">$1</h3>');
  html = html.replace(/^- (.*?)(\n|$)/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*?<\/li>)/gs, '<ul style="margin:8px 0 8px 18px;">$1</ul>');
  html = html.replace(/\n\n/g, '<br><br>');
  html = html.replace(/\n/g, '<br>');
  return html;
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('open');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('open');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function setSystemStatus(isOnline) {
  const dot = document.querySelector('.status-dot');
  const text = document.getElementById('apiStatusText');
  if (dot && text) {
    if (isOnline) {
      dot.style.backgroundColor = 'var(--accent-emerald)';
      text.innerText = 'Assistant Online';
    } else {
      dot.style.backgroundColor = 'var(--accent-rose)';
      text.innerText = 'Assistant Offline';
    }
  }
}
