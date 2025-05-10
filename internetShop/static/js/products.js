document.addEventListener("DOMContentLoaded", () => {
    const hearts = document.querySelectorAll(".custom-heart");
    const ratingValue = document.getElementById("custom-rating-value");

    hearts.forEach((heart, idx) => {
      heart.addEventListener("click", () => {
        const newRating = idx + 1;
        ratingValue.textContent = newRating.toFixed(1);
        hearts.forEach((h, i) => {
          h.style.color = i < newRating ? "red" : "transparent";
          h.style.webkitTextStroke = i < newRating ? "0" : "1px red";
        });
      });
    });
  });