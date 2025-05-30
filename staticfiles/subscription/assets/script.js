document.addEventListener("DOMContentLoaded", () => {
    const selectPlanButtons = document.querySelectorAll(".select-plan")
  
    selectPlanButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const plan = button.getAttribute("data-plan")
        alert(`You selected the ${plan} plan. Redirecting to cart...`)
        // Here you would typically redirect to the cart page
        // window.location.href = `/cart?plan=${plan}`;
      })
    })
  })
  
  // Update this in your landing page script.js
selectPlanButtons.forEach(button => {
    button.addEventListener('click', () => {
        const plan = button.getAttribute('data-plan');
        window.location.href = `cart.html?plan=${plan}`;
    });
});