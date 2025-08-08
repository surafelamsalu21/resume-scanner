/**
 * Admin Panel JavaScript
 * Handles dynamic updates for job categories and prompts
 */

document.addEventListener("DOMContentLoaded", function () {
	// Initialize components
	initJobCategoryManagement();
	initPromptManagement();
	initCVManagement();
	loadDashboardStats();

	// Setup real-time updates if WebSocket is available
	setupRealTimeUpdates();
});

/**
 * Load dashboard statistics
 */
function loadDashboardStats() {
	// Check if we're on the dashboard page
	const totalResumesElement = document.getElementById("total-resumes");
	const totalCategoriesElement = document.getElementById("total-categories");
	const totalPromptsElement = document.getElementById("total-prompts");
	const totalUsersElement = document.getElementById("total-users");

	if (
		totalResumesElement ||
		totalCategoriesElement ||
		totalPromptsElement ||
		totalUsersElement
	) {
		fetch("/admin/api/dashboard/stats")
			.then((response) => response.json())
			.then((stats) => {
				if (totalResumesElement) {
					totalResumesElement.textContent =
						stats.processed_resume_count;
				}
				if (totalCategoriesElement) {
					totalCategoriesElement.textContent =
						stats.job_category_count;
				}
				if (totalPromptsElement) {
					totalPromptsElement.textContent =
						stats.ai_prompt_count;
				}
				if (totalUsersElement) {
					totalUsersElement.textContent = stats.admin_count;
				}
			})
			.catch((error) => {
				console.error("Error loading dashboard stats:", error);
			});
	}
}

/**
 * Job Category Management
 */
function initJobCategoryManagement() {
	const categoryForm = document.getElementById("category-form");
	const categoryList = document.getElementById("category-list");
	const categoryDropdowns = document.querySelectorAll(
		".job-category-dropdown"
	);

	// Load categories on page load
	loadJobCategories();

	// Handle category form submission
	if (categoryForm) {
		categoryForm.addEventListener("submit", function (e) {
			e.preventDefault();
			const formData = new FormData(categoryForm);
			const categoryData = {
				name: formData.get("name"),
				description: formData.get("description"),
			};

			// Add or update category
			const categoryId = formData.get("category_id");
			if (categoryId) {
				updateJobCategory(categoryId, categoryData);
			} else {
				addJobCategory(categoryData);
			}
		});
	}

	// Handle category deletion
	if (categoryList) {
		categoryList.addEventListener("click", function (e) {
			if (e.target.classList.contains("delete-category")) {
				const categoryId = e.target.dataset.id;
				if (
					confirm(
						"Are you sure you want to delete this category?"
					)
				) {
					deleteJobCategory(categoryId);
				}
			}

			if (e.target.classList.contains("edit-category")) {
				const categoryId = e.target.dataset.id;
				editJobCategory(categoryId);
			}
		});
	}
}

/**
 * Load job categories from the server
 */
function loadJobCategories() {
	fetch("/admin/api/job-categories")
		.then((response) => response.json())
		.then((categories) => {
			updateCategoryList(categories);
			updateCategoryDropdowns(categories);
		})
		.catch((error) => {
			console.error("Error loading job categories:", error);
			showNotification("Error loading job categories", "error");
		});
}

/**
 * Add a new job category
 */
function addJobCategory(categoryData) {
	fetch("/admin/api/job-categories", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(categoryData),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification("Category added successfully", "success");
				document.getElementById("category-form").reset();
				loadJobCategories(); // Reload categories
			}
		})
		.catch((error) => {
			console.error("Error adding job category:", error);
			showNotification("Error adding job category", "error");
		});
}

/**
 * Update an existing job category
 */
function updateJobCategory(categoryId, categoryData) {
	fetch(`/admin/api/job-categories/${categoryId}`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(categoryData),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification(
					"Category updated successfully",
					"success"
				);
				document.getElementById("category-form").reset();
				document.getElementById("category-form").dataset.mode =
					"add";
				document.querySelector(
					'#category-form button[type="submit"]'
				).textContent = "Add Category";
				document.querySelector(
					'#category-form input[name="category_id"]'
				).value = "";
				loadJobCategories(); // Reload categories
			}
		})
		.catch((error) => {
			console.error("Error updating job category:", error);
			showNotification("Error updating job category", "error");
		});
}

