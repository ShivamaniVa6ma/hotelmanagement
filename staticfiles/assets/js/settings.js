    // setTimeout(function () {
    //     console.log("💥 Is jQuery loaded?", typeof $);
    
    //     if (typeof $ === "undefined") {
    //         console.error("❌ jQuery is NOT loaded before this script runs.");
    //         return;
    //     }
    
    //     $(document).ready(function () {
    //         alert("✅ jQuery is ready, About Us form script is working.");
    //     });
    // }, 500);


    $(document).ready(function () {
        console.log("💡 About Us form script loaded!");
    
        const submitUrl = $('#aboutUsForm').data('url');
        console.log("🧭 Submit URL:", submitUrl);
    
        const form = $('#aboutUsForm');
        console.log("📝 Form found:", form.length > 0);
    
        form.on('submit', function (e) {
            e.preventDefault();
            console.log("🚀 Form submission started");
    
            const formData = new FormData(this);
            console.log("📦 FormData created");
    
            // Log form data (for debugging)
            for (let pair of formData.entries()) {
                console.log('Form contains:', pair[0], pair[1]);
            }
    
            $.ajax({
                url: submitUrl,
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                headers: {
                    "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()
                },
                beforeSend: function () {
                    console.log("🌐 Making AJAX request to:", submitUrl);
                },
                success: function (response) {
                    console.log("✅ Response:", response);
                    if (response.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: response.message
                        }).then(() => {
                            form.trigger('reset');
                            $('#preview-image').attr('src', '#').hide();
                            $('#file-name').text("No file chosen");
                        });
                    } else {
                        let errorHtml = "<ul style='text-align: left; font-size: 14px;'>";
                        if (response.errors) {
                            for (let field in response.errors) {
                                response.errors[field].forEach((msg) => {
                                    errorHtml += `<li><strong>${field}:</strong> ${msg}</li>`;
                                });
                            }
                        } else {
                            errorHtml += `<li>${response.message}</li>`;
                        }
                        errorHtml += "</ul>";
    
                        Swal.fire({
                            icon: 'error',
                            title: 'Form Validation Failed',
                            html: errorHtml
                        });
                    }
                },
                error: function (xhr, status, error) {
                    console.error("❌ AJAX Error:", error);
                    console.error("Status:", status);
                    console.error("Response Text:", xhr.responseText);
    
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: 'Something went wrong. Please check the console for details.'
                    });
                }
            });
        });
    });
    
   // Make loadAboutUsList globally accessible
function loadAboutUsList() {
    const container = $(".aboutlistview_container");
    const fetchUrl = $("#aboutList").data("url");

    $.ajax({
        url: fetchUrl,
        type: "GET",
        success: function (response) {
            container.empty();

            if (response.status === "success") {
                if (response.entries.length === 0) {
                    container.append("<p class='text-muted'>No About Us entries found.</p>");
                    return;
                }

                response.entries.forEach(entry => {
                    const html = `
                        <div class="card mb-3 shadow-sm p-3 rounded-4 about-entry">
                            <div class="row g-3 align-items-center">
                                ${entry.image_url ? `
                                    <div class="col-md-3">
                                        <img src="${entry.image_url}" class="img-fluid rounded" alt="${entry.title}">
                                    </div>` : ''
                                }
                                <div class="${entry.image_url ? 'col-md-9' : 'col-md-12'}">
                                    <h5 class="mb-1 fw-semibold">${entry.title}</h5>
                                    <p class="mb-2 text-muted">${entry.description}</p>
                                    <small class="text-secondary">Created on: ${entry.created_at}</small>
                                    <button class="btn btn-sm btn-danger mt-2 delete-aboutus-btn" data-id="${entry.id}">Delete</button>
                                </div>
                            </div>
                        </div>
                    `;

                    container.append(html);
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Failed to Load',
                    text: response.message || 'Could not fetch the About Us list.'
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("❌ AJAX error:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to fetch data. Please try again later.'
            });
        }
    });
}

$(document).ready(function () {
    console.log("📄 About Us list loader script started");
    loadAboutUsList();
});

    // Delete button click
    $(document).on("click", ".delete-aboutus-btn", function () {
        const entryId = $(this).data("id");
    
        if (!entryId) {
            console.error("❌ No entry ID found.");
            Swal.fire("Error", "Unable to delete: ID not found.", "error");
            return;
        }
    
        Swal.fire({
            title: 'Are you sure?',
            text: 'This action cannot be undone!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/admin-panel/about-us/${entryId}/delete/`,
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    success: function (response) {
                        if (response.status === 'success') {
                            Swal.fire('Deleted!', response.message, 'success');
                            loadAboutUsList();  // Refresh list
                        } else {
                            Swal.fire('Error', response.message || 'Something went wrong.', 'error');
                        }
                    },
                    error: function (xhr) {
                        console.error("❌ AJAX delete error:", xhr.responseText);
                        Swal.fire('Error', 'Something went wrong.', 'error');
                    }
                });
            }
        });
    });
    
    

// Utility to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


    // console.log("🧪 Script loaded!");
    
    // document.addEventListener("DOMContentLoaded", function () {
    //     const form = document.getElementById("aboutUsForm");
    //     const submitUrl = $('#aboutUsForm').data('url');

    
    //     if (!form) {
    //         console.error("❌ Form not found");
    //         return;
    //     }
    
    //     console.log("✅ Form found");
    
    //     form.addEventListener("submit", function (e) {
    //         e.preventDefault();
    //         console.log("🚀 Submit triggered");
    //         alert("Submit triggered!");
    
    //         const formData = new FormData(form);
    //         const url = form.getAttribute("data-url");
    
    //         console.log("📡 Submitting to:", url);
    
    //         fetch(url, {
    //             method: "POST",
    //             body: formData,
    //             headers: {
    //                 "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
    //             },
    //         })
    //         .then((res) => res.json())
    //         .then((data) => {
    //             console.log("✅ Response:", data);
    //         })
    //         .catch((err) => {
    //             console.error("❌ Error submitting form:", err);
    //         });
    //     });
    // });
   
   

    //  document.addEventListener('DOMContentLoaded', function() {
    //     const aboutUsForm = document.getElementById('aboutUsForm');
    //     const fileUpload = document.getElementById('file-upload');
    //     const previewImage = document.getElementById('preview-image');
    //     const fileNameText = document.getElementById('file-name');
    //     const resetBtn = document.getElementById('resetBtn');
    
    //     // Handle file upload and preview
    //     fileUpload.addEventListener('change', function() {
    //         const file = this.files[0];
    //         if (file && file.type.startsWith('image/')) {
    //             fileNameText.textContent = file.name;
    //             const reader = new FileReader();
    //             reader.onload = function(e) {
    //                 previewImage.src = e.target.result;
    //                 previewImage.style.display = 'block';
    //             };
    //             reader.readAsDataURL(file);
    //         } else {
    //             alert('Please select a valid image file (JPEG, PNG, GIF, etc.)');
    //             resetImagePreview();
    //         }
    //     });
    
    //     // Reset button functionality
    //     resetBtn.addEventListener('click', function() {
    //         aboutUsForm.reset();
    //         resetImagePreview();
    //     });
    
    //     function resetImagePreview() {
    //         fileNameText.textContent = 'No file chosen';
    //         previewImage.style.display = 'none';
    //         previewImage.src = '#';
    //     }
    
    //     // Form submission via AJAX
    //     aboutUsForm.addEventListener('submit', async function(e) {
    //         e.preventDefault();
        
    //         console.log("Submitting form..."); // 🔴 Debugging log
        
    //         // Validate form inputs
    //         if (!fileUpload.files.length) {
    //             alert('Please upload an image.');
    //             return;
    //         }
    //         if (!document.getElementById('title').value.trim()) {
    //             alert('Title is required.');
    //             return;
    //         }
    //         if (!document.getElementById('description').value.trim()) {
    //             alert('Description is required.');
    //             return;
    //         }
        
    //         Swal.fire({
    //             title: 'Saving...',
    //             text: 'Please wait while we save the details.',
    //             allowOutsideClick: false,
    //             showConfirmButton: false,
    //             didOpen: () => Swal.showLoading()
    //         });
        
    //         const formData = new FormData(this);
    //         const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
    //         console.log("Sending AJAX request..."); // 🔴 Debugging log
        
    //         try {
    //             const response = await fetch("{% url 'admin-panel:save_about_us' %}", {
    //                 method: 'POST',
    //                 headers: {
    //                     'X-CSRFToken': csrftoken,
    //                     'X-Requested-With': 'XMLHttpRequest' // Mark as AJAX
    //                 },
    //                 body: formData,
    //                 credentials: 'same-origin'
    //             });
        
    //             console.log("Response received:", response); // 🔴 Debugging log
        
    //             const data = await response.json();
    //             console.log("Server Response Data:", data); // 🔴 Debugging log
        
    //             Swal.close();
        
    //             if (data.status === 'success') {
    //                 Swal.fire({
    //                     icon: 'success',
    //                     title: 'Success!',
    //                     text: data.message,
    //                     confirmButtonColor: '#28a745'
    //                 }).then(() => {
    //                     aboutUsForm.reset();
    //                     resetImagePreview();
    //                 });
    //             } else {
    //                 Swal.fire({
    //                     icon: 'error',
    //                     title: 'Error!',
    //                     text: data.message,
    //                     confirmButtonColor: '#dc3545'
    //                 });
    //             }
    //         } catch (error) {
    //             console.error('Fetch error:', error);
    //             Swal.fire({
    //                 icon: 'error',
    //                 title: 'Oops...',
    //                 text: 'Something went wrong! Please try again later.',
    //                 confirmButtonColor: '#dc3545'
    //             });
    //         }
    //     });
        
    // });

    

//     aboutUsForm.addEventListener("submit", function (e) {
// e.preventDefault();

// // Check if a file is selected
// if (fileUpload.files.length === 0) {
//     Swal.fire({
//         icon: "error",
//         title: "Oops...",
//         text: "Please upload an image before submitting!",
//     });
//     return;
// }

// // Prepare form data
// let formData = new FormData(this);
//     console.log("Submitting About Us Form...");


