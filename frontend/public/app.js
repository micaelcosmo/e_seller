// Storefront e_seller — SPA leve (sem build). Consome a API na mesma origem.
// Código em inglês; comentários em pt-BR.

const API = "/api/v1";
const view = document.getElementById("view");
const hero = document.getElementById("hero");

// ---------- Utilitários ----------

function money(value) {
  // Formata um valor decimal (string) em reais.
  return "R$ " + Number(value).toFixed(2).replace(".", ",");
}

function toast(message, kind) {
  // Mostra uma notificação temporária (sucesso/erro/neutra).
  const box = document.getElementById("toasts");
  const el = document.createElement("div");
  el.className = "toast " + (kind || "");
  el.textContent = message;
  box.appendChild(el);
  setTimeout(function () { el.remove(); }, 3200);
}

async function tryRefreshToken() {
  // Renova a sessão usando o refresh_token salvo no localStorage.
  // Retorna true se bem-sucedido; false se o refresh falhou (sessão encerrada).
  const rt = localStorage.getItem("refresh_token");
  if (!rt) { return false; }
  try {
    const resp = await fetch(API + "/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!resp.ok) {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("email");
      return false;
    }
    const tok = await resp.json();
    localStorage.setItem("token", tok.access_token);
    localStorage.setItem("refresh_token", tok.refresh_token);
    return true;
  } catch (e) {
    return false;
  }
}

async function api(path, options) {
  // Wrapper de fetch que injeta o token e trata JSON/erros.
  // Em caso de 401 tenta renovar o token uma vez via refresh_token.
  const opts = options || {};
  opts.headers = opts.headers || {};
  const token = localStorage.getItem("token");
  if (token) { opts.headers["Authorization"] = "Bearer " + token; }
  let resp = await fetch(API + path, opts);
  if (resp.status === 401 && localStorage.getItem("refresh_token")) {
    const renewed = await tryRefreshToken();
    if (renewed) {
      opts.headers["Authorization"] = "Bearer " + localStorage.getItem("token");
      resp = await fetch(API + path, opts);
    }
  }
  let data = null;
  try { data = await resp.json(); } catch (e) { data = null; }
  if (!resp.ok) {
    const detail = data && data.detail ? data.detail : "Erro";
    throw new Error(typeof detail === "string" ? detail : "Erro");
  }
  return data;
}

// ---------- Renderização ----------

function skeleton() {
  // Placeholder de carregamento (cards "fantasma").
  let html = '<div class="skeleton">';
  for (let i = 0; i < 6; i++) { html += '<div class="sk"></div>'; }
  return html + "</div>";
}

function coverHtml(p, emoji) {
  // Renderiza a capa do produto: imagem (se houver cover_url) ou emoji.
  if (p.cover_url) {
    return '<div class="cover"><img src="' + escapeHtml(p.cover_url) +
      '" alt="Capa de ' + escapeHtml(p.title) + '" loading="lazy"></div>';
  }
  return '<div class="cover">' + emoji + "</div>";
}

// Slugs na wishlist do usuário logado (Set atualizado por renderHome).
const _wishSlugs = new Set();
// Slugs de produtos já comprados (Set atualizado por renderHome e renderProduct).
const _ownedSlugs = new Set();

function productCard(p, isOwned) {
  // HTML de um cartão de produto; isOwned exibe o badge "Comprado".
  const badge = isOwned
    ? '<span class="badge-owned">Comprado</span>'
    : "";
  const inWish = _wishSlugs.has(p.slug);
  const wishBtn = localStorage.getItem("token")
    ? '<button class="btn-wish' + (inWish ? " wished" : "") +
      '" data-slug="' + escapeHtml(p.slug) + '" title="' +
      (inWish ? "Remover da wishlist" : "Adicionar à wishlist") + '">' +
      (inWish ? "♥" : "♡") + "</button>"
    : "";
  return (
    '<a class="card" href="#/produto/' + p.slug + '" title="Ver detalhes">' +
    badge + wishBtn + coverHtml(p, "📕") + '<div class="body">' +
    '<span class="tag">' + (p.author || "e-book") + "</span>" +
    "<h3>" + escapeHtml(p.title) + "</h3>" +
    '<div class="price">' + money(p.price) + "</div></div></a>"
  );
}

function escapeHtml(text) {
  // Evita injeção de HTML ao renderizar dados do servidor.
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}

// ---------- Facetas de navegação (tags e autores) — FE-13 ----------

const _facets = { tags: [], authors: [] };