/**
 * Delete a job category
 */
function deleteJobCategory(categoryId) {
	fetch(`/admin/api/job-categories/${categoryId}`, {
		method: "DELETE",
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification(
					"Category deleted successfully",
					"success"
				);
				loadJobCategories(); // Reload categories
			}
		})
		.catch((error) => {
			console.error("Error deleting job category:", error);
			showNotification("Error deleting job category", "error");
		});
}

/**
 * Edit a job category (populate form)
 */
function editJobCategory(categoryId) {
	fetch(`/admin/api/job-categories/${categoryId}`)
		.then((response) => response.json())
		.then((category) => {
			const form = document.getElementById("category-form");
			form.querySelector('input[name="name"]').value = category.name;
			form.querySelector('textarea[name="description"]').value =
				category.description;
			form.querySelector('input[name="category_id"]').value =
				category.id;
			form.dataset.mode = "edit";
			form.querySelector('button[type="submit"]').textContent =
				"Update Category";

			// Scroll to form
			form.scrollIntoView({ behavior: "smooth" });
		})
		.catch((error) => {
			console.error("Error loading category details:", error);
			showNotification("Error loading category details", "error");
		});
}

/**
 * Update category list in the UI
 */
function updateCategoryList(categories) {
	const categoryList = document.getElementById("category-list");
	if (!categoryList) return;

	categoryList.innerHTML = "";

	if (categories.length === 0) {
		categoryList.innerHTML =
			'<tr><td colspan="5" class="text-center">No categories found</td></tr>';
		return;
	}

	categories.forEach((category) => {
		const row = document.createElement("tr");
		row.innerHTML = `
            <td>${category.id}</td>
            <td>${category.name}</td>
            <td>${category.description || "-"}</td>
            <td>
                <span class="badge ${
					category.is_active ? "badge-success" : "badge-danger"
				}">
                    ${category.is_active ? "Active" : "Inactive"}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary edit-category" data-id="${
					category.id
				}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-category" data-id="${
					category.id
				}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
		categoryList.appendChild(row);
	});
}

/**
 * Update all category dropdowns in the UI
 */
function updateCategoryDropdowns(categories) {
	const dropdowns = document.querySelectorAll(".job-category-dropdown");

	dropdowns.forEach((dropdown) => {
		const currentValue = dropdown.value;
		dropdown.innerHTML = '<option value="">Select Category</option>';

		categories.forEach((category) => {
			if (category.is_active) {
				const option = document.createElement("option");
				option.value = category.id;
				option.textContent = category.name;
				dropdown.appendChild(option);
			}
		});

		// Restore selected value if it still exists
		if (currentValue) {
			dropdown.value = currentValue;
		}
	});
}

/**
 * Prompt Management
 */
function initPromptManagement() {
	const promptForm = document.getElementById("prompt-form");
	const promptList = document.getElementById("prompt-list");

	// Load prompts on page load
	loadPrompts();

	// Handle prompt form submission
	if (promptForm) {
		promptForm.addEventListener("submit", function (e) {
			e.preventDefault();
			const formData = new FormData(promptForm);
			const promptData = {
				name: formData.get("name"),
				description: formData.get("description"),
				prompt_template: formData.get("prompt_template"),
				job_type: formData.get("job_type"),
				version: formData.get("version"),
				job_category_id: formData.get("job_category_id"),
			};

			// Add or update prompt
			const promptId = formData.get("prompt_id");
			if (promptId) {
				updatePrompt(promptId, promptData);
			} else {
				addPrompt(promptData);
			}
		});
	}

	// Handle prompt deletion
	if (promptList) {
		promptList.addEventListener("click", function (e) {
			if (e.target.classList.contains("delete-prompt")) {
				const promptId = e.target.dataset.id;
				if (
					confirm("Are you sure you want to delete this prompt?")
				) {
					deletePrompt(promptId);
				}
			}

			if (e.target.classList.contains("edit-prompt")) {
				const promptId = e.target.dataset.id;
				editPrompt(promptId);
			}
		});
	}
}

/**
 * Load prompts from the server
 */
function loadPrompts() {
	fetch("/admin/api/prompts")
		.then((response) => response.json())
		.then((prompts) => {
			updatePromptList(prompts);
		})
		.catch((error) => {
			console.error("Error loading prompts:", error);
			showNotification("Error loading prompts", "error");
		});
}

/**
 * Add a new prompt
 */
function addPrompt(promptData) {
	fetch("/admin/api/prompts", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(promptData),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification("Prompt added successfully", "success");
				document.getElementById("prompt-form").reset();
				loadPrompts(); // Reload prompts
			}
		})
		.catch((error) => {
			console.error("Error adding prompt:", error);
			showNotification("Error adding prompt", "error");
		});
}

/**
 * Update an existing prompt
 */
function updatePrompt(promptId, promptData) {
	fetch(`/admin/api/prompts/${promptId}`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(promptData),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification("Prompt updated successfully", "success");
				document.getElementById("prompt-form").reset();
				document.getElementById("prompt-form").dataset.mode = "add";
				document.querySelector(
					'#prompt-form button[type="submit"]'
				).textContent = "Add Prompt";
				document.querySelector(
					'#prompt-form input[name="prompt_id"]'
				).value = "";
				loadPrompts(); // Reload prompts
			}
		})
		.catch((error) => {
			console.error("Error updating prompt:", error);
			showNotification("Error updating prompt", "error");
		});
}

/**
 * Delete a prompt
 */
function deletePrompt(promptId) {
	fetch(`/admin/api/prompts/${promptId}`, {
		method: "DELETE",
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification("Prompt deleted successfully", "success");
				loadPrompts(); // Reload prompts
			}
		})
		.catch((error) => {
			console.error("Error deleting prompt:", error);
			showNotification("Error deleting prompt", "error");
		});
}

/**
 * Edit a prompt (populate form)
 */
function editPrompt(promptId) {
	fetch(`/admin/api/prompts/${promptId}`)
		.then((response) => response.json())
		.then((prompt) => {
			const form = document.getElementById("prompt-form");
			form.querySelector('input[name="name"]').value = prompt.name;
			form.querySelector('textarea[name="description"]').value =
				prompt.description;
			form.querySelector('textarea[name="prompt_template"]').value =
				prompt.prompt_template;
			form.querySelector('input[name="job_type"]').value =
				prompt.job_type;
			form.querySelector('input[name="version"]').value =
				prompt.version;
			form.querySelector('select[name="job_category_id"]').value =
				prompt.job_category_id;
			form.querySelector('input[name="prompt_id"]').value = prompt.id;
			form.dataset.mode = "edit";
			form.querySelector('button[type="submit"]').textContent =
				"Update Prompt";

			// Scroll to form
			form.scrollIntoView({ behavior: "smooth" });
		})
		.catch((error) => {
			console.error("Error loading prompt details:", error);
			showNotification("Error loading prompt details", "error");
		});
}

/**
 * Update prompt list in the UI
 */
function updatePromptList(prompts) {
	const promptList = document.getElementById("prompt-list");
	if (!promptList) return;

	promptList.innerHTML = "";

	if (prompts.length === 0) {
		promptList.innerHTML =
			'<tr><td colspan="6" class="text-center">No prompts found</td></tr>';
		return;
	}

	prompts.forEach((prompt) => {
		const row = document.createElement("tr");
		row.innerHTML = `
            <td>${prompt.id}</td>
            <td>${prompt.name}</td>
            <td>${prompt.job_type}</td>
            <td>${prompt.version}</td>
            <td>
                <span class="badge ${
					prompt.is_active ? "badge-success" : "badge-danger"
				}">
                    ${prompt.is_active ? "Active" : "Inactive"}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary edit-prompt" data-id="${
					prompt.id
				}">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-prompt" data-id="${
					prompt.id
				}">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
		promptList.appendChild(row);
	});
}

