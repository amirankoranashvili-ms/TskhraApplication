// const API_BASE = 'http://localhost:8080';
const API_BASE = 'http://10.227.164.247:8081';

let accessToken = null;

const BULK_ENDPOINTS = {
    'categories':  '/admin/trade-categories/bulk',
    'brands':      '/admin/brands/bulk',
    'attributes':  '/admin/attributes/bulk',
    'item-types':  '/admin/item-types/bulk',
    'attr-links':  '/admin/item-type-attributes/bulk'
};

const EXPORT_ENDPOINTS = {
    'categories':  '/admin/trade-categories/export',
    'brands':      '/admin/brands/export',
    'attributes':  '/admin/attributes/export',
    'item-types':  '/admin/item-types/export',
    'attr-links':  '/admin/item-type-attributes/export'
};

// --- API Client ---

async function api(method, path, body) {
    const headers = { 'Content-Type': 'application/json' };
    if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, opts);

    if (res.status === 401) {
        logout();
        throw new Error('Session expired');
    }

    if (res.status === 403) {
        throw new Error('Access denied — make sure your user has the ADMIN role in Keycloak');
    }

    if (res.status === 204) return null;

    if (!res.ok) {
        const err = await res.json().catch(() => ({ message: res.statusText }));
        throw new Error(err.message || err.error || res.statusText);
    }

    const text = await res.text();
    return text ? JSON.parse(text) : null;
}

// --- Auth ---

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('login-error');
    errEl.hidden = true;

    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const data = await api('POST', '/auth/login', { username, password });
        accessToken = data.access_token;
        document.getElementById('login-screen').hidden = true;
        document.getElementById('admin-shell').hidden = false;
        loadSection('categories');
    } catch (err) {
        errEl.textContent = 'Invalid credentials';
        errEl.hidden = false;
    }
});

function logout() {
    accessToken = null;
    document.getElementById('admin-shell').hidden = true;
    document.getElementById('login-screen').hidden = false;
    document.getElementById('login-password').value = '';
}

document.getElementById('logout-btn').addEventListener('click', logout);

// --- Navigation ---

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        loadSection(section);
    });
});

function loadSection(section) {
    document.querySelectorAll('.section').forEach(s => s.hidden = true);

    switch (section) {
        case 'categories':
            document.getElementById('sec-categories').hidden = false;
            loadCategories();
            break;
        case 'item-types':
            document.getElementById('sec-item-types').hidden = false;
            loadItemTypes();
            break;
        case 'attributes':
            document.getElementById('sec-attributes').hidden = false;
            loadAttributes();
            break;
        case 'attr-links':
            document.getElementById('sec-attr-links').hidden = false;
            loadAttrLinksSection();
            break;
        case 'brands':
            document.getElementById('sec-brands').hidden = false;
            loadBrands();
            break;
    }
}

// --- Form helpers ---

function showForm(id) { document.getElementById(id).hidden = false; }
function hideForm(id) { document.getElementById(id).hidden = true; }

function toast(msg, type = 'success') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = `toast toast-${type}`;
    el.hidden = false;
    setTimeout(() => { el.hidden = true; }, 3000);
}

// --- Pagination helper ---