async function loadFacets() {
  // Carrega tags e autores uma única vez na inicialização.
  try {
    const results = await Promise.all([api("/tags"), api("/authors")]);
    _facets.tags = results[0];
    _facets.authors = results[1];
  } catch (e) { /* facetas são opcionais; falha silenciosa */ }
}

function facetBar(activeTag, authorSlug) {
  // Renderiza a barra de chips de filtragem por tag/autor com contagem de produtos.
  if (!_facets.tags.length && !_facets.authors.length) { return ""; }
  let html = '<div class="facets">';
  for (const t of _facets.tags) {
    const active = t.slug === activeTag ? " active" : "";
    const badge = t.count > 0 ? ' <span class="chip-count">' + t.count + "</span>" : "";
    html += '<button class="chip-btn' + active + '" data-tag="' + escapeHtml(t.slug) + '"' +
      ' title="Filtrar por tema: ' + escapeHtml(t.name) + '">' +
      escapeHtml(t.name) + badge + '</button>';
  }
  for (const a of _facets.authors) {
    const active = a.slug === authorSlug ? " active" : "";
    const badge = a.count > 0 ? ' <span class="chip-count">' + a.count + "</span>" : "";
    html += '<button class="chip-btn' + active + '" data-author="' + escapeHtml(a.slug) + '"' +
      ' title="Filtrar por autor: ' + escapeHtml(a.name) + '">' +
      escapeHtml(a.name) + badge + '</button>';
  }
  if (activeTag || authorSlug) {
    html += '<button class="chip-btn clear" title="Remover filtro">✕ Limpar filtro</button>';
  }
  return html + '</div>';
}

function bindFacetChips(query, activeTag, authorSlug, activeSort) {
  // Liga os eventos de clique nos chips de faceta após renderização.
  const chips = view.querySelectorAll(".chip-btn");
  for (const c of chips) {
    c.addEventListener("click", function () {
      if (c.classList.contains("clear")) {
        renderHome(null, null, null, 1, activeSort);
      } else if (c.getAttribute("data-tag")) {
        const slug = c.getAttribute("data-tag");
        renderHome(null, slug === activeTag ? null : slug, null, 1, activeSort);
      } else if (c.getAttribute("data-author")) {
        const slug = c.getAttribute("data-author");
        renderHome(null, null, slug === authorSlug ? null : slug, 1, activeSort);
      }
    });
  }
}

const _PAGE_SIZE = 12;

function sortBar(activeSort) {
  // Renderiza o seletor de ordenação do catálogo.
  const opts = [
    { value: "newest", label: "Mais recentes" },
    { value: "price_asc", label: "Menor preço" },
    { value: "price_desc", label: "Maior preço" },
    { value: "title_asc", label: "A–Z" },
  ];
  let options = "";
  for (const o of opts) {
    options += '<option value="' + o.value + '"' +
      (o.value === activeSort ? " selected" : "") + ">" +
      o.label + "</option>";
  }
  return '<div class="sort-bar"><label for="sort-select">Ordenar por:</label>' +
    '<select id="sort-select" title="Ordenar produtos">' + options + "</select></div>";
}

function bindWishlistButtons() {
  // Liga os botões de wishlist (coração) nos cards após renderização.
  const btns = view.querySelectorAll(".btn-wish");
  for (const btn of btns) {
    btn.addEventListener("click", function (evt) {
      evt.preventDefault();
      evt.stopPropagation();
      toggleWish(btn);
    });
  }
}

async function toggleWish(btn) {
  // Adiciona ou remove o produto da wishlist, atualizando o botão imediatamente.
  const slug = btn.getAttribute("data-slug");
  const inWish = _wishSlugs.has(slug);
  try {
    if (inWish) {
      await api("/wishlist/" + slug, { method: "DELETE" });
      _wishSlugs.delete(slug);
      btn.textContent = "♡";
      btn.classList.remove("wished");
      btn.title = "Adicionar à wishlist";
    } else {
      await api("/wishlist/" + slug, { method: "POST" });
      _wishSlugs.add(slug);
      btn.textContent = "♥";
      btn.classList.add("wished");
      btn.title = "Remover da wishlist";
    }
  } catch (e) {
    toast(e.message, "err");
  }
}