/**
 * CV Management
 */
function initCVManagement() {
	const cvList = document.getElementById("cv-list");
	const filterForm = document.getElementById("cv-filter-form");

	// Load CVs on page load
	loadCVs();

	// Handle filter form submission
	if (filterForm) {
		filterForm.addEventListener("submit", function (e) {
			e.preventDefault();
			const formData = new FormData(filterForm);
			const filters = {
				job_category: formData.get("job_category"),
				status: formData.get("status"),
			};

			loadCVs(filters);
		});
	}

	// Handle CV actions
	if (cvList) {
		cvList.addEventListener("click", function (e) {
			// Handle view CV
			if (e.target.classList.contains("view-cv")) {
				const resumeId = e.target.dataset.id;
				viewCV(resumeId);
			}

			// Handle approve CV
			if (e.target.classList.contains("approve-cv")) {
				const resumeId = e.target.dataset.id;
				updateCVStatus(resumeId, "approved");
			}

			// Handle reject CV
			if (e.target.classList.contains("reject-cv")) {
				const resumeId = e.target.dataset.id;
				updateCVStatus(resumeId, "rejected");
			}

			// Handle feedback
			if (e.target.classList.contains("add-feedback")) {
				const resumeId = e.target.dataset.id;
				showFeedbackModal(resumeId);
			}
		});
	}
}