//     fetch("{% url 'admin-panel:about_us_submit' %}", {
//         method: "POST",
//         body: formData,
//         headers: {
//             "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
//         },
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             Swal.fire({
//                 icon: "success",
//                 title: "Success!",
//                 text: data.message,
//                 confirmButtonText: "OK"
//             }).then(() => {
//                 aboutUsForm.reset();
//             });
//         } else {
//             Swal.fire({
//                 icon: "error",
//                 title: "Error!",
//                 text: data.message,
//             });
//         }
//     })
//     .catch(error => {
//         console.error("Error:", error);
//         Swal.fire({
//             icon: "error",
//             title: "Oops...",
//             text: "Something went wrong! Please try again.",
//         });
//     });
// });


    //  document.addEventListener('DOMContentLoaded', function() {
    //      const fileUpload = document.getElementById('file-upload');
    //      const previewImage = document.getElementById('preview-image');
    //      const fileName = document.getElementById('file-name');
    //      const uploadPlaceholder = document.querySelector('.upload-placeholder');
    //      const titleInput = document.getElementById('title');
    //      const descriptionInput = document.getElementById('description');
    //      const titleCharCount = document.getElementById('title-character-count');
    //      const descriptionCharCount = document.getElementById('description-character-count');
    //      const resetBtn = document.getElementById('resetBtn');
    //      const aboutUsForm = document.getElementById('aboutUsForm');
    //      const successMessage = document.getElementById('successMessage');
    //      const dropArea = document.getElementById('drop-area');
         
    //      // Character counter update and styling
    //      function updateCharCounter(input, counter, maxLength) {
    //          const count = input.value.length;
    //          counter.textContent = count;
             
    //          // Update counter styling based on remaining characters
    //          const counterContainer = counter.parentElement;
    //          counterContainer.classList.remove('near-limit', 'at-limit');
             
    //          if (count >= maxLength * 0.9 && count < maxLength) {
    //              counterContainer.classList.add('near-limit');
    //          } else if (count === maxLength) {
    //              counterContainer.classList.add('at-limit');
    //          }
    //      }
         
    //      // Handle file upload and preview
    //      fileUpload.addEventListener('change', function() {
    //          const file = this.files[0];
    //          handleFile(file);
    //      });
         
    //      // Drag and drop functionality
    //      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    //          dropArea.addEventListener(eventName, preventDefaults, false);
    //      });
         
    //      function preventDefaults(e) {
    //          e.preventDefault();
    //          e.stopPropagation();
    //      }
         
    //      ['dragenter', 'dragover'].forEach(eventName => {
    //          dropArea.addEventListener(eventName, highlight, false);
    //      });
         
    //      ['dragleave', 'drop'].forEach(eventName => {
    //          dropArea.addEventListener(eventName, unhighlight, false);
    //      });
         
    //      function highlight() {
    //          dropArea.classList.add('bg-light');
    //          dropArea.style.borderColor = 'var(--primary-color)';
    //      }
         
    //      function unhighlight() {
    //          dropArea.classList.remove('bg-light');
    //          dropArea.style.borderColor = '#cbd5e1';
    //      }
         
    //      dropArea.addEventListener('drop', handleDrop, false);
         
    //      function handleDrop(e) {
    //          const dt = e.dataTransfer;
    //          const file = dt.files[0];
    //          handleFile(file);
    //      }
         
    //      function handleFile(file) {
    //          if (file && file.type.startsWith('image/')) {
    //              fileName.textContent = file.name;
                 
    //              const reader = new FileReader();
    //              reader.onload = function(e) {
    //                  previewImage.src = e.target.result;
    //                  previewImage.style.display = 'block';
    //                  uploadPlaceholder.style.display = 'none';
                     
    //                  // Add a nice fade-in effect
    //                  previewImage.style.opacity = 0;
    //                  setTimeout(() => {
    //                      previewImage.style.transition = 'opacity 0.5s ease';
    //                      previewImage.style.opacity = 1;
    //                  }, 50);
    //              }
    //              reader.readAsDataURL(file);
    //          } else if (file) {
    //              alert('Please select an image file (JPEG, PNG, GIF, etc.)');
    //              resetImagePreview();
    //          }
    //      }
         
    //      // Character counter for title
    //      titleInput.addEventListener('input', function() {
    //          updateCharCounter(this, titleCharCount, 100);
    //      });
         
    //      // Character counter for description
    //      descriptionInput.addEventListener('input', function() {
    //          updateCharCounter(this, descriptionCharCount, 500);
    //      });
         
    //      // Reset button functionality with animation
    //      resetBtn.addEventListener('click', function() {
    //          aboutUsForm.reset();
    //          resetImagePreview();
    //          titleCharCount.textContent = '0';
    //          descriptionCharCount.textContent = '0';
             
    //          // Reset counter styling
    //          document.querySelectorAll('.character-counter').forEach(counter => {
    //              counter.classList.remove('near-limit', 'at-limit');
    //          });
             
    //          // Add shake animation to reset button
    //          this.classList.add('animate__animated', 'animate__headShake');
    //          setTimeout(() => {
    //              this.classList.remove('animate__animated', 'animate__headShake');
    //          }, 1000);
    //      });
         
    //      // Form submission
    //      aboutUsForm.addEventListener('submit', function(e) {
    //          e.preventDefault();
             
    //          // Validate form
    //          if (fileUpload.files.length === 0) {
    //              alert('Please upload an image.');
    //              return;
    //          }
             
    //          if (!titleInput.value.trim()) {
    //              titleInput.focus();
    //              return;
    //          }
             

    //          if (!descriptionInput.value.trim()) {
    //              descriptionInput.focus();
    //              return;
    //          }
             
    //          // Hide form and show success message with animation
    //          aboutUsForm.style.display = 'none';
    //          successMessage.style.display = 'block';
             
    //          // Here you would typically send the form data to a server
    //          // For demonstration purposes, we're just showing the success message
             
    //          // Option to reset form after 5 seconds
    //          setTimeout(() => {
    //              // Uncomment these lines if you want automatic reset
    //              // aboutUsForm.reset();
    //              // resetImagePreview();
    //              // titleCharCount.textContent = '0';
    //              // descriptionCharCount.textContent = '0';
    //              // successMessage.style.display = 'none';
    //              // aboutUsForm.style.display = 'block';
    //          }, 5000);
    //      });
         
    //     function resetImagePreview() {
    //         fileName.textContent = "No file chosen";
    //         previewImage.style.display = "none";
    //         uploadPlaceholder.style.display = "block";
    //         fileUpload.value = ""; // Clear file input
    //     }

         
    //      // Floating label effect enhancement
    //      const formControls = document.querySelectorAll('.form-control');
    //      formControls.forEach(control => {
    //          control.addEventListener('focus', function() {
    //              this.parentElement.classList.add('focused');
    //          });
             
    //          control.addEventListener('blur', function() {
    //              this.parentElement.classList.remove('focused');
    //          });
    //      });
    //  });
     
    // document.addEventListener("DOMContentLoaded", function () {
    //     const aboutUsForm = document.getElementById("aboutUsForm");
    //     const fileUpload = document.getElementById("file-upload");
    //     const titleInput = document.getElementById("title");
    //     const descriptionInput = document.getElementById("description");
    //     const fileName = document.getElementById("file-name");

    //     aboutUsForm.addEventListener("submit", function (e) {
    //         e.preventDefault();

    //         // Validate File Input
    //         if (fileUpload.files.length === 0) {
    //             Swal.fire({
    //                 icon: "error",
    //                 title: "Oops...",
    //                 text: "Please upload an image before submitting!",
    //             });
    //             return;
    //         }

    //         // Validate Title
    //         if (!titleInput.value.trim()) {
    //             Swal.fire({
    //                 icon: "error",
    //                 title: "Validation Error",
    //                 text: "Title is required!",
    //             });
    //             return;
    //         }

    //         // Validate Description
    //         if (!descriptionInput.value.trim()) {
    //             Swal.fire({
    //                 icon: "error",
    //                 title: "Validation Error",
    //                 text: "Description is required!",
    //             });
    //             return;
    //         }

    //         let formData = new FormData(aboutUsForm);

    //         fetch("/admin-panel/about-us-submit/", {
    //             method: "POST",
    //             body: formData,
    //             headers: {
    //                 "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    //             },
    //         })
    //             .then((response) => response.json())
    //             .then((data) => {
    //                 if (data.success) {
    //                     Swal.fire({
    //                         icon: "success",
    //                         title: "Success!",
    //                         text: data.message,
    //                     }).then(() => {
    //                         aboutUsForm.reset();
    //                         resetImagePreview();
    //                     });
    //                 } else {
    //                     Swal.fire({
    //                         icon: "error",
    //                         title: "Error!",
    //                         text: data.message,
    //                     });
    //                 }
    //             })
    //             .catch((error) => {
    //                 console.error("Error:", error);
    //                 Swal.fire({
    //                     icon: "error",
    //                     title: "Oops...",
    //                     text: "Something went wrong! Please try again.",
    //                 });
    //             });
    //     });

    //     function resetImagePreview() {
    //         fileName.textContent = "No file chosen";
    //         fileUpload.value = ""; // Reset file input
    //     }
    // });


 

    // Sample team members data
    
 
    document.addEventListener('DOMContentLoaded', function() {
        const iconUpload = document.getElementById('iconUpload');
        const iconPreview = document.getElementById('iconPreview');
        const imageUpload = document.getElementById('imageUpload');
        const imagePreview = document.getElementById('imagePreview');
        const serviceForm = document.getElementById('serviceForm');
        const resetBtn = document.getElementById('resetBtn');
        
        // Preview icon image
        iconUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    iconPreview.innerHTML = `<img src="${e.target.result}" alt="Icon Preview">`;
                }
                reader.readAsDataURL(file);
            }
        });
        
        // Preview service image
        imageUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Image Preview">`;
                }
                reader.readAsDataURL(file);
            }
        });
        
    //     // Form submission
    //     serviceForm.addEventListener('submit', function(e) {
    //         e.preventDefault();
            
    //         const serviceName = document.getElementById('serviceName').value;
    //         const serviceDescription = document.getElementById('serviceDescription').value;
    //         const iconFile = iconUpload.files[0];
    //         const imageFile = imageUpload.files[0];
            
    //         // Validate form
    //         if (!serviceName || !serviceDescription) {
    //             alert('Please fill in all required fields');
    //             return;
    //         }
            
    //         // Here you would typically send this data to your server
    //         console.log('Service saved:', {
    //             name: serviceName,
    //             description: serviceDescription,
    //             icon: iconFile ? iconFile.name : null,
    //             image: imageFile ? imageFile.name : null
    //         });
            
    //         alert('Service saved successfully!');
    //         // Reset form after successful submission
    //         resetForm();
    //     });
        
    //     // Reset form
    //     resetBtn.addEventListener('click', resetForm);
        
    //     function resetForm() {
    //         serviceForm.reset();
    //         iconPreview.innerHTML = '<i class="fas fa-upload fa-2x text-muted"></i>';
    //         imagePreview.innerHTML = '<i class="fas fa-image fa-3x text-muted"></i>';
    //     }
    // });


 
    // document.addEventListener('DOMContentLoaded', function() {
    //     // Add delete functionality
    //     document.querySelectorAll('.delete-btn1').forEach(btn => {
    //         btn.addEventListener('click', function() {
    //             if (confirm('Are you sure you want to delete this service?')) {
    //                 // Find the parent service item and remove it
    //                 const serviceItem = this.closest('.service-item');
    //                 serviceItem.remove();
    //             }
    //         });
    //     });
    // });

 
 
    // Sample data for demonstration
//         // const sampleFacilities = [
//         //     {
//         //         id: 1,
//         //         name: "Swimming Pool",
//         //         description: "Luxurious infinity pool with ocean view. Open from 7:00 AM to 10:00 PM daily. Includes heated sections and a kiddie pool area.",
//         //         image: "/api/placeholder/800/600",
//         //         icon: "/api/placeholder/64/64",
//         //         status: "active"
//         //     },
//         //     {
//         //         id: 2,
//         //         name: "Fitness Center",
//         //         description: "State of the art gym equipment with personal trainers available. Features cardio machines, free weights, and yoga studio.",
//         //         image: "/api/placeholder/800/600",
//         //         icon: "/api/placeholder/64/64",
//         //         status: "active"
//         //     },
//         //     {
//         //         id: 3,
//         //         name: "Spa & Wellness",
//         //         description: "Relaxing spa treatments including massages, facials, and aromatherapy. Advance booking recommended.",
//         //         image: "/api/placeholder/800/600",
//         //         icon: "/api/placeholder/64/64",
//         //         status: "maintenance"
//         //     }
//         // ];
    
//         // // DOM elements
//         // const facilityFormCard = document.getElementById('facilityFormCard');
//         // const toggleFormBtn = document.getElementById('toggleFormBtn');
//         // const cancelBtn = document.getElementById('cancelBtn');
//         // const facilityForm = document.getElementById('facilityForm');
//         // const facilitiesList = document.getElementById('facilitiesList');
    
//         // // File upload elements
//         // const facilityImageInput = document.getElementById('facilityImage');
//         // const facilityIconInput = document.getElementById('facilityIcon');
//         // const imagePreview = document.getElementById('imagePreview');
//         // const iconPreview = document.getElementById('iconPreview');
//         // const imageRemove = document.getElementById('imageRemove');
//         // const iconRemove = document.getElementById('iconRemove');
    