async function renderHome(query, tagSlug, authorSlug, page, sort) {
  // Lista produtos com paginação, busca, filtros de faceta e ordenação.
  // page=1 limpa a lista; page>1 acrescenta (botão "Carregar mais").
  const currentPage = page || 1;
  const activeSort = sort || "newest";
  hero.classList.toggle("hidden", Boolean(query || tagSlug || authorSlug));
  if (currentPage === 1) { view.innerHTML = skeleton(); }
  const searchEl = document.getElementById("search-input");
  if (searchEl) { searchEl.classList.add("is-busy"); }
  try {
    const params = new URLSearchParams();
    if (query) { params.set("q", query); }
    if (tagSlug) { params.set("tag", tagSlug); }
    if (authorSlug) { params.set("author", authorSlug); }
    params.set("sort", activeSort);
    params.set("page", currentPage);
    params.set("page_size", _PAGE_SIZE);
    const qs = "?" + params.toString();
    const [products, countData] = await Promise.all([
      api("/products" + qs),
      api("/products/count" + qs),
    ]);
    // Carrega slugs de produtos já comprados e wishlist do usuário logado.
    _ownedSlugs.clear();
    _wishSlugs.clear();
    if (localStorage.getItem("token")) {
      const [lib, wish] = await Promise.all([
        api("/library").catch(function () { return []; }),
        api("/wishlist").catch(function () { return []; }),
      ]);
      for (const item of lib) { _ownedSlugs.add(item.slug); }
      for (const item of wish) { _wishSlugs.add(item.slug); }
    }
    if (currentPage === 1) {
      let html = facetBar(tagSlug, authorSlug);
      html += sortBar(activeSort);
      if (!products.length) {
        html += '<div class="empty">Nenhum e-book encontrado.</div>';
      } else {
        html += '<div class="grid" id="product-grid">';
        for (const p of products) { html += productCard(p, _ownedSlugs.has(p.slug)); }
        html += "</div>";
      }
      view.innerHTML = html;
      const sel = document.getElementById("sort-select");
      if (sel) {
        sel.addEventListener("change", function () {
          renderHome(query, tagSlug, authorSlug, 1, sel.value);
        });
      }
    } else {
      const grid = document.getElementById("product-grid");
      if (grid) {
        for (const p of products) {
          grid.insertAdjacentHTML("beforeend", productCard(p, _ownedSlugs.has(p.slug)));
        }
      }
    }
    // Remove botão anterior de "Carregar mais" antes de (re)inserir.
    const oldBtn = document.getElementById("load-more-btn");
    if (oldBtn) { oldBtn.remove(); }
    if (countData.has_next) {
      const btn = document.createElement("button");
      btn.id = "load-more-btn";
      btn.className = "btn-load-more";
      btn.textContent = "Carregar mais";
      btn.addEventListener("click", function () {
        renderHome(query, tagSlug, authorSlug, currentPage + 1, activeSort);
      });
      view.appendChild(btn);
    }
    bindFacetChips(query, tagSlug, authorSlug, activeSort);
    bindWishlistButtons();
  } catch (e) {
    view.innerHTML = '<div class="empty">Não foi possível carregar o catálogo.</div>';
    toast(e.message, "err");
  } finally {
    if (searchEl) { searchEl.classList.remove("is-busy"); }
  }
}

function updateProductMeta(p) {
  // Atualiza as meta tags OG/title para SEO na página de detalhes do produto.
  document.title = escapeHtml(p.title) + " — e_seller";
  const metas = {
    "og:title": escapeHtml(p.title) + " — e_seller",
    "og:description": escapeHtml(p.description || p.title),
    "og:type": "product",
  };
  for (const prop in metas) {
    const el = document.querySelector('meta[property="' + prop + '"]');
    if (el) { el.setAttribute("content", metas[prop]); }
  }
  const desc = document.querySelector('meta[name="description"]');
  if (desc) { desc.setAttribute("content", escapeHtml(p.description || p.title)); }
}

