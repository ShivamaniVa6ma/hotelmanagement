document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("subscription-form")
    const planInput = document.getElementById("plan")
    const durationSelect = document.getElementById("duration")
    const totalInput = document.getElementById("total")
  
    // Get the selected plan from URL parameters
    const urlParams = new URLSearchParams(window.location.search)
    const selectedPlan = urlParams.get("plan")
    planInput.value = selectedPlan || "No plan selected"
  
    // Define plan prices
    const planPrices = {
      free: 0,
      basic: 9.99,
      premium: 19.99,
    }
  
    // Calculate and update total amount
    function updateTotal() {
      const duration = Number.parseInt(durationSelect.value)
      const planPrice = planPrices[selectedPlan] || 0
      const total = (planPrice * duration).toFixed(2)
      totalInput.value = `$${total}`
    }
  
    durationSelect.addEventListener("change", updateTotal)
  
    form.addEventListener("submit", (e) => {
      e.preventDefault()
      const formData = new FormData(form)
      const userData = Object.fromEntries(formData.entries())
  
      // Here you would typically send this data to your server
      console.log("User data:", userData)
  
      alert("Proceeding to payment gateway...")
      // Redirect to payment gateway or process payment
      // window.location.href = '/payment-gateway';
    })
  })
  
  