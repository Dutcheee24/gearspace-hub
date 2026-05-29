function toggleSidebar(){
    document.getElementById("sidebar").classList.toggle("show");
}

const searchInput = document.getElementById("searchInput");
if (searchInput) {
    searchInput.addEventListener("keyup", function(){
        const searchValue = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll(".product-row");

        rows.forEach(row => {
            const nameInput = row.querySelector("input[name='item_name']");
            const categoryInput = row.querySelector("input[name='category']");
            
            const nameText = nameInput ? nameInput.value.toLowerCase() : "";
            const categoryText = categoryInput ? categoryInput.value.toLowerCase() : "";

            if (nameText.includes(searchValue) || categoryText.includes(searchValue)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
}

document.querySelectorAll(".btn-update").forEach(button => {
    button.addEventListener("click", function() {
        const row = this.closest(".product-row");
        const itemId = row.getAttribute("data-id");

        const itemName = row.querySelector("input[name='item_name']").value;
        const category = row.querySelector("input[name='category']").value;
        const status = row.querySelector("select[name='status']").value;
        const borrower = row.querySelector("input[name='borrower']").value;

        const formData = new FormData();
        formData.append("item_name", itemName);
        formData.append("category", category);
        formData.append("status", status);
        formData.append("borrower", borrower);

        const originalText = this.innerText;
        this.innerText = "Saving...";
        this.disabled = true;

        fetch(`/update/${itemId}`, {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (response.ok) {
                this.innerText = "Saved!";
                this.classList.replace("btn-warning", "btn-success");
                setTimeout(() => {
                    this.innerText = originalText;
                    this.classList.replace("btn-success", "btn-warning");
                    this.disabled = false;
                    window.location.reload(); // I-reload para mag-update ang kulay ng badge at dashboard
                }, 1000);
            } else {
                alert("Error saving.");
                this.innerText = originalText;
                this.disabled = false;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            this.innerText = originalText;
            this.disabled = false;
        });
    });
});