async function renderProduct(slug) {
  // Detalhe do produto + caixa de compra (ou botão de download se já comprado).
  hero.classList.add("hidden");
  view.innerHTML = '<div class="loading">Carregando…</div>';
  try {
    const p = await api("/products/" + slug);
    updateProductMeta(p);
    // Verifica propriedade: carrega biblioteca se logado e _ownedSlugs está vazio.
    if (localStorage.getItem("token") && !_ownedSlugs.size) {
      const lib = await api("/library").catch(function () { return []; });
      for (const item of lib) { _ownedSlugs.add(item.slug); }
    }
    const isOwned = _ownedSlugs.has(slug);
    const actionBox = isOwned
      ? '<div class="buy-box">' +
        '<p style="color:#15a05a;font-weight:700;margin:0 0 10px">✓ Você já possui este e-book</p>' +
        '<a class="btn primary" href="#/biblioteca" title="Ir para sua biblioteca">📚 Ir para a biblioteca</a>' +
        '</div>'
      : '<div class="buy-box"><strong>Comprar agora</strong>' +
        '<input id="buy-email" type="email" placeholder="seu@email.com" ' +
        'title="E-mail para receber o acesso">' +
        '<input id="buy-coupon" type="text" placeholder="Cupom (opcional) — ex.: BEMVINDO10" ' +
        'title="Código de cupom de desconto" autocomplete="off">' +
        '<div id="coupon-feedback" class="coupon-feedback hidden"></div>' +
        '<button class="primary" id="buy-btn" title="Ir para o pagamento">Comprar e baixar</button> ' +
        '<button class="ghost" id="cart-add-btn" title="Adicionar ao carrinho">🛒 Carrinho</button>' +
        '</div>';
    view.innerHTML =
      '<a class="back" href="#/">← Voltar</a>' +
      '<div class="detail">' + coverHtml(p, "📘") + "<div>" +
      '<span class="tag">' + escapeHtml(p.author || "e-book") + "</span>" +
      "<h2>" + escapeHtml(p.title) + "</h2>" +
      '<p class="muted">' + escapeHtml(p.description || "") + "</p>" +
      '<div class="price" style="font-size:1.4rem">' + money(p.price) + "</div>" +
      tagChips(p.tags) +
      actionBox +
      '</div></div><div id="reviews" class="reviews"></div>' +
      '<div id="related"></div>';
    if (!isOwned) {
      document.getElementById("buy-btn").addEventListener("click", function () {
        buy(slug);
      });
      document.getElementById("cart-add-btn").addEventListener("click", function () {
        addToCart(slug);
      });
      bindCouponValidation(p.price);
    }
    loadReviews(slug);
    loadRelated(slug);
  } catch (e) {
    view.innerHTML = '<div class="empty">Produto não encontrado.</div>';
  }
}

function tagChips(tags) {
  // Renderiza as tags do e-book como "chips" (vazio se não houver).
  if (!tags || !tags.length) { return ""; }
  let chips = "";
  for (const t of tags) {
    chips += '<span class="chip" title="Tema: ' + escapeHtml(t.name) + '">' +
      escapeHtml(t.name) + "</span>";
  }
  return '<div class="chips">' + chips + "</div>";
}

function stars(rating) {
  // Renderiza a nota como estrelas cheias/vazias.
  let out = "";
  for (let i = 1; i <= 5; i++) { out += i <= rating ? "★" : "☆"; }
  return out;
}

function bindCouponValidation(basePrice) {
  // Valida o cupom em tempo real com debounce de 500ms; mostra desconto ou erro.
  const input = document.getElementById("buy-coupon");
  const feedback = document.getElementById("coupon-feedback");
  if (!input || !feedback) { return; }
  let timer = null;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    const code = input.value.trim().toUpperCase();
    if (!code) { feedback.textContent = ""; feedback.className = "coupon-feedback hidden"; return; }
    timer = setTimeout(async function () {
      try {
        const result = await api("/coupons/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: code, amount: String(basePrice) }),
        });
        feedback.textContent = "✓ Cupom válido — total: " + money(result.total) + " (desconto: " + money(result.discount) + ")";
        feedback.className = "coupon-feedback ok";
      } catch (e) {
        feedback.textContent = "✗ Cupom inválido ou expirado.";
        feedback.className = "coupon-feedback err";
      }
      feedback.classList.remove("hidden");
    }, 500);
  });
}

async function loadReviews(slug) {
  // Carrega e renderiza as avaliações do produto, com formulário se logado.
  const box = document.getElementById("reviews");
  if (!box) { return; }
  box.innerHTML = "<h3>Avaliações</h3>";
  try {
    const list = await api("/products/" + slug + "/reviews");
    if (!list.length) { box.innerHTML += '<p class="muted">Ainda sem avaliações.</p>'; }
    for (const r of list) {
      box.innerHTML +=
        '<div class="review"><span class="rt">' + stars(r.rating) + "</span> " +
        "<strong>" + escapeHtml(r.author) + "</strong>" +
        '<p class="muted">' + escapeHtml(r.comment) + "</p></div>";
    }
  } catch (e) { /* silencioso */ }
  if (localStorage.getItem("token")) {
    box.innerHTML +=
      '<div class="review-form"><select id="rev-rating" title="Sua nota">' +
      '<option value="5">★★★★★</option><option value="4">★★★★</option>' +
      '<option value="3">★★★</option><option value="2">★★</option><option value="1">★</option>' +
      '</select><input id="rev-comment" placeholder="Seu comentário (opcional)" ' +
      'title="Comente sobre o e-book"><button class="ghost" id="rev-send" ' +
      'title="Enviar avaliação (só quem comprou)">Avaliar</button></div>';
    document.getElementById("rev-send").addEventListener("click", function () {
      submitReview(slug);
    });
  }
}

