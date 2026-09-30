
const form = document.getElementById("fitnessForm");
const result = document.getElementById("result");
const loading = document.getElementById("loading");
const button = document.getElementById("generateBtn");

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const userData = {
        name: document.getElementById("name").value,
        age: document.getElementById("age").value,
        weight: document.getElementById("weight").value,
        height: document.getElementById("height").value,
        goal: document.getElementById("goal").value,
        level: document.getElementById("level").value,
        diet: document.getElementById("diet").value
    };

    loading.hidden = false;
    result.textContent = "";
    button.disabled = true;

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong");
        }

        result.textContent = data.plan;

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }

    loading.hidden = true;
    button.disabled = false;
});