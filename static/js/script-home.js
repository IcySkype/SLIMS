function handleDisagree() {
    document.getElementById("acknowledgmentModal").style.display = "none";
    document.getElementById("acknowledgmentModalz").style.display = "none";
}

function showModal() {
    document.getElementById("choiceModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("choiceModal").style.display = "none";
}

function chooseLabGown() {
    closeModal();
    document.getElementById("acknowledgmentModal").style.display = "flex";
}

function chooseMaterials() {
    closeModal();
    document.getElementById("acknowledgmentModalz").style.display = "flex";
}

function closeAcknowledgment() {
    document.getElementById("acknowledgmentModal").style.display = "none";
    document.getElementById("acknowledgmentModalz").style.display = "none";
}

function goToAnotherPage(page) {
    window.location.href = page;
}

window.onclick = function(event) {
    const choiceModal = document.getElementById("choiceModal");
    const acknowledgmentModal = document.getElementById("acknowledgmentModal");
    if (event.target === choiceModal) {
        choiceModal.style.display = "none";
    }
    if (event.target === acknowledgmentModal) {
        acknowledgmentModal.style.display = "none";
    }
};
