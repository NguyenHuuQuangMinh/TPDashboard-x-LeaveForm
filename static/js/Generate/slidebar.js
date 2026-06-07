function toggleSidebar() {

    const sidebar =
        document.getElementById('sidebar');

    const overlay =
        document.getElementById('sidebarOverlay');

    sidebar.classList.toggle('open');

    overlay.classList.toggle('show');
}

function closeSidebar() {

    document.getElementById('sidebar')
        .classList.remove('open');

    document.getElementById('sidebarOverlay')
        .classList.remove('show');
}

const sidebar = document.getElementById('sidebar');

sidebar.addEventListener('mouseenter', () => {
    sidebar.classList.add('open');
});

sidebar.addEventListener('mouseleave', () => {
    sidebar.classList.remove('open');
});