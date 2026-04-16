function toggleUserMenu(){
    const menu = document.getElementById("userDropdown")

    if (menu.style.display === "flex") {
        menu.style.display = "none";
    } else {
        menu.style.display = "flex";
    }
}

document.addEventListener("click", function (e) {
    const menu = document.getElementById("userDropdown");
    const box = document.querySelector(".user-box");

    if (!box.contains(e.target) && !menu.contains(e.target)) {
        menu.style.display = "none";
    }
});