async function loadRelated(slug) {
  // Carrega e renderiza produtos relacionados ao e-book atual (mesmo autor/tag).
  const box = document.getElementById("related");
  if (!box) { return; }
  try {
    const list = await api("/products/" + slug + "/related");
    if (!list.length) { return; }
    let cards = "";
    for (const p of list) { cards += productCard(p, false); }
    box.innerHTML =
      '<h3 class="related-title">Você também pode gostar</h3>' +
      '<div class="related-grid">' + cards + "</div>";
  } catch (e) { /* silencioso — relacionados são opcionais */ }
}

async function submitReview(slug) {
  // Envia a avaliação (apenas comprador verificado).
  const rating = Number(document.getElementById("rev-rating").value);
  const comment = document.getElementById("rev-comment").value || "";
  try {
    await api("/products/" + slug + "/reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rating: rating, comment: comment }),
    });
    toast("Avaliação enviada!", "ok");
    loadReviews(slug);
  } catch (e) {
    toast(e.message, "err");
  }
}

async function buy(slug) {
  // Cria o pedido e leva ao pagamento (página same-origin, via proxy).
  const email = (document.getElementById("buy-email").value || "").trim();
  const coupon = (document.getElementById("buy-coupon").value || "").trim();
  const btn = document.getElementById("buy-btn");
  if (!email || email.indexOf("@") < 0) { toast("Informe um e-mail válido.", "err"); return; }
  btn.disabled = true; btn.textContent = "Processando…";
  try {
    const payload = { product_slug: slug, buyer_email: email };
    if (coupon) { payload.coupon_code = coupon; }
    const order = await api("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    // Navega para a lista de pedidos; o botão "Pagar" na order-card completa o pagamento.
    toast("Pedido criado! Clique em Pagar para concluir.", "ok");
    location.hash = "#/pedidos";
  } catch (e) {
    toast(e.message, "err");
    btn.disabled = false; btn.textContent = "Comprar e baixar";
  }
}

// ---------- Conta / Perfil fiscal — FE-12 ----------

async function renderAccount() {
  // Exibe o formulário de perfil fiscal (dados de cobrança) do usuário logado.
  hero.classList.add("hidden");
  if (!localStorage.getItem("token")) {
    view.innerHTML = '<div class="empty">Entre para ver a sua conta.</div>';
    return;
  }
  view.innerHTML = '<div class="loading">Carregando perfil…</div>';
  let profile = {};
  try {
    profile = (await api("/billing/profile")) || {};
  } catch (e) { /* perfil ainda não criado — exibe formulário vazio */ }
  const pt = profile.person_type || "PF";
  view.innerHTML =
    '<a class="back" href="#/">← Voltar</a>' +
    '<h2 style="margin:8px 0 16px">Minha Conta</h2>' +
    '<a href="#/pedidos" class="btn ghost" style="display:inline-block;margin-bottom:16px" title="Ver meus pedidos">🧾 Meus Pedidos</a>' +
    '<form id="account-form" class="form account-form">' +
    '<label class="field-label">Tipo de pessoa' +
    '<select name="person_type" title="Pessoa Física ou Jurídica">' +
    '<option value="PF"' + (pt !== "PJ" ? " selected" : "") + '>Pessoa Física (CPF)</option>' +
    '<option value="PJ"' + (pt === "PJ" ? " selected" : "") + '>Pessoa Jurídica (CNPJ)</option>' +
    '</select></label>' +
    '<input name="legal_name" type="text" placeholder="Nome completo ou Razão Social" required ' +
    'value="' + escapeHtml(profile.legal_name || "") + '" title="Nome completo ou razão social">' +
    '<input name="document" type="text" placeholder="CPF (000.000.000-00) ou CNPJ" required ' +
    'value="' + escapeHtml(profile.document || "") + '" title="CPF ou CNPJ">' +
    '<input name="address_line" type="text" placeholder="Logradouro, número, complemento" ' +
    'value="' + escapeHtml(profile.address_line || "") + '" title="Endereço completo">' +
    '<div class="form-row">' +
    '<input name="city" type="text" placeholder="Cidade" ' +
    'value="' + escapeHtml(profile.city || "") + '" title="Cidade">' +
    '<input name="state" type="text" placeholder="UF" maxlength="2" style="max-width:70px" ' +
    'value="' + escapeHtml(profile.state || "") + '" title="Sigla do estado (ex.: SP)">' +
    '</div>' +
    '<div class="form-row">' +
    '<input name="postal_code" type="text" placeholder="CEP" ' +
    'value="' + escapeHtml(profile.postal_code || "") + '" title="CEP (00000-000)">' +
    '<input name="country" type="text" placeholder="País" ' +
    'value="' + escapeHtml(profile.country || "BR") + '" title="País (ex.: BR)">' +
    '</div>' +
    '<button class="primary" type="submit" title="Salvar perfil fiscal">Salvar perfil</button>' +
    '</form>';
  document.getElementById("account-form").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    const fd = new FormData(ev.currentTarget);
    const payload = {};
    for (const entry of fd.entries()) {
      payload[entry[0]] = entry[1];
    }
    try {
      await api("/billing/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      toast("Perfil salvo!", "ok");
    } catch (e) {
      toast(e.message, "err");
    }
  });
}