//         // // Toggle form visibility
//         // toggleFormBtn.addEventListener('click', function() {
//         //     facilityFormCard.style.display = 'block';
//         //     toggleFormBtn.style.display = 'none';
//         //     window.scrollTo({top: facilityFormCard.offsetTop - 100, behavior: 'smooth'});
//         // });
    
//         // cancelBtn.addEventListener('click', function() {
//         //     facilityFormCard.style.display = 'none';
//         //     toggleFormBtn.style.display = 'block';
//         //     resetForm();
//         // });
    
//         // // Handle image upload preview
//         // facilityImageInput.addEventListener('change', function(e) {
//         //     handleFileUpload(e.target.files[0], imagePreview, imageRemove);
//         // });
    
//         // facilityIconInput.addEventListener('change', function(e) {
//         //     handleFileUpload(e.target.files[0], iconPreview, iconRemove);
//         // });
    
//         // // Remove image preview
//         // imageRemove.addEventListener('click', function() {
//         //     removeFilePreview(facilityImageInput, imagePreview, imageRemove);
//         // });
    
//         // iconRemove.addEventListener('click', function() {
//         //     removeFilePreview(facilityIconInput, iconPreview, iconRemove);
//         // });
    
//         // // Form submission
//         // facilityForm.addEventListener('submit', function(e) {
//         //     e.preventDefault();
        
//         //     // Get form values
//         //     const name = document.getElementById('facilityName').value;
//         //     const description = document.getElementById('facilityDescription').value;
//         //     const status = document.getElementById('facilityStatus').value;
        
//         //     // In a real application, you'd handle file uploads to server here
//         //     // For demo purposes, we're using placeholder images
//         //     const newFacility = {
//         //         id: Date.now(), // Generate a unique ID
//         //         name: name,
//         //         description: description,
//         //         status: status,
//         //         image: "/api/placeholder/800/600", // Placeholder for demo
//         //         icon: "/api/placeholder/64/64" // Placeholder for demo
//         //     };
        
//         //     // Add to sample facilities
//         //     sampleFacilities.push(newFacility);
        
//         //     // Update UI
//         //     renderFacilities();
        
//         //     // Reset form
//         //     resetForm();
        
//         //     // Hide form
//         //     facilityFormCard.style.display = 'none';
//         //     toggleFormBtn.style.display = 'block';
        
//         //     // Show success notification
//         //     showNotification('Facility added successfully!', 'success');
//         // });
    
//         // Helper functions
//         function handleFileUpload(file, previewElement, removeButton) {
//             if (!file) return;
        
//             const reader = new FileReader();
//             reader.onload = function(e) {
//                 previewElement.style.display = 'block';
//                 previewElement.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
//                 removeButton.style.display = 'flex';
//             };
//             reader.readAsDataURL(file);
//         }
    
//         function removeFilePreview(inputElement, previewElement, removeButton) {
//             inputElement.value = '';
//             previewElement.style.display = 'none';
//             previewElement.innerHTML = '';
//             removeButton.style.display = 'none';
//         }
    
//         function resetForm() {
//             facilityForm.reset();
//             removeFilePreview(facilityImageInput, imagePreview, imageRemove);
//             removeFilePreview(facilityIconInput, iconPreview, iconRemove);
//         }
    
//         function renderFacilities() {
//             facilitiesList.innerHTML = '';
        
//             if (sampleFacilities.length === 0) {
//                 facilitiesList.innerHTML = `
//                     <div class="col-12 text-center p-5">
//                         <i class="fas fa-info-circle text-muted fa-3x mb-3"></i>
//                         <h5 class="text-muted">No facilities found</h5>
//                         <p>Click the "Add New Facility" button to get started.</p>
//                     </div>
//                 `;
//                 return;
//             }
        
//             sampleFacilities.forEach(facility => {
//                 const statusBadge = getStatusBadge(facility.status);
            
//                 const facilityCard = document.createElement('div');
//                 facilityCard.className = 'col-md-6 col-lg-4 mb-4';
//                 facilityCard.innerHTML = `
//                     <div class="card facility-card h-100">
//                         <img src="${facility.image}" class="facility-image" alt="${facility.name}">
//                         <div class="card-body">
//                             <div class="facility-header mb-3">
//                                 <img src="${facility.icon}" class="facility-icon" alt="${facility.name} icon">
//                                 <div>
//                                     <h5 class="card-title mb-0">${facility.name}</h5>
//                                     ${statusBadge}
//                                 </div>
//                             </div>
//                             <p class="card-text">${facility.description}</p>
//                         </div>
//                         <div class="card-footer bg-white d-flex justify-content-end p-3">
//                             <button class="btn btn-outline-primary btn-action" onclick="editFacility(${facility.id})">
//                                 <i class="fas fa-edit"></i>
//                             </button>
//                             <button class="btn btn-outline-danger btn-action" onclick="deleteFacility(${facility.id})">
//                                 <i class="fas fa-trash"></i>
//                             </button>
//                         </div>
//                     </div>
//                 `;
            
//                 facilitiesList.appendChild(facilityCard);
//             });
//         }
    
//         function getStatusBadge(status) {
//             switch(status) {
//                 case 'active':
//                     return '<span class="badge bg-success">Active</span>';
//                 case 'inactive':
//                     return '<span class="badge bg-secondary">Inactive</span>';
//                 case 'maintenance':
//                     return '<span class="badge bg-warning text-dark">Maintenance</span>';
//                 default:
//                     return '';
//             }
//         }
    
//         function showNotification(message, type) {
//             const notificationHTML = `
//                 <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
//                     <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
//                         <div class="toast-header ${type === 'success' ? 'bg-success text-white' : 'bg-danger text-white'}">
//                             <strong class="me-auto">
//                                 ${type === 'success' ? '<i class="fas fa-check-circle me-2"></i>Success' : '<i class="fas fa-exclamation-circle me-2"></i>Error'}
//                             </strong>
//                             <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
//                         </div>
//                         <div class="toast-body">
//                             ${message}
//                         </div>
//                     </div>
//                 </div>
//             `;
        
//             const tempDiv = document.createElement('div');
//             tempDiv.innerHTML = notificationHTML;
//             document.body.appendChild(tempDiv);
        
//             // Auto remove after 3 seconds
//             setTimeout(() => {
//                 document.body.removeChild(tempDiv);
//             }, 3000);
//         }
    
//         // Edit and delete functions (for demonstration)
//         function editFacility(id) {
//             const facility = sampleFacilities.find(f => f.id === id);
//             if (!facility) return;
        
//             // Fill form with facility data
//             document.getElementById('facilityName').value = facility.name;
//             document.getElementById('facilityDescription').value = facility.description;
//             document.getElementById('facilityStatus').value = facility.status;
        
//             // Show form
//             facilityFormCard.style.display = 'block';
//             toggleFormBtn.style.display = 'none';
//             window.scrollTo({top: facilityFormCard.offsetTop - 100, behavior: 'smooth'});
        
//             showNotification('Editing facility: ' + facility.name, 'success');
//         }
    
//         function deleteFacility(id) {
//             const facilityIndex = sampleFacilities.findIndex(f => f.id === id);
//             if (facilityIndex === -1) return;
        
//             const facilityName = sampleFacilities[facilityIndex].name;
        
//             // Remove from array
//             sampleFacilities.splice(facilityIndex, 1);
        
//             // Update UI
//             renderFacilities();
        
//             showNotification('Facility "' + facilityName + '" deleted successfully!', 'success');
//         }
    
//         // Initialize
//         document.addEventListener('DOMContentLoaded', function() {
//             renderFacilities();
//         });



// //new script
// document.getElementById('facilityImage').addEventListener('change', function(e) {
//         const preview = document.getElementById('imagePreview');
//         const file = e.target.files[0];
    
//         if (file) {
//             const reader = new FileReader();
//             reader.onload = function(e) {
//                 preview.src = e.target.result;
//                 preview.style.display = 'block';
//             }
//             reader.readAsDataURL(file);
//         }
//     });

 
 
    document.addEventListener('DOMContentLoaded', function() {
      // Add event listeners for delete buttons
      document.querySelectorAll('.delete-btn2').forEach(btn => {
        btn.addEventListener('click', function() {
          const facilityName = this.closest('.facility-card').querySelector('.facility-name').textContent;
      
        });
      });
    });

       
// faq script code 
$(document).ready(function () {
    console.log("💡 FAQ form script loaded!");

    const submitUrl = $('#faqForm').attr('action');
    console.log("🧭 Submit URL:", submitUrl);

    const form = $('#faqForm');
    console.log("📝 Form found:", form.length > 0);

    form.on('submit', function (e) {
        e.preventDefault();
        console.log("🚀 Form submission started");

        const formData = new FormData(this);
        console.log("📦 FormData created");

        // Debug form data
        for (let pair of formData.entries()) {
            console.log('Form contains:', pair[0], pair[1]);
        }

        $.ajax({
            url: submitUrl,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            headers: {
                "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()
            },
            beforeSend: function () {
                console.log("🌐 Making AJAX request to:", submitUrl);
                Swal.fire({
                    title: 'Saving FAQ...',
                    text: 'Please wait while we save your entry.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading()
                    }
                });
            },
            success: function (response) {
                console.log("✅ Response:", response);
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: response.message
                    }).then(() => {
                        form.trigger('reset');
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops!',
                        text: response.message || 'Validation failed. Please check your input.'
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error("❌ AJAX Error:", error);
                console.error("Status:", status);
                console.error("Response Text:", xhr.responseText);

                let message = "Something went wrong. Please try again.";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: message
                });
            }
        });
    });
});

function loadFAQList() {
    const container = $("#faqList");
    const fetchUrl = container.data("url");

    $.ajax({
        url: fetchUrl,
        method: "GET",
        success: function (response) {
            container.empty();

            if (response.status === "success") {
                if (response.faqs.length === 0) {
                    container.append(`<p class="text-muted">No FAQs found.</p>`);
                    return;
                }

                response.faqs.forEach((faq, index) => {
                    const item = `
                        <div class="faq-item">
                            <div class="faq-item-header">${faq.faq_number}</div>
                            <div class="faq-question">${faq.question}</div>
                            <div class="faq-answer">${faq.answer}</div>
                            <button class="delete-faq-btn" data-id="${faq.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    `;
                    container.append(item);
                });
            } else {
                Swal.fire("Error", response.message || "Could not load FAQs", "error");
            }
        },
        error: function () {
            Swal.fire("Error", "Failed to fetch FAQs", "error");
        }
    });
}

$(document).on("click", ".delete-faq-btn", function () {
    const faqId = $(this).data("id");
    const deleteBase = $("#faqList").data("delete-base");
    const deleteUrl = deleteBase.replace("0", faqId);  // replaces the 0 with actual ID

    Swal.fire({
        title: "Are you sure?",
        text: "This FAQ will be deleted permanently.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Yes, delete it!"
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: deleteUrl,
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                success: function (response) {
                    if (response.status === "success") {
                        Swal.fire("Deleted!", response.message, "success");
                        loadFAQList();
                    } else {
                        Swal.fire("Error", response.message || "Failed to delete", "error");
                    }
                },
                error: function () {
                    Swal.fire("Error", "Failed to delete FAQ", "error");
                }
            });
        }
    });
});


$(document).ready(function () {
    loadFAQList();
});

// Utility to fetch CSRF token


// <!--end faq form script-->
// spaform script 

