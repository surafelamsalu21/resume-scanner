// Resume Processing Interface
class ResumeProcessor {
	constructor() {
		this.initializeElements();
		this.attachEventListeners();
		this.loadJobPositions();
	}

	// Initialize DOM elements
	initializeElements() {
		this.elements = {
			dropZone: document.getElementById("dropZone"),
			resumeInput: document.getElementById("resumeInput"),
			jobSelect: document.getElementById("jobSelect"),
			analyzeBtn: document.getElementById("analyzeBtn"),
			resultsSection: document.getElementById("resultsSection"),
			loadingSpinner: document.querySelector(".loading-spinner"),
		};

		this.scoreElements = {
			overall: document.getElementById("overallScore"),
			technical: document.getElementById("technicalScore"),
			experience: document.getElementById("experienceScore"),
			education: document.getElementById("educationScore"),
			softSkills: document.getElementById("softSkillsScore"),
		};

		this.detailElements = {
			technical: document.getElementById("technicalDetails"),
			experience: document.getElementById("experienceDetails"),
			education: document.getElementById("educationDetails"),
			softSkills: document.getElementById("softSkillsDetails"),
			recommendations: document.getElementById("recommendationsList"),
		};
	}

	// Attach event listeners
	attachEventListeners() {
		// File upload handling
		this.elements.dropZone.addEventListener("click", (e) => {
			e.preventDefault();
			e.stopPropagation();
			if (e.target.tagName.toLowerCase() !== "input") {
				this.elements.resumeInput.click();
			}
		});

		this.elements.resumeInput.addEventListener("click", (e) => {
			e.stopPropagation();
		});

		this.elements.dropZone.addEventListener("dragover", (e) =>
			this.handleDragOver(e)
		);
		this.elements.dropZone.addEventListener("dragleave", () =>
			this.handleDragLeave()
		);
		this.elements.dropZone.addEventListener("drop", (e) =>
			this.handleDrop(e)
		);
		this.elements.resumeInput.addEventListener("change", (e) =>
			this.handleFileSelect(e)
		);

		// Job selection handling
		this.elements.jobSelect.addEventListener("change", () =>
			this.updateAnalyzeButton()
		);

		// Analysis button handling
		this.elements.analyzeBtn.addEventListener("click", () =>
			this.analyzeResume()
		);
	}

	// Load job positions from API
	async loadJobPositions() {
		try {
			const response = await fetch("/api/jobs");
			if (!response.ok)
				throw new Error("Failed to load job positions");

			const jobs = await response.json();
			this.updateJobSelect(jobs);
		} catch (error) {
			this.showError("Error loading job positions");
			console.error("Job loading error:", error);
		}
	}

	// Update job select dropdown
	updateJobSelect(jobs) {
		this.elements.jobSelect.innerHTML =
			'<option value="">Select a job position...</option>';
		jobs.forEach((job) => {
			const option = document.createElement("option");
			option.value = job.id;
			option.textContent = job.title;
			this.elements.jobSelect.appendChild(option);
		});
	}

	// File handling methods
	handleDragOver(e) {
		e.preventDefault();
		this.elements.dropZone.classList.add("dragover");
	}

	handleDragLeave() {
		this.elements.dropZone.classList.remove("dragover");
	}

	handleDrop(e) {
		e.preventDefault();
		this.elements.dropZone.classList.remove("dragover");
		const file = e.dataTransfer.files[0];
		this.validateAndProcessFile(file);
	}

	handleFileSelect(e) {
		const file = e.target.files[0];
		this.validateAndProcessFile(file);
	}

	validateAndProcessFile(file) {
		const validTypes = [
			"application/pdf",
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		];

		if (!file) return;

		if (!validTypes.includes(file.type)) {
			this.showError("Please upload a PDF or DOCX file");
			return;
		}

		if (file.size > 10 * 1024 * 1024) {
			// 10MB limit
			this.showError("File size should be less than 10MB");
			return;
		}

		this.updateDropZoneText(file.name);
		this.updateAnalyzeButton();
	}

	// UI update methods
	updateDropZoneText(fileName) {
		const fileNameElement = this.elements.dropZone.querySelector("p");
		fileNameElement.textContent = fileName;
		fileNameElement.classList.add("file-name");
	}

	updateAnalyzeButton() {
		this.elements.analyzeBtn.disabled =
			!this.elements.resumeInput.files[0] ||
			!this.elements.jobSelect.value;
	}

	// Resume analysis
	async analyzeResume() {
		const file = this.elements.resumeInput.files[0];
		const jobId = this.elements.jobSelect.value;

		if (!file || !jobId) return;

		const formData = new FormData();
		formData.append("resume", file);
		formData.append("job_id", jobId);

		this.setLoadingState(true);

		try {
			const response = await fetch("/api/analyze", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) throw new Error("Analysis failed");

			const result = await response.json();
			this.displayResults(result);
		} catch (error) {
			this.showError("An error occurred during analysis");
			console.error("Analysis error:", error);
		} finally {
			this.setLoadingState(false);
		}
	}

	// Results display
	displayResults(result) {
		this.elements.resultsSection.style.display = "block";

		// Update scores
		this.updateScores(result);

		// Update details
		this.updateDetails(result);

		// Update recommendations
		this.updateRecommendations(result.recommendations);

		// Smooth scroll to results
		this.elements.resultsSection.scrollIntoView({ behavior: "smooth" });
	}

	updateScores(result) {
		this.scoreElements.overall.textContent = `${result.overall_score}%`;
		this.updateScore("technical", result.technical_score);
		this.updateScore("experience", result.experience_score);
		this.updateScore("education", result.education_score);
		this.updateScore("softSkills", result.soft_skills_score);
	}

	updateScore(type, score) {
		const element = this.scoreElements[type];
		if (element) {
			element.style.width = `${score}%`;
			element.textContent = `${score}%`;

			// Update color based on score
			element.className = "progress-bar " + this.getScoreClass(score);
		}
	}

	updateDetails(result) {
		Object.keys(this.detailElements).forEach((key) => {
			if (key !== "recommendations") {
				const details = result[`${key}_details`];
				if (details) {
					this.detailElements[key].innerHTML =
						this.formatDetails(details);
				}
			}
		});
	}

	updateRecommendations(recommendations) {
		if (!recommendations || !recommendations.length) {
			this.detailElements.recommendations.innerHTML =
				'<li class="list-group-item">No specific recommendations available.</li>';
			return;
		}

		this.detailElements.recommendations.innerHTML = recommendations
			.map((rec) => `<li class="list-group-item">${rec}</li>`)
			.join("");
	}

	// Utility methods
	formatDetails(details) {
		if (typeof details === "string") return details;
		if (Array.isArray(details)) return details.join("<br>");
		return Object.entries(details)
			.map(([key, value]) => `<strong>${key}:</strong> ${value}`)
			.join("<br>");
	}

	getScoreClass(score) {
		if (score >= 80) return "bg-success";
		if (score >= 60) return "bg-info";
		if (score >= 40) return "bg-warning";
		return "bg-danger";
	}

	setLoadingState(isLoading) {
		this.elements.analyzeBtn.disabled = isLoading;
		this.elements.loadingSpinner.style.display = isLoading
			? "inline-block"
			: "none";
	}

	showError(message) {
		// You can enhance this with a proper toast/notification system
		alert(message);
	}
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
	window.resumeProcessor = new ResumeProcessor();
});