// ---------- Autenticação ----------

function refreshAuthButton() {
  // Mostra "Entrar" ou o e-mail logado; exibe botões de Biblioteca/Carrinho/Conta quando logado.
  const btn = document.getElementById("auth-btn");
  const lib = document.getElementById("lib-btn");
  const cart = document.getElementById("cart-btn");
  const account = document.getElementById("account-btn");
  const ordersBtn = document.getElementById("orders-btn");
  const email = localStorage.getItem("email");
  if (email) { btn.textContent = "Sair (" + email.split("@")[0] + ")"; btn.title = "Sair da conta"; }
  else { btn.textContent = "Entrar"; btn.title = "Entrar ou criar conta"; }
  lib.classList.toggle("hidden", !email);
  cart.classList.toggle("hidden", !email);
  account.classList.toggle("hidden", !email);
  ordersBtn.classList.toggle("hidden", !email);
}

async function addToCart(slug) {
  // Adiciona um e-book ao carrinho (exige login).
  if (!localStorage.getItem("token")) { document.getElementById("auth-modal").classList.remove("hidden"); return; }
  try {
    await api("/cart/" + slug, { method: "POST" });
    toast("Adicionado ao carrinho!", "ok");
  } catch (e) { toast(e.message, "err"); }
}

async function renderCart() {
  // Mostra o carrinho com total e botão de finalizar.
  hero.classList.add("hidden");
  if (!localStorage.getItem("token")) {
    view.innerHTML = '<div class="empty">Entre para usar o carrinho.</div>'; return;
  }
  view.innerHTML = '<div class="loading">Carregando carrinho…</div>';
  try {
    const items = await api("/cart");
    if (!items.length) { view.innerHTML = '<div class="empty">Seu carrinho está vazio.</div>'; return; }
    let total = 0;
    let html = '<h2 style="margin:8px 0 16px">🛒 Seu carrinho</h2><div class="grid">';
    for (const p of items) {
      total += Number(p.price);
      html += '<div class="card"><div class="cover">📕</div><div class="body">' +
        "<h3>" + escapeHtml(p.title) + "</h3>" +
        '<div class="price">' + money(p.price) + "</div>" +
        '<button class="ghost" data-rm="' + p.slug + '" title="Remover">Remover</button>' +
        "</div></div>";
    }
    html += "</div>";
    html += '<div class="buy-box" style="margin-top:18px"><strong>Total: ' + money(total) + "</strong>" +
      '<input id="cart-coupon" type="text" placeholder="Cupom (opcional)" title="Cupom de desconto">' +
      '<button class="primary" id="cart-checkout" title="Ir para o pagamento">Finalizar compra</button></div>';
    view.innerHTML = html;
    const rm = view.querySelectorAll("button[data-rm]");
    for (const b of rm) {
      b.addEventListener("click", async function () {
        await api("/cart/" + b.getAttribute("data-rm"), { method: "DELETE" });
        renderCart();
      });
    }
    document.getElementById("cart-checkout").addEventListener("click", cartCheckout);
  } catch (e) {
    view.innerHTML = '<div class="empty">Não foi possível carregar o carrinho.</div>';
  }
}

