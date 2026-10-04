const BACKEND_URL = 'http://backend:5000';
let currentPage = 1;
let currentFilters = {};

// Load listings on page load
document.addEventListener('DOMContentLoaded', () => {
    loadListings();
});

// Load listings with filters
async function loadListings(page = 1) {
    try {
        const searchQuery = document.getElementById('search')?.value || '';
        const categoryQuery = document.getElementById('category')?.value || '';
        const sortQuery = document.getElementById('sort')?.value || 'newest';
        
        const params = new URLSearchParams({
            page: page,
            search: searchQuery,
            category: categoryQuery,
            sort: sortQuery
        });
        
        const response = await fetch(`${BACKEND_URL}/api/listings?${params}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        displayListings(data.listings);
        displayPagination(data.pages, page);
        currentPage = page;
    } catch (error) {
        console.error('Error loading listings:', error);
        document.getElementById('listings-container').innerHTML = 
            `<div class="loading" style="grid-column: 1/-1;">Error loading listings: ${error.message}</div>`;
    }
}

// Display listings
function displayListings(listings) {
    const container = document.getElementById('listings-container');
    
    if (!listings || listings.length === 0) {
        container.innerHTML = '<div class="loading" style="grid-column: 1/-1;">No listings found</div>';
        return;
    }
    
    container.innerHTML = listings.map(listing => `
        <div class="listing-card" onclick="viewListing(${listing.id})">
            <div class="listing-image">
                <img src="${listing.image_url || 'https://via.placeholder.com/300?text=No+Image'}" onerror="this.src='https://via.placeholder.com/300?text=No+Image'">
                <div class="listing-badge">${listing.condition || 'Used'}</div>
            </div>
            <div class="listing-info">
                <div class="listing-title">${listing.title}</div>
                <div class="listing-price">$${listing.price.toFixed(2)}</div>
                <div class="listing-meta">
                    <div>📍 ${listing.location}</div>
                    <div>📅 ${new Date(listing.created_at).toLocaleDateString()}</div>
                </div>
                <div class="listing-seller">
                    <div class="seller-avatar">${listing.seller.username.charAt(0).toUpperCase()}</div>
                    <div class="seller-info">
                        <div class="seller-name">${listing.seller.username}</div>
                        <div class="seller-rating">⭐ ${listing.seller.rating.toFixed(1)}</div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// View listing detail
async function viewListing(listingId) {
    try {
        const response = await fetch(`${BACKEND_URL}/api/listings/${listingId}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const listing = await response.json();
        displayListingDetail(listing);
        openModal('detail-modal');
    } catch (error) {
        console.error('Error loading listing:', error);
        alert('Error loading listing details');
    }
}

// Display listing detail
function displayListingDetail(listing) {
    const detailDiv = document.getElementById('listing-detail');
    
    detailDiv.innerHTML = `
        <div class="detail-image">
            <img src="${listing.image_url || 'https://via.placeholder.com/400?text=No+Image'}" 
                 onerror="this.src='https://via.placeholder.com/400?text=No+Image'" style="width:100%;height:100%;object-fit:cover;">
        </div>
        <div class="detail-info">
            <h2>${listing.title}</h2>
            <div class="detail-price">$${listing.price.toFixed(2)}</div>
            
            <div class="detail-meta">
                <div class="detail-item">
                    <label>Category</label>
                    ${listing.category}
                </div>
                <div class="detail-item">
                    <label>Condition</label>
                    ${listing.condition || 'Not specified'}
                </div>
                <div class="detail-item">
                    <label>Location</label>
                    ${listing.location}
                </div>
                <div class="detail-item">
                    <label>Views</label>
                    ${listing.views}
                </div>
            </div>
            
            <div class="detail-description">
                <strong>Description:</strong><br>${listing.description}
            </div>
            
            <div class="detail-seller">
                <div class="seller-card">
                    <div class="seller-avatar-large">
                        ${listing.seller.username.charAt(0).toUpperCase()}
                    </div>
                    <div class="seller-details">
                        <h4>${listing.seller.username}</h4>
                        <p>⭐ Rating: ${listing.seller.rating.toFixed(1)}/5</p>
                        <p>📞 ${listing.seller.phone || 'Contact via message'}</p>
                    </div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="handleMessage(${listing.seller.id}, ${listing.id})">
                    💬 Message Seller
                </button>
                <button class="btn btn-secondary" onclick="handleContact(${listing.seller.id})">
                    ❤️ Save Listing
                </button>
            </div>
        </div>
    `;
}

// Display pagination
function displayPagination(totalPages, currentPage) {
    const paginationDiv = document.getElementById('pagination');
    let html = '';
    
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" 
                        onclick="loadListings(${i})">${i}</button>`;
    }
    
    paginationDiv.innerHTML = html;
}

// Filter listings
function filterListings() {
    loadListings(1);
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
    document.body.style.overflow = 'auto';
}

// Click outside to close modal
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
});

// Handle login
function handleLogin(e) {
    e.preventDefault();
    alert('Login feature coming soon!');
    closeModal('login-modal');
}

// Handle register
function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    fetch(`${BACKEND_URL}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: formData.get('username'),
            email: formData.get('email'),
            full_name: formData.get('full_name'),
            password: formData.get('password')
        })
    })
    .then(r => r.json())
    .then(data => {
        alert('Registration successful!');
        closeModal('register-modal');
    })
    .catch(err => alert('Registration failed: ' + err.message));
}

// Handle create listing
function handleCreateListing(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    fetch(`${BACKEND_URL}/api/listings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: formData.get('title'),
            description: formData.get('description'),
            category: formData.get('category'),
            price: parseFloat(formData.get('price')),
            location: formData.get('location'),
            condition: formData.get('condition'),
            seller_id: 1
        })
    })
    .then(r => r.json())
    .then(data => {
        alert('Listing created successfully!');
        closeModal('sell-modal');
        loadListings();
    })
    .catch(err => alert('Failed to create listing: ' + err.message));
}

// Handle message
function handleMessage(sellerId, listingId) {
    const message = prompt('Enter your message:');
    if (!message) return;
    
    fetch(`${BACKEND_URL}/api/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sender_id: 1,
            receiver_id: sellerId,
            listing_id: listingId,
            content: message
        })
    })
    .then(r => r.json())
    .then(data => {
        alert('Message sent!');
    })
    .catch(err => alert('Failed to send message: ' + err.message));
}

// Handle contact (save listing)
function handleContact(sellerId) {
    alert('Listing saved to favorites!');
}