$(document).ready(function () {
    console.log("💆 Spa form script loaded!");

    const form = $('#spaForm');
    const submitUrl = form.attr('action');

    console.log("🧭 Submit URL:", submitUrl);
    console.log("📝 Form found:", form.length > 0);

    form.on('submit', function (e) {
        e.preventDefault();
        console.log("🚀 Form submission started");

        const formData = new FormData(this);
        console.log("📦 FormData created");

        // Debug: Log each field
        for (let pair of formData.entries()) {
            console.log('Form data ->', pair[0], pair[1]);
        }

        $.ajax({
            url: submitUrl,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            headers: {
                "X-CSRFToken": $('[name=csrfmiddlewaretoken]').val()
            },
            beforeSend: function () {
                Swal.fire({
                    title: 'Saving...',
                    text: 'Submitting your spa details, please wait.',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });
            },
            success: function (response) {
                console.log("✅ Success Response:", response);
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Saved!',
                        text: response.message
                    }).then(() => {
                        form.trigger('reset');
                        $('#imagePreview').hide();
                        $('#imagePreviewText').text("No image selected");
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops!',
                        text: response.message || 'Please check your form fields.'
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error("❌ AJAX Error:", error);
                console.error("Status:", status);
                console.error("Response Text:", xhr.responseText);

                let message = "Something went wrong. Please try again.";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: message
                });
            }
        });
    });

    // Preview selected image
    $('#image').on('change', function () {
        const file = this.files[0];
        if (file) {
            $('#imagePreviewText').hide();
            const reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').attr('src', e.target.result).show();
            }
            reader.readAsDataURL(file);
        } else {
            $('#imagePreview').hide();
            $('#imagePreviewText').text("No image selected").show();
        }
    });
});


function loadSpaList() {
    const spaContainer = $("#spaList");
    const fetchUrl = spaContainer.data("url");
    const deleteUrlBase = spaContainer.data("delete-url-base");
    // const deleteUrl = deleteUrlBase.replace("0", spaId);
    $.ajax({
        url: fetchUrl,
        method: "GET",
        success: function (response) {
            spaContainer.empty();
            if (response.status === "success") {
                if (response.spas.length === 0) {
                    spaContainer.append("<p class='text-muted'>No SPA records found.</p>");
                    return;
                }

                response.spas.forEach((spa, index) => {
                    const spaCard = `
                        <div class="list-item">
                            <div class="list-item-image">
                                <img src="${spa.image_url}" alt="${spa.name}" class="service-image" />
                            </div>
                            <div class="list-item-details">
                                <div class="list-item-name">${spa.name}</div>
                                <div class="list-item-time">
                                    <i class="bi bi-clock"></i> ${spa.from_time} - ${spa.to_time}
                                </div>
                                <div class="list-item-description">
                                    ${spa.description}
                                </div>
                            </div>
                            <button class="delete-btn3" data-id="${spa.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    `;
                    spaContainer.append(spaCard);
                });
            } else {
                Swal.fire("Error", response.message || "Could not load SPA list", "error");
            }
        },
        error: function () {
            Swal.fire("Error", "Failed to fetch SPA list", "error");
        }
    });

    spaContainer.on("click", ".delete-btn3", function () {
        const spaId = $(this).data("id");
    
        // Use jQuery to select spaList
        const deleteUrlBase = $("#spaList").data("delete-url-base"); // Now this will work
        const deleteUrl = deleteUrlBase.replace("0", spaId);
    
        Swal.fire({
            title: 'Are you sure?',
            text: "This will delete the SPA entry.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!'
        }).then(result => {
            if (result.isConfirmed) {
                $.ajax({
                    url: deleteUrl,
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    success: function (response) {
                        if (response.status === "success") {
                            Swal.fire("Deleted!", "SPA entry has been deleted.", "success");
                            loadSpaList();
                        } else {
                            Swal.fire("Error", response.message, "error");
                        }
                    },
                    error: function () {
                        Swal.fire("Error", "Failed to delete SPA entry", "error");
                    }
                });
            }
        });
    });
    
    
}

$(document).ready(function () {
    loadSpaList();
});

// end spa form script 



// Handle image preview
document.getElementById('image').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewText = document.getElementById('imagePreviewText');
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            imagePreviewText.style.display = 'none';
        };
        reader.readAsDataURL(file);
    } else {
        imagePreview.style.display = 'none';
        imagePreviewText.style.display = 'block';
    }
});

// Handle form submission


// <!--toggler script-->

document.addEventListener('DOMContentLoaded', function() {
    
    const toggleButton = document.querySelector('.lh-toggle-sidebar');
    const sidebar = document.querySelector('.lh-sidebar');
    const mainContent = document.querySelector('.lh-main');

    if (toggleButton && sidebar && mainContent) {
        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // Store sidebar state in localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });

        // Restore sidebar state on page load
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }
});

// facilities form ajax code
$(document).ready(function () {
    console.log("🏗️ Facility form script initialized");

    const form = $('#facilityForm');  // Use an ID for precision
    const submitUrl = form.attr('action'); // Should be set in the form's action attribute

    if (!form.length) {
        console.warn("🚫 Facility form not found!");
        return;
    }

    form.on('submit', function (e) {
        e.preventDefault();
        console.log("📨 Submitting facility form...");

        const formData = new FormData(this);

        // Optional basic check
        const name = form.find('input[name="name"]').val().trim();
        const description = form.find('textarea[name="description"]').val().trim();

        if (!name || !description) {
            Swal.fire({
                icon: 'warning',
                title: 'Missing Fields',
                text: 'Facility name and description are required.',
                confirmButtonColor: '#ffc107'
            });
            return;
        }

        $.ajax({
            url: submitUrl,
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            beforeSend: function () {
                Swal.fire({
                    title: 'Saving Facility...',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });
            },
            success: function (response) {
                console.log("✅ AJAX Response:", response);
                if (response.status === "success") {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: response.message,
                        confirmButtonColor: "#28a745"
                    }).then(() => {
                        form.trigger('reset');
                        if (typeof fetchFacilities === "function") {
                            fetchFacilities();
                        }
                    });
                } else {
                    let errorHtml = "<ul style='text-align:left; font-size: 14px;'>";
                    if (response.errors) {
                        for (const [field, messages] of Object.entries(response.errors)) {
                            messages.forEach(msg => {
                                errorHtml += `<li><strong>${field}:</strong> ${msg}</li>`;
                            });
                        }
                    } else {
                        errorHtml += `<li>${response.message}</li>`;
                    }
                    errorHtml += "</ul>";

                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        html: errorHtml,
                        confirmButtonColor: "#dc3545"
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error("❌ AJAX Error:", error);
                console.error("📄 Response Text:", xhr.responseText);
                Swal.fire({
                    icon: 'error',
                    title: 'Server Error',
                    text: 'Something went wrong. Please try again later.',
                    confirmButtonColor: "#dc3545"
                });
            }
        });
    });
});


// Load facility list
// function loadFacilitiesList() {
//     const fetchUrl = $("#facilitiesList").data("url");
//     const container = $("#facilitiesList");
    
//     $.ajax({
//         url: fetchUrl,
//         method: "GET",
//         success: function (response) {
//             container.empty();

//             if (response.status === "success" && response.facilities.length > 0) {
//                 response.facilities.forEach(facility => {
//                     const card = `
//                         <div class="facility-card shadow-sm rounded mb-4 p-3 d-flex flex-column flex-md-row align-items-center justify-content-between bg-white">
//                             <div class="d-flex align-items-center mb-3 mb-md-0" style="flex: 1;">
//                                 <div class="facility-icon me-3">
//                                     <img src="${facility.icon_url}" alt="Icon" class="rounded-circle" style="width: 60px; height: 60px; object-fit: cover;">
//                                 </div>
//                                 <div class="facility-info">
//                                     <h5 class="mb-1 text-primary">${facility.name}</h5>
//                                     <p class="mb-0 text-muted" style="max-width: 300px;">${facility.description}</p>
//                                 </div>
//                             </div>

//                             <div class="d-flex align-items-center gap-3">
//                                 <div class="facility-image">
//                                     <img src="${facility.image_url}" alt="Image" class="rounded" style="width: 100px; height: 70px; object-fit: cover;">
//                                 </div>
//                                 <div class="facility-actions">
//                                     <button class="btn btn-outline-danger btn-sm delete-facility-btn" data-id="${facility.id}">
//                                         <i class="fas fa-trash-alt"></i>
//                                     </button>
//                                 </div>
//                             </div>
//                         </div>
//                     `;

//                     container.append(card);
//                 });
//             } else {
//                 container.html("<p class='text-muted'>No facilities found.</p>");
//             }
//         },
//         error: function () {
//             Swal.fire("Error", "Failed to fetch facilities", "error");
//         }
//     });
// }

function loadFacilitiesList() {
    const fetchUrl = $("#facilitiesList").data("url");
    const container = $("#facilitiesList");
    
    $.ajax({
        url: fetchUrl,
        method: "GET",
        success: function (response) {
            container.empty();

            if (response.status === "success" && response.facilities.length > 0) {
                response.facilities.forEach(facility => {
                   // Update the facility card template
// Add this CSS to your stylesheet
const styleSheet = `
<style>
    .facility-card {
        background: #fff;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    .facility-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    .facility-content {
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 1.5rem;
        padding: 1.5rem;
        align-items: center;
    }

    .facility-icon {
        position: relative;
    }

   .facility-icon {
        position: relative;
        overflow: hidden;  // Add this to contain the animation
    }

    .facility-icon img {
        width: 70px;
        height: 70px;
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;  // Add smooth transition
    }

    .facility-icon img:hover {
        transform: scale(1.1);  // Add zoom effect on hover
        box-shadow: 0 6px 15px rgba(0,0,0,0.12);  // Enhanced shadow on hover
    }

    .facility-info {
        padding-right: 1rem;
    }

    .facility-info h5 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .facility-info p {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 0;
    }

    .facility-image {
        position: relative;
        overflow: hidden;
    }

    .facility-image img {
        width: 120px;
        height: 80px;
        border-radius: 10px;
        object-fit: cover;
        transition: transform 0.3s ease;
        margin-right: 1rem;
    }

    .facility-image img:hover {
        transform: scale(1.05);
    }

    .facility-actions {
        margin-left: 1rem;
    }

    .delete-facility-btn {
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #dc3545;
        background: transparent;
        color: #dc3545;
        transition: all 0.3s ease;
    }

    .delete-facility-btn:hover {
        background: #dc3545;
        color: white;
    }

    @media (max-width: 768px) {
        .facility-content {
            grid-template-columns: 1fr;
            text-align: center;
        }

        .facility-icon {
            margin: 0 auto;
        }

        .facility-info {
            padding: 1rem 0;
        }

        .facility-image {
            margin: 0 auto;
        }

        .facility-actions {
            margin: 1rem auto 0;
        }
    }
</style>
`;

// Update the facility card template
const card = `
    <div class="facility-card">
        <div class="facility-content">
            <div class="facility-icon">
                <img src="${facility.icon_url}" alt="${facility.name}" loading="lazy">
            </div>
            <div class="facility-info">
                <h5>${facility.name}</h5>
                <p>${facility.description}</p>
            </div>
            <div class="d-flex align-items-center">
                <div class="facility-image">
                    <img src="${facility.image_url}" alt="${facility.name}" loading="lazy">
                </div>
                <div class="facility-actions">
                    <button class="delete-facility-btn" data-id="${facility.id}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
`;

// Add the styles to the document head
document.head.insertAdjacentHTML('beforeend', styleSheet);


                    container.append(card);
                });
            } else {
                container.html("<p class='text-muted'>No facilities found.</p>");
            }
        },
        error: function () {
            Swal.fire("Error", "Failed to fetch facilities", "error");
        }
    });
}