/**
 * Load CVs from the server
 */
function loadCVs(filters = {}) {
	let url = "/admin/api/resumes";

	// Add filters if provided
	if (filters.job_category || filters.status) {
		const params = new URLSearchParams();
		if (filters.job_category)
			params.append("job_category", filters.job_category);
		if (filters.status) params.append("status", filters.status);
		url += "?" + params.toString();
	}

	fetch(url)
		.then((response) => response.json())
		.then((resumes) => {
			updateCVList(resumes);
		})
		.catch((error) => {
			console.error("Error loading CVs:", error);
			showNotification("Error loading CVs", "error");
		});
}

/**
 * Update CV list in the UI
 */
function updateCVList(resumes) {
	const cvList = document.getElementById("cv-list");
	if (!cvList) return;

	cvList.innerHTML = "";

	if (resumes.length === 0) {
		cvList.innerHTML =
			'<tr><td colspan="7" class="text-center">No CVs found</td></tr>';
		return;
	}

	resumes.forEach((resume) => {
		const row = document.createElement("tr");
		row.innerHTML = `
            <td>${resume.id}</td>
            <td>${resume.candidate_name || "Unknown"}</td>
            <td>${resume.job_role}</td>
            <td>${new Date(resume.upload_date).toLocaleDateString()}</td>
            <td>
                <span class="badge badge-${getStatusBadgeClass(resume.status)}">
                    ${resume.status}
                </span>
            </td>
            <td>${
				resume.ranking_score
					? resume.ranking_score.toFixed(1) + "%"
					: "N/A"
			}</td>
            <td>
                <button class="btn btn-sm btn-info view-cv" data-id="${
					resume.id
				}">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-success approve-cv" data-id="${
					resume.id
				}" ${resume.status === "approved" ? "disabled" : ""}>
                    <i class="fas fa-check"></i>
                </button>
                <button class="btn btn-sm btn-danger reject-cv" data-id="${
					resume.id
				}" ${resume.status === "rejected" ? "disabled" : ""}>
                    <i class="fas fa-times"></i>
                </button>
                <button class="btn btn-sm btn-secondary add-feedback" data-id="${
					resume.id
				}">
                    <i class="fas fa-comment"></i>
                </button>
            </td>
        `;
		cvList.appendChild(row);
	});
}

/**
 * Get badge class based on CV status
 */
function getStatusBadgeClass(status) {
	switch (status) {
		case "pending":
			return "warning";
		case "processing":
			return "info";
		case "processed":
			return "primary";
		case "approved":
			return "success";
		case "rejected":
			return "danger";
		case "shortlisted":
			return "info";
		default:
			return "secondary";
	}
}

/**
 * View CV details
 */