async function cartCheckout() {
  // Finaliza o carrinho e vai ao pagamento.
  const coupon = (document.getElementById("cart-coupon").value || "").trim();
  const btn = document.getElementById("cart-checkout");
  btn.disabled = true; btn.textContent = "Processando…";
  try {
    const body = coupon ? { coupon_code: coupon } : {};
    const order = await api("/cart/checkout", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    window.location.href = "/pay/simulate/" + order.reference;
  } catch (e) {
    toast(e.message, "err"); btn.disabled = false; btn.textContent = "Finalizar compra";
  }
}

async function renderLibrary() {
  // Lista os e-books que o usuário possui, com botão de baixar.
  hero.classList.add("hidden");
  if (!localStorage.getItem("token")) {
    view.innerHTML = '<div class="empty">Entre na sua conta para ver a biblioteca.</div>';
    return;
  }
  view.innerHTML = '<div class="loading">Carregando sua biblioteca…</div>';
  try {
    const items = await api("/library");
    if (!items.length) {
      view.innerHTML = '<div class="empty">Você ainda não comprou nenhum e-book.</div>';
      return;
    }
    let html = '<h2 style="margin:8px 0 16px">📚 Minha Biblioteca</h2><div class="grid">';
    for (const p of items) {
      html +=
        '<div class="card"><div class="cover">📗</div><div class="body">' +
        '<span class="tag">' + escapeHtml(p.author || "e-book") + "</span>" +
        "<h3>" + escapeHtml(p.title) + "</h3>" +
        '<button class="primary" data-slug="' + p.slug + '" title="Baixar o arquivo">⬇️ Baixar</button>' +
        "</div></div>";
    }
    view.innerHTML = html + "</div>";
    const buttons = view.querySelectorAll("button[data-slug]");
    for (const b of buttons) {
      b.addEventListener("click", function () { downloadOwned(b.getAttribute("data-slug")); });
    }
  } catch (e) {
    view.innerHTML = '<div class="empty">Não foi possível carregar a biblioteca.</div>';
    toast(e.message, "err");
  }
}

async function renderOrders() {
  // Lista os pedidos do usuário autenticado via GET /api/v1/orders/my.
  hero.classList.add("hidden");
  if (!localStorage.getItem("token")) {
    view.innerHTML = '<div class="empty">Entre na sua conta para ver seus pedidos.</div>';
    return;
  }
  view.innerHTML = '<div class="loading">Carregando seus pedidos…</div>';
  try {
    const orders = await api("/orders/my");
    if (!orders.length) {
      view.innerHTML = '<div class="empty">Você ainda não fez nenhum pedido.</div>';
      return;
    }
    let html = '<h2 style="margin:8px 0 16px">🧾 Meus Pedidos</h2>';
    html += '<div class="orders-list">';
    for (const o of orders) {
      const statusLabel = {
        pending: "Pendente", paid: "Pago", failed: "Falhou",
        cancelled: "Cancelado", refunded: "Reembolsado",
      }[o.status] || o.status;
      const statusClass = o.status === "paid" ? "ok" : (o.status === "failed" || o.status === "cancelled" ? "err" : "");
      html +=
        '<div class="order-card">' +
        '<div class="order-ref">#' + escapeHtml(o.reference) + "</div>" +
        '<span class="order-status ' + statusClass + '">' + statusLabel + "</span>" +
        '<div class="order-amount">' + money(o.amount) + "</div>" +
        (o.checkout_url && o.status === "pending"
          ? '<a class="btn primary" href="' + escapeHtml(o.checkout_url) + '" target="_blank">Pagar</a>'
          : "") +
        "</div>";
    }
    html += "</div>";
    view.innerHTML = html;
  } catch (e) {
    view.innerHTML = '<div class="empty">Não foi possível carregar seus pedidos.</div>';
    toast(e.message, "err");
  }
}

async function downloadOwned(slug) {
  // Reemite um link de download e baixa o arquivo.
  try {
    const link = await api("/library/" + slug + "/download-link", { method: "POST" });
    window.location.href = link.url;
  } catch (e) {
    toast(e.message, "err");
  }
}

function setupAuth() {
  // Liga os eventos do modal de login/registro.
  const modal = document.getElementById("auth-modal");
  const form = document.getElementById("auth-form");
  const submit = document.getElementById("auth-submit");
  const regName = document.getElementById("reg-name");
  let mode = "login";

  document.getElementById("auth-btn").addEventListener("click", function () {
    if (localStorage.getItem("email")) {
      localStorage.removeItem("token"); localStorage.removeItem("refresh_token"); localStorage.removeItem("email"); refreshAuthButton(); toast("Você saiu da conta.", "ok"); return;
    }
    modal.classList.remove("hidden");
  });
  document.getElementById("auth-close").addEventListener("click", function () {
    modal.classList.add("hidden");
  });
  const errorDiv = document.getElementById("auth-error");
  const privacyNote = document.getElementById("auth-privacy");

  function showAuthError(msg) {
    // Exibe mensagem de erro no painel de validação do form de auth.
    errorDiv.textContent = msg;
    errorDiv.classList.remove("hidden");
  }
  function clearAuthError() {
    // Limpa o painel de erro.
    errorDiv.textContent = "";
    errorDiv.classList.add("hidden");
  }

  const tabs = document.querySelectorAll(".tab");
  for (const tab of tabs) {
    tab.addEventListener("click", function () {
      for (const t of tabs) { t.classList.remove("active"); }
      tab.classList.add("active");
      mode = tab.getAttribute("data-tab");
      regName.classList.toggle("hidden", mode !== "register");
      privacyNote.classList.toggle("hidden", mode !== "register");
      submit.textContent = mode === "register" ? "Criar conta" : "Entrar";
      clearAuthError();
    });
  }
  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    clearAuthError();
    const fd = new FormData(form);
    const email = fd.get("email");
    const password = fd.get("password");
    if (!email || !email.includes("@")) {
      showAuthError("Informe um e-mail válido.");
      return;
    }
    if (!password || password.length < 6) {
      showAuthError("A senha deve ter pelo menos 6 caracteres.");
      return;
    }
    submit.disabled = true;
    try {
      if (mode === "register") {
        await api("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email, password: password, full_name: fd.get("full_name") || "" }),
        });
      }
      const body = new URLSearchParams({ username: email, password: password });
      const tok = await api("/auth/token", { method: "POST", body: body });
      localStorage.setItem("token", tok.access_token);
      localStorage.setItem("refresh_token", tok.refresh_token);
      localStorage.setItem("email", email);
      modal.classList.add("hidden"); refreshAuthButton();
      toast("Bem-vindo!", "ok");
    } catch (e) {
      showAuthError(e.message);
    } finally {
      submit.disabled = false;
    }
  });
}