// Delete handler
$(document).on("click", ".delete-facility-btn", function () {
    const facilityId = $(this).data("id");

    Swal.fire({
        title: 'Are you sure?',
        text: 'This will delete the facility permanently.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
    }).then(result => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/admin-panel/facilities/${facilityId}/delete/`,
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                success: function (response) {
                    if (response.status === "success") {
                        Swal.fire("Deleted!", response.message, "success");
                        loadFacilitiesList();
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function () {
                    Swal.fire("Error", "Something went wrong.", "error");
                }
            });
        }
    });
});

$(document).ready(function () {
    loadFacilitiesList();
});






// document.addEventListener('DOMContentLoaded', function() {
//     const logoSettingsForm = document.getElementById("logoSettingsForm");
//     const logoSettingsURL = "{% url 'admin-panel:logo_settings_view' %}";
//     const csrfToken = "{{ csrf_token }}";

//     if (logoSettingsForm) {
//         logoSettingsForm.addEventListener("submit", function(event) {
//             event.preventDefault();

//             const formData = new FormData(this);

//             $.ajax({
//                 url: logoSettingsURL,  // ✅ uses the global variable
//                 type: "POST",
//                 data: formData,
//                 processData: false,
//                 contentType: false,
//                 headers: {
//                     "X-CSRFToken": csrfToken
//                 },
//                 success: function(data) {
//                     if (data.success) {
//                         if (data.favicon_url) {
//                             $('#faviconPreview').attr('src', data.favicon_url);
//                         }
//                         if (data.light_logo_url) {
//                             $('#lightLogoPreview').attr('src', data.light_logo_url);
//                         }
//                         if (data.dark_logo_url) {
//                             $('#darkLogoPreview').attr('src', data.dark_logo_url);
//                         }

//                         Swal.fire({
//                             icon: 'success',
//                             title: 'Success',
//                             text: data.message,
//                             confirmButtonText: 'OK'
//                         });
//                     } else {
//                         Swal.fire({
//                             icon: 'error',
//                             title: 'Error',
//                             text: data.error || 'An error occurred.',
//                             confirmButtonText: 'OK'
//                         });
//                     }
//                 },
//                 error: function(xhr) {
//                     console.error('Error:', xhr);
//                     Swal.fire({
//                         icon: 'error',
//                         title: 'Error',
//                         text: 'Your Subscription Cannot Access to Change the Logo.',
//                         confirmButtonText: 'OK'
//                     });
//                 }
//             });
//         });
//     } else {
//         console.error("Form with ID 'logoSettingsForm' not found.");
//     }
// });

	

		document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("featureForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        let formData = new FormData(this);

        fetch("{% url 'admin-panel:create_feature' %}", {  
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(response => response.json()) // Convert response to JSON
        .then(data => {
            console.log("Server Response:", data);  // Debugging: Check the actual response

            if (data.success === true) {  // ✅ Ensure only success triggers the success message
                Swal.fire({
                    icon: 'success',
                    title: 'Success',
                    text: data.message,
                    showConfirmButton: false,
                    timer: 2000
                });

                document.getElementById("featureForm").reset();  // Clear the form
                //loadFeatureList();  // Reload the feature list dynamically
            } 
            else if (data.success === false) {  // ✅ Ensure only real errors trigger an error message
                let errorMessage = data.errors 
                    ? Object.values(data.errors).map(errList => errList.map(err => err.message).join("\n")).join("\n")
                    : "Something went wrong";

                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: errorMessage
                });
            }
        })
        .catch(error => {
            console.error("Fetch Error:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to submit Features form. Please try again.'
            });
        });
    });

    
});



		
	

	document.addEventListener('DOMContentLoaded', function () {
document.getElementById("eventform").addEventListener("submit", function (event) {
	event.preventDefault(); // Prevent default form submission

	let formData = new FormData(this);

	fetch("{% url 'admin-panel:create_event' %}", {  
		method: "POST",
		body: formData,
		headers: {
			"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
		}
	})
	.then(response => response.json()) // Convert response to JSON
	.then(data => {
		console.log("Server Response:", data);  // Debugging: Check the actual response

		if (data.success === true) {  // ✅ Ensure only success triggers the success message
			Swal.fire({
				icon: 'success',
				title: 'Success',
				text: data.message,
				showConfirmButton: false,
				timer: 2000
			});

			document.getElementById("eventform").reset();  // Clear the form
			//loadFeatureList();  // Reload the feature list dynamically
		} 
		else if (data.success === false) {  // ✅ Ensure only real errors trigger an error message
			let errorMessage = data.errors 
				? Object.values(data.errors).map(errList => errList.map(err => err.message).join("\n")).join("\n")
				: "Something went wrong";

			Swal.fire({
				icon: 'error',
				title: 'Error',
				text: errorMessage
			});
		}
	})
	.catch(error => {
		console.error("Fetch Error:", error);
		Swal.fire({
			icon: 'error',
			title: 'Error',
			text: 'Failed to submit Event/Holiday form. Please try again.'
		});
	});
});


});


$(document).ready(function () {

    // ✅ Function To Load Guest List
    function loadGuestList() {
        $.ajax({
            url: $("#guest-table").data('url'),  // ✅ Fetch the URL from table data-attribute
            type: "GET",
            dataType: "json",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            success: function (response) {
                if (response.guests) {
                    let guestTableBody = $("#guest-table tbody");
                    guestTableBody.empty();

                    // ✅ Loop through the guests and create rows
                    $.each(response.guests, function (index, guest) {
                        let row = `
                            <tr>
                                <td>${guest.id}</td>
                                <td>${guest.name}</td>
                                <td>${guest.phone}</td>
                                <td>${guest.email}</td>
                                <td>₹${guest.total_amount}</td>
                                <td>
                                    <div class="d-flex justify-content-center position-relative">
                                        <div class="dropdown">
                                            <button class="btn btn-outline-success dropdown-toggle" type="button"
                                                    id="dropdownMenuButton${guest.id}" data-bs-toggle="dropdown"
                                                    aria-expanded="false">
                                                <i class="ri-settings-3-line"></i>
                                            </button>
                                            <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton${guest.id}">
                                                <li>
                                                    <a class="dropdown-item" href="/admin-panel/guest/${guest.id}">
                                                        <i class="ri-eye-line me-2"></i> View Details
                                                    </a>
                                                </li>
                                                <li>
                                                    <a class="dropdown-item delete-guest-link" href="#" data-guest-id="${guest.id}">
                                                        <i class="ri-delete-bin-line me-2"></i> Delete
                                                    </a>

                                                </li>
                                            </ul>
                                        </div>
                                    </div>

                                </td>
                            </tr>
                        `;
                        guestTableBody.append(row);
                    });

                    // ✅ Handle Delete Button Click
                    $(".delete-guest-button").click(function () {
                        const guestId = $(this).data('guest-id');
                        deleteGuest(guestId);
                    });
                }
            },
            error: function () {
                $("#guest-table tbody").html('<tr><td colspan="6" class="text-center text-danger">Failed to load guests.</td></tr>');
            }
        });
    }

    // ✅ Function To Delete Guest (With SweetAlert2)
    function deleteGuest(guestId) {
        Swal.fire({
            title: 'Are you sure?',
            text: "This guest will be permanently deleted.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/admin-panel/guest/${guestId}/delete/`,
                    type: 'POST',
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    },
                    success: function(response) {
                        Swal.fire(
                            'Deleted!',
                            'The guest has been deleted.',
                            'success'
                        );
                        loadGuestList(); // you might need to also make this global if it's not already
                    },
                    error: function() {
                        Swal.fire(
                            'Error!',
                            'Failed to delete the guest.',
                            'error'
                        );
                    }
                });
            }
        });
    }
    
    $(document).ready(function () {
        function loadGuestList() {
            // your original AJAX logic (unchanged)...
        }
    
        loadGuestList();

        $(document).on("click", ".delete-guest-link", function (e) {
            e.preventDefault();
            const guestId = $(this).data("guest-id");
            deleteGuest(guestId);
        });
        
    });
    

    // ✅ Function To Get CSRF Token
    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    // ✅ Load guest list when Tab 1 is clicked
    $('a[data-bs-target="#tab1"]').on('shown.bs.tab', function () {
        loadGuestList();
    });

    // ✅ Auto-load guest list if tab 1 is active
    if ($('#tab1').hasClass('show active')) {
        loadGuestList();
    }
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