function renderPagination(containerId, pageData, loadFn) {
    const container = document.getElementById(containerId);
    if (!pageData || pageData.totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    const page = pageData.number;
    const total = pageData.totalPages;
    const totalEl = pageData.totalElements;

    container.innerHTML = `
        <button class="btn-page" ${page === 0 ? 'disabled' : ''} onclick="void(0)">Prev</button>
        <span class="page-info">Page ${page + 1} of ${total} (${totalEl} items)</span>
        <button class="btn-page" ${page >= total - 1 ? 'disabled' : ''} onclick="void(0)">Next</button>
    `;

    const buttons = container.querySelectorAll('.btn-page');
    buttons[0].addEventListener('click', () => { if (page > 0) loadFn(page - 1); });
    buttons[1].addEventListener('click', () => { if (page < total - 1) loadFn(page + 1); });
}

// --- Categories ---

let categoriesDropdownLoaded = false;

async function loadCategories(page = 0) {
    try {
        const pageData = await api('GET', `/admin/trade-categories?page=${page}&size=20`);
        renderCategories(pageData.content);
        renderPagination('cat-pagination', pageData, loadCategories);
        if (!categoriesDropdownLoaded) {
            await populateCategorySelects();
            categoriesDropdownLoaded = true;
        }
    } catch (err) {
        toast(err.message, 'error');
    }
}

function renderCategories(categories) {
    const tbody = document.getElementById('cat-table');
    if (categories.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="5">No categories yet</td></tr>';
        return;
    }
    tbody.innerHTML = categories.map(c => `
        <tr>
            <td class="mono">${c.id}</td>
            <td>${c.name}</td>
            <td class="mono">${c.slug}</td>
            <td>${c.parentName || '-'}</td>
            <td><button class="btn-delete" onclick="deleteCategory(${c.id})">Delete</button></td>
        </tr>
    `).join('');
}

async function populateCategorySelects() {
    try {
        const allPage = await api('GET', '/admin/trade-categories?page=0&size=1000');
        const allCats = allPage.content;

        const parentSelect = document.getElementById('cat-parent');
        const itCatSelect = document.getElementById('it-category');

        parentSelect.innerHTML = '<option value="">No parent (root)</option>' +
            allCats.filter(c => !c.parentId).map(c =>
                `<option value="${c.id}">${c.name}</option>`
            ).join('');

        itCatSelect.innerHTML = '<option value="">Select category</option>' +
            allCats.map(c =>
                `<option value="${c.id}">${c.name}${c.parentId ? '' : ' (root)'}</option>`
            ).join('');
    } catch (_) {}
}

async function createCategory() {
    const name = document.getElementById('cat-name').value.trim();
    const slug = document.getElementById('cat-slug').value.trim();
    const parentId = document.getElementById('cat-parent').value || null;

    if (!name || !slug) return;

    try {
        await api('POST', '/admin/trade-categories', {
            name, slug, parentId: parentId ? parseInt(parentId) : null
        });
        document.getElementById('cat-name').value = '';
        document.getElementById('cat-slug').value = '';
        document.getElementById('cat-parent').value = '';
        hideForm('cat-form');
        toast('Category created');
        categoriesDropdownLoaded = false;
        loadCategories();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function deleteCategory(id) {
    if (!confirm('Delete this category?')) return;
    try {
        await api('DELETE', `/admin/trade-categories/${id}`);
        toast('Category deleted');
        categoriesDropdownLoaded = false;
        loadCategories();
    } catch (err) {
        toast(err.message, 'error');
    }
}

// --- Item Types ---

let itemTypesDropdownLoaded = false;

async function loadItemTypes(page = 0) {
    try {
        const pageData = await api('GET', `/admin/item-types?page=${page}&size=20`);
        renderItemTypes(pageData.content);
        renderPagination('it-pagination', pageData, loadItemTypes);
        if (!itemTypesDropdownLoaded) {
            await populateItemTypeSelects();
            itemTypesDropdownLoaded = true;
        }
        if (!categoriesDropdownLoaded) {
            await populateCategorySelects();
            categoriesDropdownLoaded = true;
        }
    } catch (err) {
        toast(err.message, 'error');
    }
}

function renderItemTypes(types) {
    const tbody = document.getElementById('it-table');
    if (types.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="5">No item types yet</td></tr>';
        return;
    }
    tbody.innerHTML = types.map(t => `
        <tr>
            <td class="mono">${t.id}</td>
            <td>${t.name}</td>
            <td class="mono">${t.slug}</td>
            <td>${t.categoryName || t.categoryId}</td>
            <td><button class="btn-delete" onclick="deleteItemType(${t.id})">Delete</button></td>
        </tr>
    `).join('');
}

async function populateItemTypeSelects() {
    try {
        const allPage = await api('GET', '/admin/item-types?page=0&size=1000');
        const types = allPage.content;
        const linkFilterSelect = document.getElementById('link-filter-it');
        linkFilterSelect.innerHTML = '<option value="">Select item type</option>' +
            types.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
    } catch (_) {}
}

async function createItemType() {
    const name = document.getElementById('it-name').value.trim();
    const slug = document.getElementById('it-slug').value.trim();
    const categoryId = document.getElementById('it-category').value;

    if (!name || !slug || !categoryId) return;

    try {
        await api('POST', '/admin/item-types', {
            name, slug, categoryId: parseInt(categoryId)
        });
        document.getElementById('it-name').value = '';
        document.getElementById('it-slug').value = '';
        document.getElementById('it-category').value = '';
        hideForm('it-form');
        toast('Item type created');
        itemTypesDropdownLoaded = false;
        loadItemTypes();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function deleteItemType(id) {
    if (!confirm('Delete this item type?')) return;
    try {
        await api('DELETE', `/admin/item-types/${id}`);
        toast('Item type deleted');
        itemTypesDropdownLoaded = false;
        loadItemTypes();
    } catch (err) {
        toast(err.message, 'error');
    }
}

// --- Attributes ---

let allAttributes = [];
let attributesDropdownLoaded = false;

async function loadAttributes(page = 0) {
    try {
        const pageData = await api('GET', `/admin/attributes?page=${page}&size=20`);
        allAttributes = pageData.content;
        renderAttributes();
        renderPagination('attr-pagination', pageData, loadAttributes);
        if (!attributesDropdownLoaded) {
            await populateAttributeSelect();
            attributesDropdownLoaded = true;
        }
    } catch (err) {
        toast(err.message, 'error');
    }
}

function renderAttributes() {
    const tbody = document.getElementById('attr-table');
    if (allAttributes.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No attributes yet</td></tr>';
        return;
    }
    tbody.innerHTML = allAttributes.map(a => `
        <tr>
            <td class="mono">${a.id}</td>
            <td>${a.name}</td>
            <td class="mono">${a.key}</td>
            <td><span class="badge">${a.dataType}</span></td>
            <td>${a.unit || '-'}</td>
            <td><button class="btn-delete" onclick="deleteAttribute(${a.id})">Delete</button></td>
        </tr>
    `).join('');
}

async function populateAttributeSelect() {
    try {
        const allPage = await api('GET', '/admin/attributes?page=0&size=1000');
        const attrs = allPage.content;
        const sel = document.getElementById('link-attr');
        sel.innerHTML = '<option value="">Select attribute</option>' +
            attrs.map(a => `<option value="${a.id}">${a.name} (${a.key})</option>`).join('');
    } catch (_) {}
}

async function createAttribute() {
    const name = document.getElementById('attr-name').value.trim();
    const key = document.getElementById('attr-key').value.trim();
    const dataType = document.getElementById('attr-datatype').value;
    const unit = document.getElementById('attr-unit').value.trim() || null;

    if (!name || !key) return;

    try {
        await api('POST', '/admin/attributes', { name, key, dataType, unit });
        document.getElementById('attr-name').value = '';
        document.getElementById('attr-key').value = '';
        document.getElementById('attr-datatype').value = 'STRING';
        document.getElementById('attr-unit').value = '';
        hideForm('attr-form');
        toast('Attribute created');
        attributesDropdownLoaded = false;
        loadAttributes();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function deleteAttribute(id) {
    if (!confirm('Delete this attribute?')) return;
    try {
        await api('DELETE', `/admin/attributes/${id}`);
        toast('Attribute deleted');
        attributesDropdownLoaded = false;
        loadAttributes();
    } catch (err) {
        toast(err.message, 'error');
    }
}

// --- Attribute Links ---

async function loadAttrLinksSection() {
    if (!attributesDropdownLoaded) {
        await populateAttributeSelect();
        attributesDropdownLoaded = true;
    }
    if (!itemTypesDropdownLoaded) {
        await populateItemTypeSelects();
        itemTypesDropdownLoaded = true;
    }
    loadAttrLinks();
}

async function loadAttrLinks() {
    const itemTypeId = document.getElementById('link-filter-it').value;
    const tbody = document.getElementById('link-table');

    if (!itemTypeId) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="8">Select an item type above</td></tr>';
        return;
    }

    try {
        const links = await api('GET', `/admin/item-type-attributes/by-item-type/${itemTypeId}`);
        if (links.length === 0) {
            tbody.innerHTML = '<tr class="empty-row"><td colspan="8">No attributes linked</td></tr>';
            return;
        }
        tbody.innerHTML = links.map(l => `
            <tr>
                <td class="mono">${l.id}</td>
                <td>${l.attributeName}</td>
                <td class="mono">${l.attributeKey}</td>
                <td><span class="badge">${l.dataType}</span></td>
                <td><span class="badge ${l.required ? 'badge-yes' : 'badge-no'}">${l.required ? 'Yes' : 'No'}</span></td>
                <td><span class="badge ${l.filterable ? 'badge-yes' : 'badge-no'}">${l.filterable ? 'Yes' : 'No'}</span></td>
                <td class="mono">${l.constraints ? JSON.stringify(l.constraints) : '-'}</td>
                <td><button class="btn-delete" onclick="deleteAttrLink(${l.id})">Delete</button></td>
            </tr>
        `).join('');
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function createAttrLink() {
    const itemTypeId = document.getElementById('link-filter-it').value;
    const attributeId = document.getElementById('link-attr').value;
    const required = document.getElementById('link-required').checked;
    const filterable = document.getElementById('link-filterable').checked;
    const constraintsStr = document.getElementById('link-constraints').value.trim();

    if (!itemTypeId || !attributeId) {
        toast('Select an item type and attribute', 'error');
        return;
    }

    let constraints = null;
    if (constraintsStr) {
        try {
            constraints = JSON.parse(constraintsStr);
        } catch (_) {
            toast('Invalid JSON in constraints', 'error');
            return;
        }
    }

    try {
        await api('POST', '/admin/item-type-attributes', {
            itemTypeId: parseInt(itemTypeId),
            attributeId: parseInt(attributeId),
            required,
            filterable,
            constraints
        });
        document.getElementById('link-attr').value = '';
        document.getElementById('link-required').checked = false;
        document.getElementById('link-filterable').checked = true;
        document.getElementById('link-constraints').value = '';
        hideForm('link-form');
        toast('Attribute linked');
        loadAttrLinks();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function deleteAttrLink(id) {
    if (!confirm('Remove this attribute link?')) return;
    try {
        await api('DELETE', `/admin/item-type-attributes/${id}`);
        toast('Link removed');
        loadAttrLinks();
    } catch (err) {
        toast(err.message, 'error');
    }
}

// --- Brands ---

async function loadBrands(page = 0) {
    try {
        const pageData = await api('GET', `/brands?page=${page}&size=20`);
        const brands = pageData.content;
        const tbody = document.getElementById('brand-table');
        if (brands.length === 0) {
            tbody.innerHTML = '<tr class="empty-row"><td colspan="4">No brands yet</td></tr>';
            renderPagination('brand-pagination', null, loadBrands);
            return;
        }
        tbody.innerHTML = brands.map(b => `
            <tr>
                <td class="mono">${b.id}</td>
                <td>${b.name}</td>
                <td class="mono">${b.slug}</td>
                <td><button class="btn-delete" onclick="deleteBrand(${b.id})">Delete</button></td>
            </tr>
        `).join('');
        renderPagination('brand-pagination', pageData, loadBrands);
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function createBrand() {
    const name = document.getElementById('brand-name').value.trim();
    const slug = document.getElementById('brand-slug').value.trim();

    if (!name || !slug) return;

    try {
        await api('POST', '/admin/brands', { name, slug });
        document.getElementById('brand-name').value = '';
        document.getElementById('brand-slug').value = '';
        hideForm('brand-form');
        toast('Brand created');
        loadBrands();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function deleteBrand(id) {
    if (!confirm('Delete this brand?')) return;
    try {
        await api('DELETE', `/admin/brands/${id}`);
        toast('Brand deleted');
        loadBrands();
    } catch (err) {
        toast(err.message, 'error');
    }
}

// --- Import / Export ---

async function importEntity(type) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        try {
            const text = await file.text();
            const data = JSON.parse(text);
            const result = await api('POST', BULK_ENDPOINTS[type], data);
            toast(`Created: ${result.created}, Skipped: ${result.skipped}, Errors: ${result.failed}`);
            reloadCurrentSection();
        } catch (err) {
            toast(err.message, 'error');
        }
    };
    input.click();
}

async function exportEntity(type) {
    try {
        const data = await api('GET', EXPORT_ENDPOINTS[type]);
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}-export.json`;
        a.click();
        URL.revokeObjectURL(url);
        toast('Export downloaded');
    } catch (err) {
        toast(err.message, 'error');
    }
}

function invalidateDropdownCaches() {
    categoriesDropdownLoaded = false;
    itemTypesDropdownLoaded = false;
    attributesDropdownLoaded = false;
}

function reloadCurrentSection() {
    invalidateDropdownCaches();
    const active = document.querySelector('.nav-link.active');
    if (active) loadSection(active.dataset.section);
}

// --- Seed Data Loader ---

async function loadSeedData() {
    if (!confirm('This will import demo data (skips duplicates). Continue?')) return;

    const steps = [
        { file: 'seed-data/01-categories.json', endpoint: BULK_ENDPOINTS['categories'], label: 'Categories' },
        { file: 'seed-data/02-brands.json', endpoint: BULK_ENDPOINTS['brands'], label: 'Brands' },
        { file: 'seed-data/03-attributes.json', endpoint: BULK_ENDPOINTS['attributes'], label: 'Attributes' },
        { file: 'seed-data/04-item-types.json', endpoint: BULK_ENDPOINTS['item-types'], label: 'Item Types' },
        { file: 'seed-data/05-item-type-attributes.json', endpoint: BULK_ENDPOINTS['attr-links'], label: 'Attribute Links' }
    ];

    for (const step of steps) {
        try {
            const res = await fetch(step.file);
            const data = await res.json();
            const result = await api('POST', step.endpoint, data);
            toast(`${step.label}: +${result.created}, skipped ${result.skipped}${result.failed ? ', errors ' + result.failed : ''}`);
        } catch (err) {
            toast(`${step.label}: ${err.message}`, 'error');
        }
    }

    reloadCurrentSection();
}