function viewCV(resumeId) {
	window.open(`/admin/resumes/${resumeId}`, "_blank");
}

/**
 * Update CV status
 */
function updateCVStatus(resumeId, status) {
	fetch(`/admin/api/resumes/${resumeId}/status`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ status }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification(`CV ${status} successfully`, "success");
				loadCVs(); // Reload CVs
			}
		})
		.catch((error) => {
			console.error("Error updating CV status:", error);
			showNotification("Error updating CV status", "error");
		});
}

/**
 * Show feedback modal
 */
function showFeedbackModal(resumeId) {
	// Get current feedback if any
	fetch(`/admin/api/resumes/${resumeId}`)
		.then((response) => response.json())
		.then((resume) => {
			// Create modal
			const modal = document.createElement("div");
			modal.className = "modal fade";
			modal.id = "feedbackModal";
			modal.setAttribute("tabindex", "-1");
			modal.setAttribute("role", "dialog");
			modal.setAttribute("aria-labelledby", "feedbackModalLabel");
			modal.setAttribute("aria-hidden", "true");

			modal.innerHTML = `
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="feedbackModalLabel">Add Feedback</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <form id="feedback-form">
                                <input type="hidden" name="resume_id" value="${resumeId}">
                                <div class="form-group">
                                    <label for="feedback">Feedback</label>
                                    <textarea class="form-control" id="feedback" name="feedback" rows="5">${
									resume.admin_feedback || ""
								}</textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" id="save-feedback">Save Feedback</button>
                        </div>
                    </div>
                </div>
            `;

			document.body.appendChild(modal);

			// Show modal
			$("#feedbackModal").modal("show");

			// Handle save feedback
			document
				.getElementById("save-feedback")
				.addEventListener("click", function () {
					const feedback =
						document.getElementById("feedback").value;
					saveFeedback(resumeId, feedback);
				});

			// Remove modal when hidden
			$("#feedbackModal").on("hidden.bs.modal", function () {
				document.body.removeChild(modal);
			});
		})
		.catch((error) => {
			console.error("Error loading resume details:", error);
			showNotification("Error loading resume details", "error");
		});
}

/**
 * Save feedback
 */
function saveFeedback(resumeId, feedback) {
	fetch(`/admin/api/resumes/${resumeId}/feedback`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ feedback }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				showNotification(data.error, "error");
			} else {
				showNotification("Feedback saved successfully", "success");
				$("#feedbackModal").modal("hide");
				loadCVs(); // Reload CVs
			}
		})
		.catch((error) => {
			console.error("Error saving feedback:", error);
			showNotification("Error saving feedback", "error");
		});
}

/**
 * Real-time updates using WebSocket
 */
function setupRealTimeUpdates() {
	// Check if WebSocket is supported
	if (typeof WebSocket === "undefined") {
		console.log("WebSocket not supported");
		return;
	}

	// Connect to WebSocket server
	const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
	const wsUrl = `${protocol}//${window.location.host}/ws/admin`;

	try {
		const socket = new WebSocket(wsUrl);

		socket.onopen = function () {
			console.log("WebSocket connection established");
		};

		socket.onmessage = function (event) {
			const data = JSON.parse(event.data);

			// Handle different types of updates
			switch (data.type) {
				case "job_category_update":
					loadJobCategories();
					break;
				case "prompt_update":
					loadPrompts();
					break;
				case "resume_update":
					loadCVs();
					break;
				case "notification":
					showNotification(data.message, data.level || "info");
					break;
			}
		};

		socket.onerror = function (error) {
			console.error("WebSocket error:", error);
		};

		socket.onclose = function () {
			console.log("WebSocket connection closed");
			// Try to reconnect after 5 seconds
			setTimeout(setupRealTimeUpdates, 5000);
		};
	} catch (error) {
		console.error("Error setting up WebSocket:", error);
	}
}

/**
 * Show notification
 */
function showNotification(message, type = "info") {
	// Check if toastr is available
	if (typeof toastr !== "undefined") {
		toastr[type](message);
		return;
	}

	// Fallback to alert
	alert(message);
}