$(document).ready(function () {

    // Load team list
    function loadTeamList() {
        let teamUrl = $("#team-table").data('url');

        $.ajax({
            url: teamUrl,
            type: "GET",
            dataType: "json",
            headers: { "X-Requested-With": "XMLHttpRequest" },
            success: function (response) {
                let tbody = $("#team-table tbody");
                tbody.empty();

                if (response.team && response.team.length > 0) {
                    $.each(response.team, function (index, team) {
                        let row = `
                            <tr>
                                <td>${team.id}</td>
                                <td>${team.name}</td>
                                <td>${team.phone1}</td>
                                <td>${team.email1}</td>
                                <td>${team.designation}</td>
                                <td>
                                    <div class="d-flex justify-content-center">
                                        <button type="button" class="btn btn-outline-success">
                                            <i class="ri-information-line"></i>
                                        </button>
                                        <div class="dropdown">
                                            <button class="btn btn-outline-success dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                                <i class="ri-settings-3-line"></i>
                                            </button>
                                            <ul class="dropdown-menu">
                                                <li>
                                                    <a class="dropdown-item" href="/admin-panel/team-member/edit/${team.id}/">
                                                        <i class="ri-edit-line"></i>Edit
                                                    </a>
                                                </li>
                                                <li>
                                                    <button class="dropdown-item delete_btn" data-member-id="${team.id}">
                                                        <i class="ri-delete-bin-line"></i> Delete
                                                    </button>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `;
                        tbody.append(row);
                    });

                    // Reinitialize Bootstrap dropdown
                    document.querySelectorAll('.dropdown-toggle').forEach(function (dropdown) {
                        new bootstrap.Dropdown(dropdown);
                    });

                    // Bind delete button
                    $(".delete_btn").click(function () {
                        const memberId = $(this).data('member-id');
                        deleteTeamMember(memberId);
                    });

                } else {
                    tbody.html(`<tr><td colspan="6" class="text-center">No team members found.</td></tr>`);
                }
            },
            error: function (xhr) {
                console.error(xhr.responseText);
                $("#team-table tbody").html('<tr><td colspan="6" class="text-center text-danger">Error loading team list.</td></tr>');
            }
        });
    }

    // Delete member
    function deleteTeamMember(memberId) {
        Swal.fire({
            title: 'Are you sure?',
            text: "This team member will be permanently deleted.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/admin-panel/team-member/${memberId}/delete/`,
                    type: 'POST',
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    },
                    success: function (response) {
                        Swal.fire('Deleted!', 'Team member has been deleted.', 'success');
                        loadTeamList();
                    },
                    error: function () {
                        Swal.fire('Error!', 'Failed to delete team member.', 'error');
                    }
                });
            }
        });
    }

    // Get CSRF token
    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    // Auto load on tab click
    $('a[data-bs-target="#tab2"]').on('shown.bs.tab', function () {
        loadTeamList();
    });

    // Auto-load if tab2 is active
    if ($('#tab2').hasClass('show active')) {
        loadTeamList();
    }

});


    //document.addEventListener("DOMContentLoaded", function () {
		// document.querySelectorAll(".delete-guest-button").forEach(button => {
		// 	button.addEventListener("click", function () {
		// 		let guestId = this.getAttribute("data-guest-id");

		// 		if (!guestId) {
		// 			console.error("❌ Error: guestId is undefined or missing");
		// 			alert("Guest ID is missing!");
		// 			return;
		// 		}

		// 		console.log("🟢 Deleting Guest ID:", guestId);  // Debugging Step 1

		// 		if (confirm("Are you sure you want to delete this guest?")) {
		// 			let deleteUrl = `/admin-panel/guest/${guestId}/delete/`;  // Debugging Step 2

		// 			console.log("🟡 Sending DELETE request to:", deleteUrl);  // Debugging Step 3

		// 			fetch(deleteUrl, {
		// 				method: "POST",
		// 				headers: {
		// 					"X-CSRFToken": getCookie("csrftoken"),
		// 					"X-Requested-With": "XMLHttpRequest",
		// 					"Content-Type": "application/json",
		// 				},
		// 			})
		// 			.then(response => {
		// 				console.log("🟠 Raw Response:", response);  // Debugging Step 4
		// 				return response.json();
		// 			})
		// 			.then(data => {
		// 				console.log("🔵 Server Response:", data);  // Debugging Step 5
		// 				if (data.success) {
		// 					alert("✅ Guest deleted successfully!");
		// 					this.closest("tr").remove();  // ✅ Remove the row dynamically
		// 				} else {
		// 					alert("❌ Error deleting guest: " + (data.error || "Unknown error"));
		// 				}
		// 			})
		// 			.catch(error => {
		// 				console.error("🚨 Fetch Error:", error);
		// 				alert("❌ An error occurred while deleting the guest.");
		// 			});
		// 		}
		// 	});
		// });
	//});

	// Function to get CSRF Token
	function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== "") {
			const cookies = document.cookie.split(";");
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.startsWith(name + "=")) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}




	


    document.addEventListener('DOMContentLoaded', function() {
        // Initialize all offcanvas elements
        var offcanvasElements = [].slice.call(document.querySelectorAll('.offcanvas'));
        offcanvasElements.map(function(offcanvasElement) {
            return new bootstrap.Offcanvas(offcanvasElement);
        });
    });

	$(document).ready(function () {
		console.log("Booking script loaded");
        const ajaxUrl = $("#booking-table").data("url");

		function loadBookingList() {
			$.ajax({
				url: ajaxUrl,
				type: "GET",
				dataType: "json",
				headers: { "X-Requested-With": "XMLHttpRequest" },
				success: function (response) {
					console.log(response); // Log the response to check its structure
					if (response.bookings) {
						let bookingTableBody = $("#booking-table tbody");
						bookingTableBody.empty();
						$.each(response.bookings, function (index, booking) {
							let row = `
								<tr>
									<td>${booking.id}</td>
									<td>${booking.room_type}</td>
									<td>${booking.check_in}</td>
									<td>${booking.check_out}</td>
									<td>${booking.total_amount}</td>
									<td>
                                        <div class="d-flex justify-content-center">
                                            <button type="button" class="btn btn-outline-success">
                                                <i class="ri-information-line"></i>
                                            </button>
                                            <div class="dropdown">
                                                <button class="btn btn-outline-success dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                                    <i class="ri-settings-3-line"></i>
                                                </button>
                                                <ul class="dropdown-menu">
                                                    <li>
                                                        <a class="dropdown-item" href="/admin-panel/booking/${booking.id}/view/">
                                                            <i class="ri-eye-line"></i>View
                                                        </a>
                                                    </li>
                                                    <li>
                                                        <a class="dropdown-item" href="/admin-panel/bookings/${booking.id}/delete/">
                                                            <i class="ri-delete-bin-line"></i> Delete
                                                        </a>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </td>

								</tr>
							`;
							bookingTableBody.append(row);
						});
						// ✅ Reinitialize Bootstrap dropdowns for dynamically added elements
						document.querySelectorAll('.dropdown-toggle').forEach(function (dropdown) {
                    		new bootstrap.Dropdown(dropdown);
                });
					} else {
						// Handle case where there are no bookings
						$("#booking-table tbody").html('<tr><td colspan="6" class="text-center">No bookings found.</td></tr>');
					}
				},
				error: function (jqXHR, textStatus, errorThrown) {
					console.error("AJAX Error: ", textStatus, errorThrown); // Log the error
					$("#booking-table tbody").html('<tr><td colspan="6" class="text-center">Failed to load Bookings.</td></tr>');
				}   
			});
		}
	
		// Load team list when Tab 2 is clicked
		$('a[data-bs-target="#tab8"]').on('shown.bs.tab', function () {
			loadBookingList();
		});
		
		// Load team list on page load if tab 8 is active
		if ($('#tab8').hasClass('show active')) {
			loadBookingList();
		}
	});



    // document.getElementById('addRoomForm').addEventListener('submit', function(event) {
    //     event.preventDefault(); // Prevent the default form submission

    //     const formData = new FormData(this);

    //     fetch(this.action, {
    //         method: 'POST',
    //         body: formData,
    //         headers: {
    //             'X-CSRFToken': '{{ csrf_token }}' // Include CSRF token
    //         }
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.success === false) {
    //             // Show SweetAlert for error message
    //             Swal.fire({
    //                 icon: 'error',
    //                 title: 'Error',
    //                 text: data.message,
    //                 confirmButtonText: 'OK'
    //             });
    //         } else {
    //             // Show success message
    //             Swal.fire({
    //                 icon: 'success',
    //                 title: 'Success',
    //                 text: 'Room added successfully!',
    //                 confirmButtonText: 'OK'
    //             }).then(() => {
    //                 window.location.href = "{% url 'admin-panel:room_list' %}"; // Redirect to rooms page
    //             });
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Error:', error);
    //         Swal.fire({
    //             icon: 'error',
    //             title: 'Error',
    //             text: 'An unexpected error occurred. Please try again.',
    //             confirmButtonText: 'OK'
    //         });
    //     });
    // });

    function handleRoomTypeChange() {
        const roomTypeSelect = document.getElementById('room_type');
        const bedTypeSection = document.getElementById('bedTypeSection');
        const seatingSection = document.getElementById('seatingSection');
        const bedTypeInput = document.getElementById('bed_type');

        // ✅ Get the selected Room Type
        const selectedOption = roomTypeSelect.options[roomTypeSelect.selectedIndex];
        const bedType = selectedOption.getAttribute('data-bed-type');

        // ✅ If Room Type = Conference
        if (bedType === 'conference') {
            // Hide the Bed Type Section
            bedTypeSection.style.display = 'none';
            seatingSection.style.display = 'block';

            // ✅ Automatically clear the Bed Type value
            bedTypeInput.value = '';
        } else {
            // ✅ If Room Type != Conference, Show Bed Type
            bedTypeSection.style.display = 'block';
            seatingSection.style.display = 'none';

            // ✅ Preserve the previous bed type value (Do not clear it)
            if (bedTypeInput.value === '') {
                bedTypeInput.value = 'single';
            }
        }
    }

    // ✅ Trigger this function when the page loads
    document.addEventListener('DOMContentLoaded', function () {
        handleRoomTypeChange();
    });

    // ✅ Trigger this function when the Room Type changes
    document.getElementById('room_type').addEventListener('change', function () {
        handleRoomTypeChange();
    });



function deleteDesignation(id) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this action!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // Start the AJAX call
            $.ajax({
                url: `/admin-panel/team-designation/${id}/delete/`, // URL to your Django delete view
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': '{{ csrf_token }}'
                },
                success: function(response) {
                    if (response.status === 'success') {
                        Swal.fire(
                            'Deleted!',
                            'Team Designation has been deleted successfully.',
                            'success'
                        );
                        // Remove the deleted row without reloading the page
                        $(`[data-member-id="${id}"]`).closest('.designation-item').fadeOut();
                    } else {
                        Swal.fire(
                            'Error!',
                            'Something went wrong. Please try again.',
                            'error'
                        );
                    }
                },
                error: function(xhr) {
                    if (xhr.status === 403) {
                        Swal.fire(
                            'Permission Denied!',
                            'You do not have permission to perform this action.',
                            'error'
                        );
                    } else if (xhr.status === 404) {
                        Swal.fire(
                            'Not Found!',
                            'The team designation was not found.',
                            'error'
                        );
                    } else {
                        Swal.fire(
                            'Error!',
                            'Something went wrong. Please contact support.',
                            'error'
                        );
                    }
                }
            });
        }
    });
}


	// function deleteItem(url, itemId, itemType) {
	// 	if (!url || !itemId || !itemType) {
	// 		console.error('Missing required parameters for deletion');
	// 		return;
	// 	}
	
	// 	Swal.fire({
	// 		title: 'Are you sure?',
	// 		text: `Do you want to delete this ${itemType}?`,
	// 		icon: 'warning',
	// 		showCancelButton: true,
	// 		confirmButtonColor: '#d33',
	// 		cancelButtonColor: '#3085d6',
	// 		confirmButtonText: 'Yes, delete it!'
	// 	}).then((result) => {
	// 		if (result.isConfirmed) {
	// 			// Get CSRF token from the cookie
	// 			const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
	
	// 			// Send delete request
	// 			fetch(url, {
	// 				method: 'POST',
	// 				headers: {
	// 					'X-CSRFToken': csrftoken,
	// 					'Content-Type': 'application/json'
	// 				}
	// 			})
	// 			.then(response => {
	// 				if (!response.ok) {
	// 					throw new Error('Network response was not ok');
	// 				}
	// 				return response.json();
	// 			})
	// 			.then(data => {
	// 				if (data.success) {
	// 					// Remove the item from DOM
	// 					const element = document.querySelector(`[data-member-id="${itemId}"]`);
	// 					if (element) {
	// 						const parentItem = element.closest('.designation-item, .feature-item, .holiday-item');
	// 						if (parentItem) {
	// 							parentItem.remove();
	// 						}
	// 					}
	
	// 					// Show success message
	// 					Swal.fire({
	// 						icon: 'success',
	// 						title: 'Deleted!',
	// 						text: `The ${itemType} has been deleted successfully.`,
	// 						timer: 1500
	// 					});
	// 				} else {
	// 					throw new Error(data.message || 'Delete operation failed');
	// 				}
	// 			})
	// 			.catch(error => {
	// 				console.error('Error:', error);
	// 				Swal.fire({
	// 					icon: 'error',
	// 					title: 'Oops...',
	// 					text: `Failed to delete ${itemType}. Please try again.`
	// 				});
	// 			});
	// 		}
	// 	});
	// }
	
	document.addEventListener('DOMContentLoaded', function() {
		const singleRoom = document.getElementById('singleRoom');
		const bulkRooms = document.getElementById('bulkRooms');
		const singleRoomNumber = document.getElementById('singleRoomNumber');
		const bulkRoomNumbers = document.getElementById('bulkRoomNumbers');

		function toggleRoomNumberInputs() {
			if (singleRoom.checked) {
				singleRoomNumber.style.display = 'block';
				bulkRoomNumbers.style.display = 'none';
				singleRoomNumber.querySelector('input').required = true;
				bulkRoomNumbers.querySelectorAll('input').forEach(input => input.required = false);
			} else {
				singleRoomNumber.style.display = 'none';
				bulkRoomNumbers.style.display = 'block';
				singleRoomNumber.querySelector('input').required = false;
				bulkRoomNumbers.querySelectorAll('input').forEach(input => input.required = true);
			}
		}

		singleRoom.addEventListener('change', toggleRoomNumberInputs);
		bulkRooms.addEventListener('change', toggleRoomNumberInputs);

		// Add this new code for room type handling
		const roomType = document.getElementById('roomType');
		const bedTypeSection = document.getElementById('bedTypeSection');
		const seatingSection = document.getElementById('seatingSection');
		const bedTypeInputs = bedTypeSection.querySelectorAll('input[name="bedType"]');

		roomType.addEventListener('change', function() {
			if (this.value === 'executive') {
				bedTypeSection.style.display = 'none';
				seatingSection.style.display = 'block';
				// Remove required attribute from bed type inputs
				bedTypeInputs.forEach(input => input.required = false);
				// Add required attribute to seating capacity
				seatingSection.querySelector('input').required = true;
			} else {
				bedTypeSection.style.display = 'block';
				seatingSection.style.display = 'none';
				// Add required attribute back to bed type inputs
				bedTypeInputs.forEach(input => input.required = true);
				// Remove required attribute from seating capacity
				seatingSection.querySelector('input').required = false;
			}
		});
	});


	function previewImages(event) {
		const preview = document.getElementById('imagePreview');
		const files = event.target.files;
		const maxImages = 10;
		const existingImages = preview.children.length;
		const remainingSlots = maxImages - existingImages;

		// Check if adding new images would exceed the limit
		if (files.length > remainingSlots) {
			alert(`You can only upload up to ${maxImages} images. You have ${existingImages} images already.`);
			event.target.value = ''; // Clear the input
			return;
		}

		for (const file of files) {
			const reader = new FileReader();
			reader.onload = function(e) {
				const imgContainer = document.createElement('div');
				imgContainer.className = 'position-relative';
				
				const img = document.createElement('img');
				img.src = e.target.result;
				img.classList.add('preview-image', 'rounded');
				
				const removeBtn = document.createElement('button');
				removeBtn.innerHTML = '×';
				removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
				removeBtn.onclick = function() {
					imgContainer.remove();
					// Enable input if images are less than max
					const imageInput = document.getElementById('imageInput');
					if (preview.children.length < maxImages) {
						imageInput.disabled = false;
					}
				};
				
				imgContainer.appendChild(img);
				imgContainer.appendChild(removeBtn);
				preview.appendChild(imgContainer);

				// Disable input if max images reached
				if (preview.children.length >= maxImages) {
					document.getElementById('imageInput').disabled = true;
				}
			}
			reader.readAsDataURL(file);
		}
	}

	function handleSubmit(event) {
		event.preventDefault();
		const formData = new FormData(event.target);
		const data = Object.fromEntries(formData.entries());
		
		// Get selected features
		data.features = Array.from(formData.getAll('features'));
		
		// Here you would typically send the data to your backend
		console.log('Form Data:', data);
		
		// Show success message
		alert('Room added successfully!');
		event.target.reset();
		document.getElementById('imagePreview').innerHTML = '';
	}

	function resetForm() {
		// Reset the form
		document.getElementById('addRoomForm').reset();
		
		// Clear image preview
		document.getElementById('imagePreview').innerHTML = '';
		
		// Enable image input
		document.getElementById('imageInput').disabled = false;
		
		// Reset room number display (show single room, hide bulk)
		document.getElementById('singleRoomNumber').style.display = 'block';
		document.getElementById('bulkRoomNumbers').style.display = 'none';
		
		// Reset radio button to single room
		document.getElementById('singleRoom').checked = true;
		
		// Reset required attributes
		document.querySelector('#singleRoomNumber input').required = true;
		document.querySelectorAll('#bulkRoomNumbers input').forEach(input => input.required = false);
		
		// Reset room type related sections
		const bedTypeSection = document.getElementById('bedTypeSection');
		const seatingSection = document.getElementById('seatingSection');
		bedTypeSection.style.display = 'block';
		seatingSection.style.display = 'none';
		
		// Reset bed type required attributes
		bedTypeSection.querySelectorAll('input[name="bedType"]').forEach(input => input.required = true);
		seatingSection.querySelector('input').required = false;
	}
	
	



    document.addEventListener('DOMContentLoaded', function() {
      // Get theme toggle container and buttons
      const themeToggle = document.getElementById('theme-toggle');
      const darkModeBtn = themeToggle.querySelector('.dark');
      const lightModeBtn = themeToggle.querySelector('.light');
      
      // Check for saved theme preference or use default
      const savedTheme = localStorage.getItem('theme') || 'light';
      setTheme(savedTheme);
      updateToggleDisplay(savedTheme);
      
      // Add click event listeners to theme toggle buttons
      darkModeBtn.addEventListener('click', function() {
        setTheme('dark');
        updateToggleDisplay('dark');
        localStorage.setItem('theme', 'dark');
      });
      
      lightModeBtn.addEventListener('click', function() {
        setTheme('light');
        updateToggleDisplay('light');
        localStorage.setItem('theme', 'light');
      });
      
      // Function to set theme
      function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
      }
      
      // Function to update toggle button display
      function updateToggleDisplay(theme) {
        if (theme === 'dark') {
          themeToggle.classList.remove('display-dark');
          themeToggle.classList.add('display-light');
        } else {
          themeToggle.classList.remove('display-light');
          themeToggle.classList.add('display-dark');
        }
      }
    });


	


	$(document).ready(function () {
    // Delegate click event because buttons are loaded dynamically
    $(document).on("click", ".delete-team-member-btn", function () {
        let memberId = $(this).attr("data-member-id");

        if (!memberId || memberId === "None") {
            console.error("❌ Error: Member ID is missing or invalid.");
            alert("Error: Unable to delete. Member ID missing!");
            return;
        }

        console.log(`🗑️ Preparing to delete member ID: ${memberId}`);

        // Set delete request URL dynamically
        $("#deleteForm").attr("action", `/admin-panel/team/${memberId}/delete/`);
    });

    // Handle delete form submission via AJAX
    $("#deleteForm").submit(function (e) {
        e.preventDefault();
        let deleteUrl = $(this).attr("action");

        fetch(deleteUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Server Response:", data);
            if (data.success) {
                alert("✅ Member deleted successfully!");

                // Remove deleted member row
                $(`button[data-member-id="${memberId}"]`).closest("tr").remove();
            } else {
                console.error("❌ Deletion Failed:", data.error);
                alert("Error deleting member: " + (data.error || "Unknown error"));
            }
        })
        .catch(error => {
            console.error("❌ Fetch Error:", error);
            alert("An unexpected error occurred while deleting.");
        });
    });
});