// ---------- Roteamento ----------

function render404() {
  // Página 404 customizada para rotas não reconhecidas pelo hash router.
  hero.classList.add("hidden");
  view.innerHTML = [
    '<div class="not-found">',
    '<h2>404 — Página não encontrada</h2>',
    '<p>O endereço que você tentou acessar não existe.</p>',
    '<a href="#/" class="btn-primary">Voltar ao catálogo</a>',
    "</div>",
  ].join("");
}

function router() {
  // Roteador por hash (#/, #/produto/slug, #/biblioteca, #/carrinho, #/conta).
  // Rotas desconhecidas renderizam a página 404.
  const hash = location.hash || "#/";
  if (hash === "#/" || hash === "") {
    renderHome(null, null, null);
  } else if (hash.startsWith("#/produto/")) {
    renderProduct(decodeURIComponent(hash.slice("#/produto/".length)));
  } else if (hash === "#/biblioteca") {
    renderLibrary();
  } else if (hash === "#/carrinho") {
    renderCart();
  } else if (hash === "#/conta") {
    renderAccount();
  } else if (hash === "#/pedidos") {
    renderOrders();
  } else {
    render404();
  }
}

function setupSearch() {
  // Busca ao teclar Enter (sem recarregar a página).
  const input = document.getElementById("search-input");
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") {
      const q = input.value.trim();
      if (location.hash !== "#/") { location.hash = "#/"; }
      renderHome(q, null, null);
    }
  });
}

window.addEventListener("hashchange", function () {
  // Sobe ao topo da página a cada troca de rota (UX-12).
  window.scrollTo(0, 0);
  router();
});
window.addEventListener("DOMContentLoaded", function () {
  setupAuth(); setupSearch(); refreshAuthButton(); loadFacets(); router();
  document.getElementById("lib-btn").addEventListener("click", function () {
    location.hash = "#/biblioteca";
  });
  document.getElementById("cart-btn").addEventListener("click", function () {
    location.hash = "#/carrinho";
  });
  document.getElementById("account-btn").addEventListener("click", function () {
    location.hash = "#/conta";
  });
  document.getElementById("orders-btn").addEventListener("click", function () {
    location.hash = "#/pedidos";
  });
  document.getElementById("news-form").addEventListener("submit", async function (ev) {
    ev.preventDefault();
    const email = document.getElementById("news-email").value;
    try {
      await api("/newsletter/subscribe", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email }),
      });
      toast("Inscrição feita! 🎉", "ok");
      document.getElementById("news-email").value = "";
    } catch (e) { toast("E-mail inválido.", "err"); }
  });
});
