(function () {
  const body = document.body;
  const overrideBase = window.__FICTO_API_BASE__;
  const fallbackBase =
    overrideBase && overrideBase !== ''
      ? overrideBase
      : body.dataset.apiBase && body.dataset.apiBase !== ''
        ? body.dataset.apiBase
        : window.location.protocol === 'file:'
          ? 'http://127.0.0.1:8000'
          : window.location.origin;
  const API_BASE = fallbackBase.replace(/\/$/, '');
  const currencyFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

  const elements = {
    floatingCart: document.getElementById('cart'),
    heroStats: {
      products: document.getElementById('hero-stat-products'),
      avgPrice: document.getElementById('hero-stat-avg-price'),
      cart: document.getElementById('hero-stat-cart'),
    },
    productGrid: document.getElementById('product-grid'),
    productStatus: document.getElementById('product-status'),
    productLoading: document.getElementById('product-loading'),
    productEmpty: document.getElementById('product-empty'),
    productSearch: document.getElementById('product-search'),
    productSort: document.getElementById('product-sort'),
    productFilterStock: document.getElementById('product-in-stock'),
    cartLoading: document.getElementById('cart-loading'),
    cartItems: document.getElementById('cart-items'),
    cartEmpty: document.getElementById('cart-empty'),
    cartTotalItems: document.getElementById('cart-total-items'),
    cartGrandTotal: document.getElementById('cart-grand-total'),
    cartMessage: document.getElementById('cart-message'),
    clearCart: document.getElementById('clear-cart'),
    checkout: document.getElementById('checkout'),
    toast: document.getElementById('app-toast'),
    links: document.querySelectorAll('[data-link]'),
  };

  const state = {
    products: [],
    filtered: [],
    search: '',
    sort: 'featured',
    stockOnly: false,
    cart: { items: [], total_items: 0, grand_total: 0 },
  };

  let toastTimeout;

  function wireExternalLinks() {
    if (!elements.links) return;
    const mapping = {
      signin: `${API_BASE}/signin`,
      meta: `${API_BASE}/meta`,
      docs: `${API_BASE}/docs`,
    };
    elements.links.forEach((anchor) => {
      const key = anchor.dataset.link;
      if (!key || !mapping[key]) return;
      anchor.href = mapping[key];
      anchor.rel = 'noopener';
      anchor.target = '_self';
    });
  }

  function showToast(message, type = 'success') {
    if (!elements.toast) return;
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      elements.toast.classList.remove('show');
    }, 3500);
  }

  async function request(path, options = {}) {
    const config = {
      method: options.method || 'GET',
      headers: { Accept: 'application/json', ...(options.headers || {}) },
    };

    if (options.body !== undefined) {
      config.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
      config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
    }

    try {
      const response = await fetch(`${API_BASE}${path}`, config);
      const contentType = response.headers.get('content-type') || '';
      const payload = contentType.includes('application/json') ? await response.json() : await response.text();
      if (!response.ok) {
        const detail = typeof payload === 'string' ? payload : payload?.detail;
        throw new Error(detail || `Request failed (${response.status})`);
      }
      return payload;
    } catch (error) {
      throw new Error(error.message || 'Network error');
    }
  }

  function toggleProductLoading(show) {
    if (!elements.productLoading || !elements.productGrid) return;
    elements.productLoading.style.display = show ? 'block' : 'none';
    elements.productGrid.setAttribute('aria-busy', show ? 'true' : 'false');
  }

  function toggleCartLoading(show) {
    if (!elements.cartLoading) return;
    elements.cartLoading.style.display = show ? 'block' : 'none';
  }

  function updateHeroStats() {
    const totalProducts = state.products.length;
    const averagePrice =
      totalProducts === 0 ? 0 : state.products.reduce((acc, product) => acc + product.price, 0) / totalProducts;
    const cartItems = state.cart?.total_items || 0;

    if (elements.heroStats.products) elements.heroStats.products.textContent = totalProducts || '0';
    if (elements.heroStats.avgPrice)
      elements.heroStats.avgPrice.textContent = totalProducts ? currencyFormatter.format(averagePrice) : '—';
    if (elements.heroStats.cart) elements.heroStats.cart.textContent = cartItems || '0';
  }

  function renderProducts() {
    if (!elements.productGrid) return;

    const query = state.search.trim().toLowerCase();
    let filtered = [...state.products];
    if (query) {
      filtered = filtered.filter(
        (product) =>
          product.name.toLowerCase().includes(query) ||
          (product.description || '').toLowerCase().includes(query),
      );
    }
    if (state.stockOnly) {
      filtered = filtered.filter((product) => product.in_stock > 0);
    }
    switch (state.sort) {
      case 'price-low':
        filtered.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        filtered.sort((a, b) => b.price - a.price);
        break;
      case 'stock-high':
        filtered.sort((a, b) => b.in_stock - a.in_stock);
        break;
      default:
        filtered.sort((a, b) => a.id - b.id);
    }
    state.filtered = filtered;

    elements.productGrid.innerHTML = '';
    filtered.forEach((product) => elements.productGrid.appendChild(createProductCard(product)));

    const hasProducts = filtered.length > 0;
    if (elements.productEmpty) elements.productEmpty.hidden = hasProducts;
    if (elements.productStatus) {
      if (state.products.length === 0) {
        elements.productStatus.textContent = 'No products available yet.';
      } else {
        elements.productStatus.textContent = `Showing ${filtered.length} of ${state.products.length} products.`;
      }
    }
  }

  function clampQuantity(value, max) {
    const numericMax = Number(max) || 1;
    const parsed = Number(value);
    if (Number.isNaN(parsed) || parsed < 1) return 1;
    return Math.min(parsed, numericMax);
  }

  function adjustQuantity(input, delta) {
    const max = Number(input.max) || 1;
    const next = clampQuantity((Number(input.value) || 1) + delta, max);
    input.value = next;
  }

  function createProductCard(product) {
    const card = document.createElement('article');
    card.className = 'product-card';

    const detailHref = `${API_BASE}/products/${product.id}/view`;
    const fallbackImage = 'assets/css/images/soccer.jpg';
    const resolvedImage =
      !product.image_url || product.image_url === ''
        ? fallbackImage
        : product.image_url.startsWith('http')
          ? product.image_url
          : `${API_BASE}${product.image_url}`;

    const imageLink = document.createElement('a');
    imageLink.href = detailHref;
    imageLink.className = 'product-card-media';
    const img = document.createElement('img');
    img.src = resolvedImage;
    img.alt = `${product.name} photo`;
    img.width = 150;
    img.height = 150;
    img.loading = 'lazy';
    img.onerror = () => {
      img.onerror = null;
      img.src = fallbackImage;
    };
    imageLink.appendChild(img);
    card.appendChild(imageLink);

    const titleLink = document.createElement('a');
    titleLink.href = detailHref;
    titleLink.className = 'product-card-title';
    const title = document.createElement('h3');
    title.textContent = product.name;
    titleLink.appendChild(title);
    card.appendChild(titleLink);

    const desc = document.createElement('p');
    desc.className = 'product-meta';
    desc.textContent = product.description || 'No description available yet.';
    card.appendChild(desc);

    const badges = document.createElement('p');
    badges.className = 'product-meta';
    const stockBadge = document.createElement('span');
    stockBadge.className = 'badge';
    if (product.in_stock === 0) {
      stockBadge.classList.add('badge--out');
      stockBadge.textContent = 'Out of stock';
    } else if (product.in_stock < 5) {
      stockBadge.classList.add('badge--low');
      stockBadge.textContent = `Low stock • ${product.in_stock} left`;
    } else {
      stockBadge.classList.add('badge--stock');
      stockBadge.textContent = `${product.in_stock} in stock`;
    }
    badges.appendChild(stockBadge);
    card.appendChild(badges);

    const price = document.createElement('p');
    price.className = 'product-price';
    price.textContent = currencyFormatter.format(product.price);
    card.appendChild(price);

    const controls = document.createElement('div');
    controls.className = 'product-controls';

    const qtyControl = document.createElement('div');
    qtyControl.className = 'quantity-control';

    const minus = document.createElement('button');
    minus.type = 'button';
    minus.className = 'quantity-btn';
    minus.textContent = '−';
    minus.addEventListener('click', () => adjustQuantity(qty, -1));

    const qty = document.createElement('input');
    qty.type = 'number';
    qty.min = 1;
    qty.step = 1;
    qty.value = 1;
    qty.className = 'quantity-input';
    qty.max = Math.max(product.in_stock, 1);
    qty.addEventListener('change', () => {
      qty.value = clampQuantity(qty.value, qty.max);
    });
    const plus = document.createElement('button');
    plus.type = 'button';
    plus.className = 'quantity-btn';
    plus.textContent = '+';
    plus.addEventListener('click', () => adjustQuantity(qty, 1));

    if (product.in_stock === 0) {
      qty.disabled = true;
      minus.disabled = true;
      plus.disabled = true;
      qtyControl.classList.add('disabled');
    }

    qtyControl.append(minus, qty, plus);
    controls.appendChild(qtyControl);

    const button = document.createElement('button');
    button.className = 'btn primary small';
    button.type = 'button';
    button.textContent = 'Add to cart';
    button.disabled = product.in_stock === 0;
    button.addEventListener('click', (event) => {
      event.preventDefault();
      const quantity = clampQuantity(qty.value, qty.max);
      addToCart(product, quantity, button);
    });
    controls.appendChild(button);

    card.appendChild(controls);
    return card;
  }

  async function addToCart(product, quantity, button) {
    if (!product) return;
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Adding…';
    try {
      await request('/cart', {
        method: 'POST',
        body: { product_id: product.id, quantity },
      });
      await loadCart({ silent: true });
      await loadProducts({ silent: true });
      showToast(`Added ${quantity} × ${product.name}`);
    } catch (error) {
      showToast(error.message, 'error');
      if (elements.cartMessage) elements.cartMessage.textContent = error.message;
    } finally {
      button.disabled = product.in_stock === 0;
      button.textContent = originalText;
    }
  }

  function renderCart() {
    if (!elements.cartItems) return;
    elements.cartItems.innerHTML = '';
    const items = state.cart?.items || [];
    if (elements.floatingCart) elements.floatingCart.hidden = items.length === 0;

    if (items.length === 0) {
      if (elements.cartEmpty) elements.cartEmpty.hidden = false;
    } else {
      if (elements.cartEmpty) elements.cartEmpty.hidden = true;
      items.forEach((item) => elements.cartItems.appendChild(createCartItem(item)));
    }

    if (elements.cartTotalItems) elements.cartTotalItems.textContent = state.cart?.total_items || 0;
    if (elements.cartGrandTotal)
      elements.cartGrandTotal.textContent = currencyFormatter.format(state.cart?.grand_total || 0);
    if (elements.checkout) elements.checkout.disabled = items.length === 0;
    if (elements.clearCart) elements.clearCart.disabled = items.length === 0;
  }

  function createCartItem(item) {
    const li = document.createElement('li');
    li.className = 'cart-item';

    const info = document.createElement('div');
    const title = document.createElement('strong');
    title.textContent = item.product.name;
    info.appendChild(title);

    const meta = document.createElement('p');
    meta.className = 'muted';
    meta.textContent = `${item.quantity} × ${currencyFormatter.format(item.product.price)}`;
    info.appendChild(meta);
    li.appendChild(info);

    const actions = document.createElement('div');
    actions.className = 'cart-item-actions';
    const total = document.createElement('span');
    total.textContent = currencyFormatter.format(item.line_total);
    actions.appendChild(total);

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn ghost small';
    removeBtn.type = 'button';
    removeBtn.textContent = 'Remove';
    removeBtn.addEventListener('click', () => removeFromCart(item.product.id, removeBtn));
    actions.appendChild(removeBtn);

    li.appendChild(actions);
    return li;
  }

  async function removeFromCart(productId, button) {
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Removing…';
    try {
      await request(`/cart/${productId}`, { method: 'DELETE' });
      await loadCart({ silent: true });
      await loadProducts({ silent: true });
      showToast('Item removed');
    } catch (error) {
      showToast(error.message, 'error');
      if (elements.cartMessage) elements.cartMessage.textContent = error.message;
    } finally {
      button.disabled = false;
      button.textContent = originalText;
    }
  }

  async function clearCart() {
    const clearButton = elements.clearCart;
    if (!clearButton || !state.cart?.items?.length) return;
    clearButton.disabled = true;
    try {
      await request('/cart', { method: 'DELETE' });
      await loadCart({ silent: true });
      await loadProducts({ silent: true });
      showToast('Cart cleared');
    } catch (error) {
      showToast(error.message, 'error');
      if (elements.cartMessage) elements.cartMessage.textContent = error.message;
    } finally {
      clearButton.disabled = false;
    }
  }

  async function loadProducts({ silent = false } = {}) {
    if (!silent) toggleProductLoading(true);
    if (!silent && elements.productStatus) elements.productStatus.textContent = 'Loading catalog...';
    try {
      state.products = await request('/products');
      renderProducts();
      updateHeroStats();
    } catch (error) {
      if (elements.productStatus) elements.productStatus.textContent = error.message;
      showToast(error.message, 'error');
    } finally {
      if (!silent) toggleProductLoading(false);
    }
  }

  async function loadCart({ silent = false } = {}) {
    if (!silent) toggleCartLoading(true);
    if (elements.cartMessage) elements.cartMessage.textContent = '';
    try {
      state.cart = await request('/cart');
      renderCart();
      updateHeroStats();
    } catch (error) {
      if (elements.cartMessage) elements.cartMessage.textContent = error.message;
      showToast(error.message, 'error');
    } finally {
      if (!silent) toggleCartLoading(false);
    }
  }

  function setupEventListeners() {
    if (elements.productSearch) {
      elements.productSearch.addEventListener('input', (event) => {
        state.search = event.target.value || '';
        renderProducts();
      });
    }
    if (elements.productSort) {
      elements.productSort.addEventListener('change', (event) => {
        state.sort = event.target.value;
        renderProducts();
      });
    }
    if (elements.productFilterStock) {
      elements.productFilterStock.addEventListener('change', (event) => {
        state.stockOnly = event.target.checked;
        renderProducts();
      });
    }
    document.querySelectorAll('[data-scroll-target]').forEach((btn) => {
      btn.addEventListener('click', (event) => {
        const target = document.getElementById(btn.dataset.scrollTarget);
        if (target) {
          event.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
    if (elements.clearCart) {
      elements.clearCart.addEventListener('click', clearCart);
    }
    if (elements.checkout) {
      elements.checkout.addEventListener('click', onCheckout);
    }
  }

  function onCheckout() {
    if (!state.cart?.items?.length) return;
    window.location.assign(`${API_BASE}/checkout`);
  }

  async function init() {
    wireExternalLinks();
    setupEventListeners();
    await Promise.all([loadProducts(), loadCart()]);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