// Function to get CSRF token
function getCSRFToken() {
    const cookieValue = document.cookie.match(/csrftoken=([^;]*)/);
    return cookieValue ? cookieValue[1] : "";
}


    
        document.getElementById("room-type-form").addEventListener("submit", function(event) {
            event.preventDefault(); // Prevent default form submission
    
            let formData = new FormData(this);
    
            fetch("{% url 'admin-panel:room_type' %}", {  // Ensure the correct URL name
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: data.message,
                        showConfirmButton: false,
                        timer: 2000
                    });
    
                    // Optionally, clear form fields after submission
                    document.getElementById("room-type-form").reset();
                } else {
                    let errorMessage = data.errors 
                        ? Object.values(data.errors).join("\n") 
                        : "Something went wrong";
    
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: errorMessage
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Failed to submit form. Please try again.'
                });
            });
        });
        
    
        document.addEventListener('DOMContentLoaded', function() {
           
            // Delete button click event
            document.querySelectorAll('.delete-button').forEach(button => {
                button.addEventListener('click', function() {
                    const id = this.getAttribute('data-id');
                    
                    // Use SweetAlert for confirmation
                    Swal.fire({
                        title: 'Are you sure?',
                        text: "You won't be able to revert this!",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Yes, delete it!'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Proceed with deletion
                            fetch(`/admin-panel/room-type/${id}/delete/`, {
                                method: 'DELETE',
                                headers: {
                                    'X-CSRFToken': '{{ csrf_token }}', // Ensure CSRF token is included
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Show success message
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Deleted!',
                                        text: 'The Room Type has been deleted.',
                                        confirmButtonText: 'OK'
                                    }).then(() => {
                                        location.reload(); // Reload the page to see changes
                                    });
                                } else {
                                    // Show error message
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error',
                                        text: data.message || 'An error occurred. Please try again.',
                                        confirmButtonText: 'OK'
                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: 'Failed to delete the Room type. Please try again.',
                                    confirmButtonText: 'OK'
                                });
                            });
                        }
                    });
                });
            });
        });
    
            
        document.addEventListener('DOMContentLoaded', function() {
           
            // Delete button click event
            document.querySelectorAll('.delete-button').forEach(button => {
                button.addEventListener('click', function() {
                    const id = this.getAttribute('data-id');
                    
                    // Use SweetAlert for confirmation
                    Swal.fire({
                        title: 'Are you sure?',
                        text: "You won't be able to revert this!",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Yes, delete it!'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Proceed with deletion
                            fetch(`/admin-panel/event/${id}/delete/`, {
                                method: 'DELETE',
                                headers: {
                                    'X-CSRFToken': '{{ csrf_token }}', // Ensure CSRF token is included
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    // Show success message
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Deleted!',
                                        text: 'The Event has been deleted.',
                                        confirmButtonText: 'OK'
                                    }).then(() => {
                                        location.reload(); // Reload the page to see changes
                                    });
                                } else {
                                    // Show error message
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error',
                                        text: data.message || 'An error occurred. Please try again.',
                                        confirmButtonText: 'OK'
                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: 'Failed to delete the Event. Please try again.',
                                    confirmButtonText: 'OK'
                                });
                            });
                        }
                    });
                });
            });
        });
    
            
    
        document.addEventListener('DOMContentLoaded', function() {
            let currentFeatureId = null;
            const deleteModal = document.getElementById('deleteConfirmModal');
            const confirmDeleteBtn = document.getElementById('confirmDeleteFeature');
        
            // When any delete button is clicked
            document.querySelectorAll('.delete-button').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    currentFeatureId = this.getAttribute('data-feature-id');
                    const modal = new bootstrap.Modal(deleteModal);
                    modal.show();
                });
            });
        
            // When confirm delete button in modal is clicked
            confirmDeleteBtn.addEventListener('click', function() {
                if (!currentFeatureId) return;
        
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
                // Send delete request
                fetch(`/admin-panel/feature/${currentFeatureId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Close the modal
                        const modalInstance = bootstrap.Modal.getInstance(deleteModal);
                        modalInstance.hide();
        
                        // Remove the feature element from DOM
                        const featureElement = document.querySelector(`.delete-button[data-feature-id="${currentFeatureId}"]`)
                            .closest('.feature-item');
                        if (featureElement) {
                            featureElement.remove();
                        }
        
                        // Show success message
                        Swal.fire({
                            icon: 'success',
                            title: 'Deleted!',
                            text: 'Feature has been deleted successfully.',
                            confirmButtonText: 'OK'
                        });
                    } else {
                        throw new Error(data.message || 'Failed to delete feature');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to delete the feature. Please try again.',
                        confirmButtonText: 'OK'
                    });
                })
                .finally(() => {
                    // Reset the feature ID
                    currentFeatureId = null;
                });
            });
        });
 
     document.addEventListener("DOMContentLoaded", function () {
         const tab3 = document.querySelector("#tab3-btn"); // Select tab by ID
 
         if (!tab3) {
             console.error("Tab3 button not found! Check the ID or selector in HTML.");
             return;
         }
 
         tab3.addEventListener("click", function () {
             console.log("Tab3 clicked, fetching rooms...");
             fetchRooms();
         });
     });
 
 
 
 function fetchRooms() {
     fetch("/admin-panel/api/rooms/")
         .then((response) => {
             console.log("Response status:", response.status);
             return response.json();
         })
         .then((data) => {
             console.log("Rooms received:", data);
 
             const container = document.querySelector("#tab3 .container");
             if (!container) {
                 console.error("Tab3 container not found!");
                 return;
             }
 
             container.innerHTML = ""; // Clear previous content
 
             if (Object.keys(data).length === 0) {
                 container.innerHTML = "<p>No rooms available.</p>";
                 return;
             }
 
             // Loop through room categories (standard, deluxe, vip, conference)
             for (const [roomType, roomData] of Object.entries(data)) {
                 const section = document.createElement("div");
                 section.innerHTML = `<h3 class="room-category">${roomData.title}</h3>`;
 
                 roomData.rooms.forEach((room) => {
                     let additionalInfo = roomType === "conference"
                         ? `<span><strong>Seating Capacity:</strong> ${room.seatingCapacity}</span>`
                         : `<span><strong>Bed Type:</strong> ${room.bedType}</span>`;
 
                     let roomItem = document.createElement("div");
                     roomItem.classList.add("room-item");
 
                     roomItem.innerHTML = `
                         <div class="room-header">
                             <span class="room-title">Room ${room.number}</span>
                             <div class="room-actions">
                                 <button class="action-btn edit" title="Edit Room"  style="color:#ffff">
                             <i class="fas fa-edit"></i>
                         </button>
                         <button class="action-btn delete" title="Delete Room"  style="color:#ffff">
                             <i class="fas fa-trash-alt"></i>
                         </button>
                          <button class="action-btn delete" title="View Room"  style="color:#ffff">
                            <i class='fas fa-eye'></i>
  
                         </button>
                             </div>
                         </div>
                         <div class="room-details">
                             <span><strong>Price:</strong> ${room.price}</span>
                             <span><strong>AC Type:</strong> ${room.ac}</span>
                             ${additionalInfo}
                             <span><strong>Max Occupancy:</strong> ${room.maxOccupancy}</span>
                         </div>
                     `;
 
                     section.appendChild(roomItem);
                 });
 
                 container.appendChild(section);
             }
         })
         .catch((error) => console.error("Error fetching rooms:", error));
 }
 
 
 
     function createRoomRow(room) {
         return `
             <div class="room-row" style="display: flex; flex-direction: row;gap:3px;background-color: #ffffff; padding: 10px;padding-bottom: 0px; border-radius: 5px; margin-bottom: 10px;">
                 <div class="room-number">
                     <span>Room ${room.number}</span>
                 
               <div class="action-buttons">
             
                         <button class="action-btn edit" title="Edit Room"  style="color:#ffff">
                             <i class="fas fa-edit"></i>
                         </button>
                         <button class="action-btn delete" title="Delete Room"  style="color:#ffff">
                             <i class="fas fa-trash-alt"></i>
                         </button>
                          <button class="action-btn delete" title="View Room"  style="color:#ffff">
                            <i class='fas fa-eye'></i>
 
                         </button>
                     </div>
                 </div>
                 
                 <div class="room-details">
                     <div class="detail-item">
                         <div class="icon-circle">
                             
                         </div>
                         <div class="detail-content" style="display: flex; flex-direction: row;gap:3px">
                             <div><span class="detail-label">Basic Price:</span></div>
                             <div><span class="detail-value">${room.price}</span></div>
                         </div>
                     </div>
                     <div class="detail-item">
                         <div class="icon-circle">
                             
                         </div>
                         <div class="detail-content"  style="display: flex; flex-direction: row;gap:3px">
                             <div><span class="detail-label">AC Type:</span></div>
                             <div><span class="detail-value">${room.ac}</span></div>
                         </div>
                     </div> 
                     <div class="detail-item">
                         <div class="icon-circle">      
                             
                         </div>
                         <div class="detail-content" style="display: flex; flex-direction: row;gap:3px">
                             <div><span class="detail-label">Bed Type:</span></div>
                             <div><span class="detail-value">${room.bedType}</span></div>
                         </div>
                     </div>
                     <div class="detail-item">
                         <div class="icon-circle">
                             
                         </div>
                         <div class="detail-content" style="display: flex; flex-direction: row;gap:3px">
                             <div><span class="detail-label">Max Occupancy:</span></div>
                             <div><span class="detail-value">${room.maxOccupancy}</span></div>
                         </div>
                     </div>
                 </div>
                 </div>
                 
                               
         `;
     }
 
 
     document.addEventListener('DOMContentLoaded', () => {
         const container = document.querySelector('.container');
         
         for (const [type, data] of Object.entries(roomTypes)) {
             const section = document.createElement('div');
             section.className = 'room-list';
             section.innerHTML = `
                 <h2 class="section-title">${data.title}</h2>
                 ${data.rooms.map(room => createRoomRow(room)).join('')}
             `;
             container.appendChild(section);
         }
     });
  
 
 // Preview image functions with animation
//  function previewImage(input, previewId) {
//      const preview = document.getElementById(previewId);
//      const file = input.files[0];
     
//      if (file) {
//          const reader = new FileReader();
//          reader.onload = function(e) {
//              preview.src = e.target.result;
//              preview.classList.add('success-animation');
//              setTimeout(() => {
//                  preview.classList.remove('success-animation');
//              }, 500);
//          }
//          reader.readAsDataURL(file);
//      }
//  }
function previewImage(input, previewId) {
    if (!input || !input.files || !input.files[0]) {
        console.log(`No file selected for ${previewId}`);
        return;
    }

    const file = input.files[0];
    const preview = document.getElementById(previewId);

    if (!preview) {
        console.error(`Preview element with ID ${previewId} not found`);
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Update file input labels
function updateFileLabel(input) {
    const label = input.parentElement.querySelector('span');
    if (input.files.length > 0) {
        label.textContent = input.files[0].name;
    }
}

// Setup file input listeners with error handling
function setupLogoPreview() {
    console.log('Setting up logo preview functionality');
    
    const logoInputs = [
        { id: 'favicon', previewId: 'faviconPreview' },
        { id: 'lightLogo', previewId: 'lightLogoPreview' },
        { id: 'darkLogo', previewId: 'darkLogoPreview' }
    ];
    
    logoInputs.forEach(({ id, previewId }) => {
        const input = document.getElementById(id);
        const preview = document.getElementById(previewId);

        if (input && preview) {
            console.log(`Found input and preview for ${id}`);
            input.addEventListener('change', function() {
                console.log(`File selected for ${id}`);
                previewImage(this, previewId);
                updateFileLabel(this);
            });
        } else {
            console.warn(`Could not find input or preview for ${id}`);
        }
    });
}

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing logo preview functionality');
    setupLogoPreview();
});

document.getElementById("favicon").addEventListener("change", function () {
    previewImage(this, "faviconPreview");
});

document.getElementById("lightLogo").addEventListener("change", function () {
    previewImage(this, "lightLogoPreview");
});

document.getElementById("darkLogo").addEventListener("change", function () {
    previewImage(this, "darkLogoPreview");
});

document.getElementById("darkModeToggle").addEventListener('change', function() {
    document.body.style.transition = 'background-color 0.3s ease';
    document.body.classList.toggle('dark-mode');
});

document.getElementById('settingsForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('siteName', document.getElementById('siteName').value);
    formData.append('favicon', document.getElementById('favicon').files[0]);
    formData.append('lightLogo', document.getElementById('lightLogo').files[0]);
    formData.append('darkLogo', document.getElementById('darkLogo').files[0]);

    // Add success animation to button
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.classList.add('success-animation');
    setTimeout(() => {
        submitButton.classList.remove('success-animation');
        alert('Settings saved successfully!');
    }, 500);
});


    document.addEventListener('DOMContentLoaded', function() {
        // Edit button click event
        // document.querySelectorAll('.edit-button').forEach(button => {
        //     button.addEventListener('click', function() {
        //         const id = this.getAttribute('data-id');
        //         // Fetch the team designation data and populate the form
        //         fetch(`/team-designation/${id}/edit/`)
        //             .then(response => response.json())
        //             .then(data => {
        //                 if (data.success) {
        //                     // Populate the form with the data
        //                     document.querySelector('#designation').value = data.designation;
        //                     document.querySelector('#date_time').value = data.date_time;
        //                     document.querySelector('#team-designation-id').value = id; // Hidden input for ID
        //                 } else {
        //                     alert('Error fetching data.');
        //                 }
        //             });
        //     });
        // });

        // Delete button click event
        document.querySelectorAll('.delete-button').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                
                // Use SweetAlert for confirmation
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Proceed with deletion
                        fetch(`/admin-panel/team-designation/${id}/delete/`, {
                            method: 'DELETE',
                            headers: {
                                'X-CSRFToken': '{{ csrf_token }}', // Ensure CSRF token is included
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                // Show success message
                                Swal.fire({
                                    icon: 'success',
                                    title: 'Deleted!',
                                    text: 'The designation has been deleted.',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    location.reload(); // Reload the page to see changes
                                });
                            } else {
                                // Show error message
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: data.message || 'An error occurred. Please try again.',
                                    confirmButtonText: 'OK'
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'Failed to delete the designation. Please try again.',
                                confirmButtonText: 'OK'
                            });
                        });
                    }
                });
            });
        });
    });
});


    $(document).ready(function () {
        console.log("🧠 Service Form script loaded!");
    
        const form = $('#serviceForm');
        const submitUrl = '/admin-panel/save-service/';  // Update if dynamic
    
        form.on('submit', function (e) {
            e.preventDefault();
            console.log("🚀 Submitting service form...");
    
            const formData = new FormData(this);
    
            // Debug: Log form entries
            for (let pair of formData.entries()) {
                console.log(`${pair[0]}:`, pair[1]);
            }
    
            $.ajax({
                url: submitUrl,
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function (response) {
                    console.log("✅ Success Response:", response);
    
                    if (response.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Service Saved!',
                            text: response.message
                        }).then(() => {
                            form.trigger('reset');
                            $('#iconPreview').html('<i class="fas fa-upload fa-2x text-muted"></i>');
                            $('#imagePreview').html('<i class="fas fa-image fa-3x text-muted"></i>');
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Validation Error!',
                            text: response.message
                        });
                    }
                },
                error: function (xhr) {
                    console.error("❌ AJAX Error", xhr);
                
                    let msg = "Something went wrong.";
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.message) {
                            msg = response.message;
                        }
                    } catch (e) {
                        console.warn("Error parsing error response", e);
                    }
                
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: msg
                    });
                }
                
            });
        });
    
        // Optional: Reset button clears previews
        $('#resetBtn').on('click', function () {
            form.trigger('reset');
            $('#iconPreview').html('<i class="fas fa-upload fa-2x text-muted"></i>');
            $('#imagePreview').html('<i class="fas fa-image fa-3x text-muted"></i>');
        });
    });
    

    // ✅ Global function to fetch services
function loadServicesList() {
    const container = $(".services-list");
    const fetchUrl = $("#serviceList").data("url");  // from HTML data-url attr

    $.ajax({
        url: fetchUrl,
        method: "GET",
        success: function (response) {
            container.empty();

            if (response.status === "success") {
                if (response.services.length === 0) {
                    container.append("<p class='text-muted'>No services found.</p>");
                    return;
                }

                response.services.forEach(service => {
                    const html = `
                        <div class="service-item">
                            <div class="service-icon-container">
                                <img src="${service.icon_url}" alt="Icon" class="service-icon">
                            </div>
                            <div class="service-info">
                                <h4 class="service-name">${service.name}</h4>
                                <p class="service-description">${service.description}</p>
                            </div>
                            <div class="service-image-container">
                                <img src="${service.image_url}" alt="Image" class="service-image">
                            </div>
                            <div class="service-actions">
                                <div class="delete-btn1" data-id="${service.id}">
                                    <i class="fas fa-trash"></i>
                                </div>
                            </div>
                        </div>
                    `;
                    container.append(html);
                });
            } else {
                Swal.fire("Error", response.message || "Could not load services", "error");
            }
        },
        error: function () {
            Swal.fire("Error", "Failed to fetch services", "error");
        }
    });
}

$(document).ready(function () {
    loadServicesList();
});

// ✅ Delete button click
$(document).on("click", ".delete-btn1", function () {
    const serviceId = $(this).data("id");

    Swal.fire({
        title: 'Delete Service?',
        text: 'This action cannot be undone!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/admin-panel/services/${serviceId}/delete/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function (response) {
                    if (response.status === "success") {
                        Swal.fire("Deleted!", response.message, "success");
                        loadServicesList();  // Refresh after deletion
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function () {
                    Swal.fire("Error", "Something went wrong.", "error");
                }
            });
        }
    });
});


$(document).ready(function() {
    $('#mapForm').on('submit', function(e) {
        e.preventDefault();

        var embedCode = $('#embed_code').val();
        var csrfToken = $('[name=csrfmiddlewaretoken]').val();
        var postUrl = $('#mapForm').data('url'); // ✅ Get from HTML

        $.ajax({
            url: postUrl,
            type: "POST",
            data: {
                embed_code: embedCode,
                csrfmiddlewaretoken: csrfToken
            },
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Saved!',
                        text: 'Map embed code was saved successfully!',
                        confirmButtonColor: '#3085d6'
                    }).then(() => location.reload());
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: response.message || 'Something went wrong while saving the map code.',
                        confirmButtonColor: '#d33'
                    });
                }
            },
            error: function(xhr, status, error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops!',
                    text: 'An error occurred while processing your request.',
                    confirmButtonColor: '#d33'
                });
            }
        });
    });
});

